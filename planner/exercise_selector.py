"""
Filter and select exercises for a given day-focus, respecting equipment,
preferences, avoided exercises, and the user's current difficulty ceiling
(Section 9).
"""
import re
from exercises.models import Exercise

# Movement patterns that should appear for each "focus" type, in priority
# order. The generator walks this list and tries to fill each slot.
FOCUS_PATTERNS = {
    'full_body': ['squat', 'hinge', 'push_horizontal', 'pull_horizontal', 'core'],
    'upper': ['push_horizontal', 'pull_horizontal', 'push_vertical', 'pull_vertical', 'core'],
    'lower': ['squat', 'hinge', 'lunge', 'core'],
    'push': ['push_horizontal', 'push_vertical', 'push_horizontal', 'core'],
    'pull': ['pull_horizontal', 'pull_vertical', 'pull_horizontal', 'core'],
    'legs': ['squat', 'hinge', 'lunge', 'core'],
    'cardio': ['gait'],
}

EXPERIENCE_DIFFICULTY_CEILING = {
    'deconditioned_beginner': 2,
    'beginner': 2,
    'intermediate': 4,
    'advanced': 5,
}

PHASE_DIFFICULTY_CEILING = {
    'phase1': 2,
    'phase2': 3,
    'phase3': 4,
    'phase4': 5,
}


def _split_free_text_list(text):
    if not text:
        return []
    return [t.strip().lower() for t in re.split(r'[,\n]', text) if t.strip()]


def base_queryset(assessment):
    """Apply hard constraints: equipment availability and explicit avoidances."""
    equipment = assessment.available_equipment or []
    allowed_equipment = set(equipment) | {'none'}
    if 'full_gym' in allowed_equipment:
        # Full gym access implies everything else is available too.
        allowed_equipment |= {'dumbbells', 'barbell', 'kettlebell', 'pullup_bar', 'bench', 'cardio_machine', 'resistance_bands'}

    qs = Exercise.objects.filter(equipment__in=allowed_equipment)

    avoid = _split_free_text_list(assessment.exercises_to_avoid)
    for term in avoid:
        qs = qs.exclude(name__icontains=term)

    ceiling = min(
        EXPERIENCE_DIFFICULTY_CEILING.get(assessment.experience_level, 2),
        PHASE_DIFFICULTY_CEILING.get(assessment.training_phase, 2),
    )
    qs = qs.filter(difficulty__lte=ceiling)

    # Any active safety flag (pain/injury/medical/recent surgery) narrows
    # the pool to low-impact, beginner-safe movements only, regardless of
    # the computed experience level.
    if assessment.safety_flags:
        qs = qs.filter(is_low_impact=True, is_beginner_safe=True)

    return qs


def _score_preference(exercise, preferences):
    if not preferences:
        return 0
    name_lower = exercise.name.lower()
    tags_lower = [t.lower() for t in (exercise.tags or [])]
    for pref in preferences:
        if pref in name_lower or pref in tags_lower or pref in exercise.movement_pattern:
            return 1
    return 0


def select_exercises_for_focus(assessment, focus, exclude_ids=None):
    """
    Return an ordered list of Exercise instances covering the movement
    patterns appropriate for this day's focus.
    """
    exclude_ids = exclude_ids or set()
    qs = base_queryset(assessment).exclude(id__in=exclude_ids)
    preferences = _split_free_text_list(assessment.exercise_preferences)

    patterns = FOCUS_PATTERNS.get(focus, FOCUS_PATTERNS['full_body'])
    chosen = []
    used_ids = set(exclude_ids)

    for pattern in patterns:
        candidates = list(
            qs.filter(movement_pattern=pattern, exercise_type__in=['main_strength', 'accessory'])
            .exclude(id__in=used_ids)
        )
        if not candidates:
            continue
        candidates.sort(key=lambda e: (-_score_preference(e, preferences), e.difficulty))
        pick = candidates[0]
        chosen.append(pick)
        used_ids.add(pick.id)

    return chosen


def select_warmup(assessment, count=1):
    qs = base_queryset(assessment).filter(exercise_type='warmup')
    return list(qs[:count])


def select_cooldown(assessment, count=1):
    qs = base_queryset(assessment).filter(exercise_type='mobility')
    return list(qs[:count])


def select_cardio(assessment, count=1):
    preferences = _split_free_text_list(assessment.exercise_preferences)
    qs = base_queryset(assessment).filter(exercise_type='cardio')
    candidates = list(qs)
    candidates.sort(key=lambda e: (-_score_preference(e, preferences), e.difficulty))
    return candidates[:count]
