"""
Determine the appropriate starting training phase (Section 7).

The phase decision leans conservative: when signals disagree, the engine
prefers the lower (safer) phase. Progression later moves users up — see
planner/progression.py — but the *starting* point should never overshoot
what the person can currently sustain.
"""

PHASE_1 = 'phase1'  # Habit & Tolerance
PHASE_2 = 'phase2'  # Foundation
PHASE_3 = 'phase3'  # Development
PHASE_4 = 'phase4'  # Specialized

PHASE_LABELS = {
    PHASE_1: 'Phase 1 — Habit & Tolerance',
    PHASE_2: 'Phase 2 — Foundation',
    PHASE_3: 'Phase 3 — Development',
    PHASE_4: 'Phase 4 — Specialized',
}


def select_training_phase(assessment) -> str:
    experience = assessment.experience_level or 'beginner'
    cardio = assessment.cardio_capacity or 0
    strength = assessment.strength_capacity or 0
    work_capacity = assessment.work_capacity or 0
    sedentary_hours = assessment.sedentary_hours_per_day or 0
    activity_level = assessment.daily_activity_level or 'low'

    very_deconditioned = work_capacity < 25 or (cardio < 20 and strength < 20)
    highly_sedentary = sedentary_hours >= 10 or activity_level == 'very_low'

    # Hard-coded conservative ladder.
    if experience == 'deconditioned_beginner' or (very_deconditioned and highly_sedentary):
        return PHASE_1

    if experience == 'beginner':
        if very_deconditioned:
            return PHASE_1
        return PHASE_2

    if experience == 'intermediate':
        if very_deconditioned:
            return PHASE_1
        if work_capacity < 45:
            return PHASE_2
        return PHASE_3

    if experience == 'advanced':
        if very_deconditioned:
            # A long layoff can make even an "advanced" trainee currently
            # deconditioned — never assume experience overrides today's
            # measured capacity.
            return PHASE_1
        if work_capacity < 45:
            return PHASE_2
        if work_capacity < 70:
            return PHASE_3
        return PHASE_4

    return PHASE_1
