"""
Management command: python manage.py test_plan_variety

Runs the verification checklist for the recent plan-generation fixes:
  1. Exercise rotation/variety across programs
  2. Movement-pattern coverage on full-body days
  3. Set-count variation by goal
  4. Experience/phase classification spread
  5. ML model wiring sanity check

Read-only — does not modify any data. Safe to run anytime, including in
production, though it does import ml_models.predictor which loads the
.pkl bundles from disk.

Place this file at: planner/management/commands/test_plan_variety.py
(create the `management/` and `commands/` directories with empty
__init__.py files if they don't already exist.)
"""
from collections import Counter, defaultdict

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Verify recent plan-generation fixes: exercise variety, pattern coverage, set/goal variation, phase spread, ML wiring."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=10,
            help="Max number of most recent programs to inspect (default 10).",
        )

    def handle(self, *args, **options):
        limit = options["limit"]

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 1. Exercise rotation/variety across programs ==="))
        self._check_exercise_variety(limit)

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 2. Movement-pattern coverage on full-body days ==="))
        self._check_pattern_coverage(limit)

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 3. Set-count variation by goal ==="))
        self._check_sets_by_goal(limit)

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 4. Experience/phase classification spread ==="))
        self._check_experience_spread()

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== 5. ML model wiring sanity check ==="))
        self._check_ml_wiring()

        self.stdout.write(self.style.SUCCESS("\nDone. Review any [WARN] lines above.\n"))

    # ------------------------------------------------------------------

    def _check_exercise_variety(self, limit):
        from programs.models import Program, Workout

        programs = Program.objects.order_by("-id")[:limit]
        seen_sets = []
        for p in programs:
            ids = list(
                Workout.objects.filter(day__program=p, section__in=["main", "accessory"])
                .values_list("exercise_id", flat=True)
            )
            id_set = tuple(sorted(set(ids)))
            seen_sets.append(id_set)
            self.stdout.write(
                f"  Program #{p.id} (user={p.user_id}, phase={p.phase}, goal={p.goal}): "
                f"{len(id_set)} distinct exercises -> {id_set}"
            )

        duplicate_count = Counter(seen_sets)
        repeats = {k: v for k, v in duplicate_count.items() if v > 1 and k}
        if repeats:
            self.stdout.write(self.style.WARNING(
                f"  [WARN] {len(repeats)} identical exercise-ID set(s) reused across multiple programs: {repeats}"
            ))
        else:
            self.stdout.write(self.style.SUCCESS("  [OK] No two inspected programs share an identical exercise set."))

    def _check_pattern_coverage(self, limit):
        from programs.models import Program, Workout, WorkoutDay

        full_body_days = WorkoutDay.objects.filter(
            program__in=Program.objects.order_by("-id")[:limit], focus="full_body"
        ) if hasattr(WorkoutDay, "focus") else WorkoutDay.objects.filter(
            program__in=Program.objects.order_by("-id")[:limit], label__icontains="Full Body"
        )

        pattern_counts = Counter()
        for day in full_body_days:
            patterns = Workout.objects.filter(
                day=day, section__in=["main", "accessory"]
            ).values_list("exercise__movement_pattern", flat=True)
            pattern_counts.update(patterns)

        expected = {"squat", "hinge", "push_horizontal", "pull_horizontal", "core"}
        seen = set(pattern_counts.keys())
        missing = expected - seen

        for pat in sorted(expected):
            self.stdout.write(f"  {pat}: seen {pattern_counts.get(pat, 0)} time(s)")

        if missing:
            self.stdout.write(self.style.WARNING(
                f"  [WARN] These full-body movement patterns never appeared across inspected days: {missing}"
            ))
        else:
            self.stdout.write(self.style.SUCCESS("  [OK] All expected full-body movement patterns appeared at least once."))

    def _check_sets_by_goal(self, limit):
        from programs.models import Program, Workout

        goal_sets = defaultdict(list)
        for p in Program.objects.order_by("-id")[:limit]:
            sets_vals = list(
                Workout.objects.filter(day__program=p, section__in=["main", "accessory"])
                .values_list("sets", flat=True)
            )
            if sets_vals:
                goal_sets[p.goal].append(round(sum(sets_vals) / len(sets_vals), 2))

        for goal, avgs in goal_sets.items():
            self.stdout.write(f"  goal={goal}: avg sets per program = {avgs}")

        distinct_goal_avgs = {goal: avgs for goal, avgs in goal_sets.items()}
        if len(distinct_goal_avgs) >= 2:
            all_avgs = [round(sum(v) / len(v), 2) for v in distinct_goal_avgs.values()]
            if len(set(all_avgs)) == 1:
                self.stdout.write(self.style.WARNING(
                    "  [WARN] All goals produced identical average set counts — GOAL_SET_ADJUST may not be applied."
                ))
            else:
                self.stdout.write(self.style.SUCCESS("  [OK] Set counts differ across goals."))
        else:
            self.stdout.write("  (Not enough distinct goals in recent programs to compare — generate test users with different goals.)")

    def _check_experience_spread(self):
        from assessment.models import Assessment

        rows = list(
            Assessment.objects.all().values(
                "id", "experience_level", "training_phase",
                "strength_capacity", "cardio_capacity", "work_capacity",
            )
        )
        for r in rows:
            self.stdout.write(f"  {r}")

        levels = Counter(r["experience_level"] for r in rows)
        self.stdout.write(f"  experience_level distribution: {dict(levels)}")

        if len(levels) <= 1 and len(rows) > 3:
            self.stdout.write(self.style.WARNING(
                "  [WARN] All assessments classify to the same experience_level despite multiple users — check scoring thresholds."
            ))
        else:
            self.stdout.write(self.style.SUCCESS("  [OK] experience_level shows some spread across users."))

        strength_vals = [r["strength_capacity"] for r in rows if r["strength_capacity"] is not None]
        if len(strength_vals) >= 3 and len(set(strength_vals)) == 1:
            self.stdout.write(self.style.WARNING(
                f"  [WARN] All users share an identical strength_capacity ({strength_vals[0]}) — scoring may still be collapsing distinct inputs."
            ))

    def _check_ml_wiring(self):
        import inspect

        try:
            from ml_models.predictor import ml_progression_hint
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  [WARN] Could not import ml_progression_hint: {e}"))
            return

        try:
            result = ml_progression_hint("beginner", 3, 24.5)
            self.stdout.write(f"  ml_progression_hint('beginner', 3, 24.5) -> {result!r}")
            self.stdout.write(self.style.SUCCESS("  [OK] ML predictor loads and runs without error."))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  [WARN] ml_progression_hint raised an error: {e}"))
            return

        # Check whether anything in planner/ actually references it — best-effort static check.
        try:
            import planner.recommendation as rec
            import planner.phase_selector as phase_sel
            import planner.progression as prog

            found_in = []
            for modname, mod in [("recommendation", rec), ("phase_selector", phase_sel), ("progression", prog)]:
                src = inspect.getsource(mod)
                if "ml_progression_hint" in src or "predict_experience_tier" in src:
                    found_in.append(modname)

            if found_in:
                self.stdout.write(self.style.SUCCESS(f"  [OK] ML hint referenced in: {found_in}"))
            else:
                self.stdout.write(self.style.WARNING(
                    "  [WARN] ML hint function is not referenced in recommendation.py, phase_selector.py, or progression.py — it may still be unwired."
                ))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  [WARN] Could not statically check ML wiring: {e}"))
