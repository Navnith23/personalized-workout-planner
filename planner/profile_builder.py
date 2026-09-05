"""
Safety validation and capacity-score computation.

This module is pure Python — it knows nothing about Django views or HTTP.
It takes an `assessment.models.Assessment` instance and:
  1. Runs the safety screen (Section 6, Step 2) and returns flags.
  2. Computes 0-100 capacity scores from the fitness tests (Step 6).
  3. Classifies the user's experience level (Step 5).

Keeping this independent of Django views means it can be unit tested with
plain objects/dicts if desired.
"""
from dataclasses import dataclass, field


@dataclass
class SafetyResult:
    cleared: bool
    flags: list = field(default_factory=list)
    requires_professional_evaluation: bool = False


# Any "yes" answer to these is a hard stop — the user should see a
# professional before receiving an unrestricted plan.
HARD_STOP_FIELDS = [
    ('has_cardiovascular_symptoms', 'Cardiovascular symptoms during activity'),
    ('has_dizziness_or_fainting', 'Dizziness or fainting'),
    ('has_unusual_shortness_of_breath', 'Unusual shortness of breath'),
]

# These raise flags that constrain (but don't block) the plan.
SOFT_FLAG_FIELDS = [
    ('has_current_pain_or_injury', 'Current pain or injury'),
    ('has_medical_condition_affecting_exercise', 'Medical condition affecting exercise'),
    ('has_prior_exercise_restrictions', 'Prior professional exercise restriction'),
    ('had_recent_surgery_or_injury', 'Recent surgery or injury'),
]


def run_safety_screen(assessment) -> SafetyResult:
    """Never diagnoses. Only decides whether to gate the plan."""
    flags = []
    hard_stop = False

    for field_name, label in HARD_STOP_FIELDS:
        if getattr(assessment, field_name) is True:
            flags.append(label)
            hard_stop = True

    for field_name, label in SOFT_FLAG_FIELDS:
        if getattr(assessment, field_name) is True:
            flags.append(label)

    if (assessment.other_safety_concern or '').strip():
        flags.append('Other safety concern noted')

    return SafetyResult(
        cleared=not hard_stop,
        flags=flags,
        requires_professional_evaluation=hard_stop,
    )


def _score_from_choice(value, ordering):
    """Map an ordered choice list to a 0-100 score."""
    if not value or value not in ordering:
        return None
    idx = ordering.index(value)
    return round(100 * idx / max(len(ordering) - 1, 1))


def compute_capacity_scores(assessment) -> dict:
    """Translate raw fitness-test answers into normalized capacity scores."""

    # Cardio capacity: walking duration + pace + stair tolerance
    walk_minutes = assessment.walking_duration_minutes or 0
    walk_score = min(100, round((walk_minutes / 45) * 100, 1)) if walk_minutes else 0
    pace_score = _score_from_choice(assessment.walking_pace, ['slow', 'moderate', 'brisk', 'fast']) or 0
    stair_score = _score_from_choice(
        assessment.stair_tolerance, ['poor', 'fair', 'good', 'very_good']
    ) or 0
    cardio_capacity = round((walk_score * 0.5) + (pace_score * 0.25) + (stair_score * 0.25), 1)

    # Strength capacity: squat + push-up + sit-to-stand
    squat_score = _score_from_choice(
        assessment.squat_variation, ['none', 'assisted', 'bodyweight', 'loaded']
    ) or 0
    pushup_score = _score_from_choice(
        assessment.pushup_variation, ['none', 'wall_incline', 'knee', 'full', 'advanced']
    ) or 0
    sit_to_stand = assessment.sit_to_stand_reps_30s or 0
    sts_score = min(100, round((sit_to_stand / 20) * 100, 1))
    strength_capacity = round((squat_score * 0.4) + (pushup_score * 0.4) + (sts_score * 0.2), 1)

    # Work capacity: blend of cardio + strength + inverse perceived exertion
    exertion = assessment.perceived_exertion_after_tests
    exertion_penalty = 0
    if exertion:
        # Higher exertion for the same tests implies lower current work capacity
        exertion_penalty = max(0, (exertion - 5)) * 4
    work_capacity = max(0, round((cardio_capacity * 0.5 + strength_capacity * 0.5) - exertion_penalty, 1))

    # Mobility / balance
    mobility_score = _score_from_choice(
        assessment.mobility_balance_rating, ['poor', 'fair', 'good', 'very_good']
    )
    plank_seconds = assessment.plank_hold_seconds or 0
    plank_score = min(100, round((plank_seconds / 90) * 100, 1))
    if mobility_score is None:
        mobility_score = plank_score
    else:
        mobility_score = round((mobility_score * 0.6) + (plank_score * 0.4), 1)

    return {
        'cardio_capacity': cardio_capacity,
        'strength_capacity': strength_capacity,
        'work_capacity': work_capacity,
        'mobility_score': mobility_score,
        'balance_score': mobility_score,  # single combined mobility/balance test in this simplified engine
    }


def classify_experience_level(assessment) -> str:
    """
    Classify Beginner / Deconditioned Beginner / Intermediate / Advanced
    using training history + how recently they trained + current capacity.
    """
    experience = assessment.training_experience or 'none'
    recency = assessment.time_since_last_trained or 'never'

    long_layoff = recency in ('2y_plus', 'never')
    very_deconditioned = (
        (assessment.cardio_capacity or 0) < 25 and (assessment.strength_capacity or 0) < 25
    )

    if experience in ('none',) or recency == 'never':
        if very_deconditioned or (assessment.sedentary_hours_per_day or 0) >= 10:
            return 'deconditioned_beginner'
        return 'beginner'

    if experience == 'under_6mo':
        return 'deconditioned_beginner' if (long_layoff or very_deconditioned) else 'beginner'

    if experience == '6mo_2y':
        if long_layoff or very_deconditioned:
            return 'beginner'
        return 'intermediate'

    if experience in ('2y_5y', '5y_plus'):
        if long_layoff or very_deconditioned:
            return 'beginner'
        if recency in ('6mo_2y',):
            return 'intermediate'
        return 'advanced' if experience == '5y_plus' else 'intermediate'

    return 'beginner'


def build_profile(assessment):
    """
    Run the full profile-building pipeline against an Assessment instance
    and persist the derived fields. Returns the SafetyResult so the caller
    (a view) can decide whether to redirect the user to a "see a
    professional" page instead of generating a plan.
    """
    safety = run_safety_screen(assessment)
    assessment.safety_cleared = safety.cleared
    assessment.safety_flags = safety.flags

    if not safety.cleared:
        assessment.status = 'blocked'
        assessment.save()
        return safety

    scores = compute_capacity_scores(assessment)
    for key, value in scores.items():
        setattr(assessment, key, value)

    assessment.experience_level = classify_experience_level(assessment)
    assessment.save()
    return safety
