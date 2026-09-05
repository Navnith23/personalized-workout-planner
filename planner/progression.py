"""
Weekly adaptive progression (Section 13 + 15).

Given a CheckIn, decide how the *next* program week should change:
increase challenge, hold steady, reduce workload, or simplify the plan.
Never punishes missed sessions by adding workload.
"""
from dataclasses import dataclass

INCREASE = 'increase'
HOLD = 'hold'
REDUCE = 'reduce'
SIMPLIFY = 'simplify'
STOP_AND_REFER = 'stop_and_refer'


@dataclass
class ProgressionDecision:
    action: str
    notes: str


def decide_progression(checkin) -> ProgressionDecision:
    if checkin.pain_flag:
        return ProgressionDecision(
            action=STOP_AND_REFER,
            notes=(
                "You flagged pain or discomfort. We've paused progression on the "
                "affected movements. If pain persists or is sharp/sudden, please "
                "check in with a qualified professional before continuing."
            ),
        )

    completion_rate = checkin.completion_rate  # 0-100

    if completion_rate < 50:
        return ProgressionDecision(
            action=SIMPLIFY,
            notes=(
                "Adherence was low this week. Rather than adding more, we're "
                "simplifying the plan — fewer exercises and/or a lighter schedule "
                "— so it's easier to stay consistent."
            ),
        )

    if checkin.recovery <= 3:
        return ProgressionDecision(
            action=REDUCE,
            notes="Recovery was reported as poor. We're reducing workload this week and prioritizing rest.",
        )

    if checkin.difficulty >= 8:
        return ProgressionDecision(
            action=REDUCE if checkin.difficulty >= 9 else HOLD,
            notes="Sessions felt very difficult. We're holding — or slightly reducing — the workload rather than increasing it.",
        )

    if checkin.sessions_too_long:
        return ProgressionDecision(
            action=SIMPLIFY,
            notes="Sessions have been running long. We're trimming volume so each session fits your available time.",
        )

    if completion_rate >= 80 and 3 <= checkin.difficulty <= 6 and checkin.recovery >= 6:
        return ProgressionDecision(
            action=INCREASE,
            notes="Great adherence, manageable effort, and good recovery — increasing challenge slightly this week.",
        )

    if checkin.difficulty <= 2 and checkin.recovery >= 7 and completion_rate >= 80:
        return ProgressionDecision(
            action=INCREASE,
            notes="Sessions felt very easy with strong recovery — increasing reps/resistance/volume this week.",
        )

    return ProgressionDecision(
        action=HOLD,
        notes="Holding steady this week — current effort and recovery both look appropriate.",
    )


def apply_progression(program, decision: ProgressionDecision):
    """
    Adjust the *next* week's Workout rows for the active program based on
    the progression decision. Operates on Workout objects directly (simple,
    transparent rule application rather than regenerating from scratch).
    """
    from programs.models import Workout

    workouts = Workout.objects.filter(day__program=program, section__in=['main', 'accessory'])

    if decision.action == INCREASE:
        for w in workouts:
            if w.reps and '-' in w.reps:
                low, high = w.reps.split('-')
                try:
                    low, high = int(low), int(high)
                    w.reps = f"{low + 1}-{high + 1}"
                except ValueError:
                    pass
            elif w.duration_seconds:
                w.duration_seconds = int(w.duration_seconds * 1.1)
            w.save()

    elif decision.action == REDUCE:
        for w in workouts:
            if w.sets > 1:
                w.sets = max(1, w.sets - 1)
            w.rest_seconds = int(w.rest_seconds * 1.15)
            w.save()

    elif decision.action == SIMPLIFY:
        # Drop the lowest-priority accessory work, keep the main lifts.
        accessories = list(Workout.objects.filter(day__program=program, section='accessory'))
        for w in accessories[max(1, len(accessories) // 2):]:
            w.delete()

    elif decision.action == STOP_AND_REFER:
        # Leave the plan untouched but do not progress; the view layer
        # should surface the professional-evaluation messaging.
        pass

    program.week_number += 1
    program.save()

PHASE_ORDER = ['phase1', 'phase2', 'phase3', 'phase4']


def maybe_promote_phase(program, decision):
    """
    After apply_progression() runs, check whether it's time to graduate
    to the next phase: the program has completed its duration_weeks AND
    the most recent decision was INCREASE (real, no-friction progress).
    Returns True if a new program was generated (caller should re-fetch
    the user's active program).
    """
    if decision.action != INCREASE:
        return False
    if program.week_number < program.duration_weeks:
        return False

    current_index = PHASE_ORDER.index(program.phase)
    if current_index >= len(PHASE_ORDER) - 1:
        return False  # already at phase4, nothing higher to graduate to

    assessment = program.assessment
    if assessment is None:
        return False

    next_phase = PHASE_ORDER[current_index + 1]
    assessment.training_phase = next_phase
    assessment.save()

    from . import program_selector, workout_generator
    structure = program_selector.build_program_structure(assessment)
    workout_generator.generate_program(program.user, assessment, structure)
    return True
