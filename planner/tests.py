from types import SimpleNamespace
from unittest import TestCase

from .phase_selector import PHASE_2, PHASE_3, select_training_phase
from .profile_builder import compute_capacity_scores
from .workout_generator import _preset_for


def assessment(**overrides):
    values = {
        'walking_duration_minutes': 30,
        'walking_pace': 'moderate',
        'stair_tolerance': 'fair',
        'squat_variation': 'bodyweight',
        'pushup_variation': 'knee',
        'sit_to_stand_reps_30s': 10,
        'perceived_exertion_after_tests': 5,
        'mobility_balance_rating': 'fair',
        'plank_hold_seconds': 30,
        'training_phase': 'phase2',
        'primary_goal': 'muscle_gain',
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class ProfileBuilderTests(TestCase):
    def test_numeric_tests_preserve_distinct_capacity_values(self):
        lower = compute_capacity_scores(assessment(sit_to_stand_reps_30s=9))
        higher = compute_capacity_scores(assessment(sit_to_stand_reps_30s=11))

        self.assertLess(lower['strength_capacity'], higher['strength_capacity'])


class PhaseSelectorTests(TestCase):
    def test_ml_hint_can_nudge_capable_user_one_phase(self):
        user = assessment(
            experience_level='beginner',
            cardio_capacity=60,
            strength_capacity=60,
            work_capacity=60,
            sedentary_hours_per_day=4,
            daily_activity_level='moderate',
            safety_flags=[],
        )

        self.assertEqual(select_training_phase(user), PHASE_2)
        self.assertEqual(
            select_training_phase(user, ml_hint='looks more advanced'),
            PHASE_3,
        )

    def test_ml_hint_cannot_bypass_safety_flags(self):
        user = assessment(
            experience_level='beginner',
            cardio_capacity=60,
            strength_capacity=60,
            work_capacity=60,
            sedentary_hours_per_day=4,
            daily_activity_level='moderate',
            safety_flags=['Current pain or injury'],
        )

        self.assertEqual(select_training_phase(user, ml_hint='looks more advanced'), PHASE_2)


class WorkoutPresetTests(TestCase):
    def test_goal_changes_set_count(self):
        strength = _preset_for(assessment(primary_goal='strength'))
        endurance = _preset_for(assessment(primary_goal='endurance'))

        self.assertGreater(strength['sets'], endurance['sets'])