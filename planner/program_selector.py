"""
Decide the weekly training *structure*: how many training days, what type
of split, and how each day is labeled — before any specific exercises are
chosen. Section 11 (weekly plan) + Section 7 (phase focus).
"""
from dataclasses import dataclass, field


@dataclass
class DayPlan:
    day_index: int  # 0=Monday .. 6=Sunday
    label: str
    day_type: str  # 'training' | 'active_recovery' | 'rest'
    focus: str = ''  # 'full_body' | 'upper' | 'lower' | 'cardio' | 'mobility' etc.


@dataclass
class ProgramStructure:
    phase: str
    days_per_week_trained: int
    day_plans: list = field(default_factory=list)
    session_minutes: int = 30
    weekly_cardio_minutes_target: int = 60


def _cap_days_by_phase(phase, requested_days):
    """Never exceed what's safe for the phase, even if the user has more time available."""
    caps = {'phase1': 4, 'phase2': 5, 'phase3': 6, 'phase4': 6}
    return max(1, min(requested_days, caps.get(phase, 4)))


def _distribute_days(total_days_in_week, training_days):
    """
    Spread `training_days` training sessions evenly across a 7-day week,
    starting Monday, so rest days fall between sessions rather than
    clumping at the end.
    """
    if training_days <= 0:
        return []
    step = total_days_in_week / training_days
    indices = sorted({round(i * step) % total_days_in_week for i in range(training_days)})
    # Ensure we have exactly `training_days` unique slots
    i = 0
    while len(indices) < training_days:
        candidate = i % total_days_in_week
        if candidate not in indices:
            indices.append(candidate)
        i += 1
    return sorted(indices[:training_days])


def build_program_structure(assessment) -> ProgramStructure:
    phase = assessment.training_phase
    requested_days = assessment.days_per_week_available or 3
    minutes = assessment.minutes_per_session or 30
    goal = assessment.primary_goal or 'general_fitness'

    training_days = _cap_days_by_phase(phase, requested_days)
    training_slots = _distribute_days(7, training_days)

    day_plans = []
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Decide the split style based on phase + days/week.
    if phase == 'phase1':
        focuses = ['full_body'] * training_days
    elif phase == 'phase2':
        focuses = ['full_body'] * training_days
    elif phase == 'phase3':
        if training_days >= 4:
            pattern = ['upper', 'lower', 'full_body', 'upper', 'lower', 'full_body']
        else:
            pattern = ['full_body'] * training_days
        focuses = pattern[:training_days]
    else:  # phase4
        if training_days >= 5:
            pattern = ['push', 'pull', 'legs', 'push', 'pull', 'legs']
        elif training_days == 4:
            pattern = ['upper', 'lower', 'upper', 'lower']
        else:
            pattern = ['full_body'] * training_days
        focuses = pattern[:training_days]

    for i in range(7):
        if i in training_slots:
            idx = training_slots.index(i)
            focus = focuses[idx] if idx < len(focuses) else 'full_body'
            label = f"{day_names[i]} — {focus.replace('_', ' ').title()} Training"
            day_plans.append(DayPlan(day_index=i, label=label, day_type='training', focus=focus))
        else:
            # Give Phase 1 users a light active-recovery nudge (walking) on
            # some non-training days rather than pure rest, per Section 7.
            if phase == 'phase1' and (i - (training_slots[-1] if training_slots else 0)) % 2 == 1:
                day_plans.append(DayPlan(
                    day_index=i, label=f"{day_names[i]} — Walking / Light Activity",
                    day_type='active_recovery', focus='cardio'
                ))
            else:
                day_plans.append(DayPlan(day_index=i, label=f"{day_names[i]} — Rest", day_type='rest'))

    cardio_target = {
        'phase1': 60, 'phase2': 90, 'phase3': 120, 'phase4': 120,
    }.get(phase, 90)
    if goal == 'endurance':
        cardio_target += 30

    return ProgramStructure(
        phase=phase,
        days_per_week_trained=training_days,
        day_plans=day_plans,
        session_minutes=minutes,
        weekly_cardio_minutes_target=cardio_target,
    )
