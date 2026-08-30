"""
Thin service layer so views don't import planner internals directly.
Keeps the recommendation engine swappable/testable independent of Django.
"""
from planner.recommendation import generate_plan


def run_recommendation_engine(user, assessment):
    return generate_plan(user, assessment)
