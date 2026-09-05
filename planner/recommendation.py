"""
Top-level orchestrator (Section 8):

    Assessment -> Safety Validator -> Profile Builder -> Training Phase
    -> Program Structure -> Exercise Filter -> Workout Generator

Django views should call `generate_plan(user, assessment)` and handle the
two possible outcomes: a blocked result (safety concern) or a Program.
"""
from dataclasses import dataclass

from . import profile_builder
from . import phase_selector
from . import program_selector
from . import workout_generator
from ml_models.predictor import ml_progression_hint


@dataclass
class PlanResult:
    blocked: bool
    safety_flags: list
    program = None


def generate_plan(user, assessment):
    safety = profile_builder.build_profile(assessment)

    if not safety.cleared:
        return PlanResult(blocked=True, safety_flags=safety.flags)

    profile = getattr(user, 'profile', None)
    ml_hint = None
    if profile:
        ml_hint = ml_progression_hint(
            stated_tier_label=assessment.experience_level,
            workout_frequency=assessment.past_training_frequency_per_week,
            bmi=profile.bmi,
        )

    phase = phase_selector.select_training_phase(assessment, ml_hint=ml_hint)
    assessment.training_phase = phase
    assessment.status = 'completed'
    assessment.save()

    structure = program_selector.build_program_structure(assessment)
    program = workout_generator.generate_program(user, assessment, structure)

    result = PlanResult(blocked=False, safety_flags=safety.flags)
    result.program = program
    return result
