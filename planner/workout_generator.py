"""
Turn a ProgramStructure + selected exercises into concrete Program /
WorkoutDay / Workout database rows (Section 10 + 16).
"""
from django.db import transaction

from programs.models import Program, WorkoutDay, Workout
from . import exercise_selector as selector

# Volume/intensity presets by phase. Kept intentionally modest — the
# engine should prescribe the most *sustainable* plan, not the hardest.
PHASE_PRESETS = {
    'phase1': {'sets': 2, 'reps': '8-12', 'rest': 60, 'intensity': 'RPE 4-5 (easy, focus on form)'},
    'phase2': {'sets': 3, 'reps': '10-12', 'rest': 60, 'intensity': 'RPE 5-6 (moderate effort)'},
    'phase3': {'sets': 3, 'reps': '8-12', 'rest': 75, 'intensity': 'RPE 6-7 (challenging, 2-3 reps in reserve)'},
    'phase4': {'sets': 4, 'reps': '6-12', 'rest': 90, 'intensity': 'RPE 7-8 (1-2 reps in reserve)'},
}

GOAL_REP_ADJUST = {
    'strength': '4-6',
    'muscle_gain': '8-12',
    'endurance': '15-20',
    'fat_loss': '10-15',
}

GOAL_SET_ADJUST = {
    'strength': 1,
    'muscle_gain': 0,
    'endurance': -1,
    'fat_loss': 0,
}


def _phase_label(phase):
    return dict(Program.PHASE_CHOICES).get(phase, phase)


def _preset_for(assessment):
    preset = dict(PHASE_PRESETS.get(assessment.training_phase, PHASE_PRESETS['phase1']))
    set_adjust = GOAL_SET_ADJUST.get(assessment.primary_goal, 0)
    preset['sets'] = max(2, min(5, preset['sets'] + set_adjust))
    reps_override = GOAL_REP_ADJUST.get(assessment.primary_goal)
    if reps_override and assessment.training_phase != 'phase1':
        preset['reps'] = reps_override
    return preset


@transaction.atomic
def generate_program(user, assessment, structure):
    """Create a new active Program with its WorkoutDay/Workout rows."""

    Program.objects.filter(user=user, is_active=True).update(is_active=False)

    program = Program.objects.create(
        user=user,
        assessment=assessment,
        name=f"{_phase_label(structure.phase)} — {structure.days_per_week_trained} days/week",
        goal=assessment.primary_goal,
        phase=structure.phase,
        difficulty=assessment.experience_level,
        days_per_week=structure.days_per_week_trained,
        duration_weeks=4,
        is_active=True,
        week_number=1,
    )

    preset = _preset_for(assessment)
    session_minutes = structure.session_minutes

    for day_plan in structure.day_plans:
        day = WorkoutDay.objects.create(
            program=program,
            day_index=day_plan.day_index,
            label=day_plan.label,
            day_type=day_plan.day_type,
        )

        if day_plan.day_type == 'rest':
            continue

        order = 0
        rotation_seed = program.pk + day_plan.day_index

        if day_plan.day_type == 'active_recovery':
            for ex in selector.select_cardio(assessment, count=1, rotation_seed=rotation_seed):
                Workout.objects.create(
                    day=day, exercise=ex, section='cardio', order=order,
                    sets=1, duration_seconds=min(1800, session_minutes * 60),
                    rest_seconds=0, intensity_target='Easy, conversational pace',
                )
                order += 1
            continue

        # --- Training day ---
        for ex in selector.select_warmup(assessment, count=1, rotation_seed=rotation_seed):
            Workout.objects.create(
                day=day, exercise=ex, section='warmup', order=order,
                sets=1, duration_seconds=300, rest_seconds=0,
                intensity_target='Easy — just raise heart rate and mobilize joints',
            )
            order += 1

        max_exercises = max(3, min(6, session_minutes // 6))
        main_exercises = selector.select_exercises_for_focus(
            assessment,
            day_plan.focus,
            rotation_seed=rotation_seed,
            max_exercises=max_exercises,
        )
        # Roughly budget: allow more exercises for longer sessions.

        for i, ex in enumerate(main_exercises):
            section = 'main' if i < 2 else 'accessory'
            sets = preset['sets']
            reps = preset['reps'] if not ex.default_duration_seconds else ''
            duration = ex.default_duration_seconds
            Workout.objects.create(
                day=day, exercise=ex, section=section, order=order,
                sets=sets, reps=reps, duration_seconds=duration,
                rest_seconds=preset['rest'], intensity_target=preset['intensity'],
            )
            order += 1

        # Cardio finisher if the goal or phase calls for it and there's time.
        if assessment.primary_goal in ('fat_loss', 'endurance', 'general_fitness') and session_minutes >= 30:
            for ex in selector.select_cardio(assessment, count=1, rotation_seed=rotation_seed):
                Workout.objects.create(
                    day=day, exercise=ex, section='cardio', order=order,
                    sets=1, duration_seconds=600, rest_seconds=0,
                    intensity_target='Moderate — able to hold a conversation',
                )
                order += 1

        for ex in selector.select_cooldown(assessment, count=1, rotation_seed=rotation_seed):
            Workout.objects.create(
                day=day, exercise=ex, section='cooldown', order=order,
                sets=1, duration_seconds=300, rest_seconds=0,
                intensity_target='Gentle stretching',
            )
            order += 1

    return program
