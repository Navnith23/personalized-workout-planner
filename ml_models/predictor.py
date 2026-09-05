import joblib
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

_progression_bundle = None
_recovery_bundle = None


def _load_progression():
    global _progression_bundle
    if _progression_bundle is None:
        path = Path(settings.BASE_DIR) / "ml_models" / "progression_predictor.pkl"
        _progression_bundle = joblib.load(path)
    return _progression_bundle


def _load_recovery():
    global _recovery_bundle
    if _recovery_bundle is None:
        path = Path(settings.BASE_DIR) / "ml_models" / "recovery_signal.pkl"
        _recovery_bundle = joblib.load(path)
    return _recovery_bundle


def predict_experience_tier(workout_frequency, bmi):
    bundle = _load_progression()
    model = bundle["model"]
    features = [[workout_frequency, bmi]]
    prediction = int(model.predict(features)[0])
    logger.info(
        "ML progression prediction: workout_frequency=%s bmi=%s predicted_tier=%s",
        workout_frequency,
        bmi,
        prediction,
    )
    return prediction


def ml_progression_hint(stated_tier_label, workout_frequency, bmi):
    if workout_frequency is None or bmi is None:
        return None

    tier_map = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 3}
    stated = tier_map.get((stated_tier_label or "").lower())
    if stated is None:
        return None

    predicted = predict_experience_tier(workout_frequency, bmi)

    if predicted > stated:
        return "Your training pattern looks more advanced than your current level — consider progressing."
    if predicted < stated:
        return "Your training pattern looks lighter than your current level — hold steady for now."
    return None


def check_recovery_flag(resting_bpm, avg_workout_bpm):
    if resting_bpm is None or avg_workout_bpm is None:
        return False
    bundle = _load_recovery()
    model = bundle["model"]
    result = model.predict([[resting_bpm, avg_workout_bpm]])
    flagged = result[0] == -1
    logger.info(
        "ML recovery prediction: resting_bpm=%s avg_workout_bpm=%s flagged=%s",
        resting_bpm,
        avg_workout_bpm,
        flagged,
    )
    return flagged
