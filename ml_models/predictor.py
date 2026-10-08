"""
ML prediction helpers.

IMPORTANT — input mismatch note
--------------------------------
train_progression.py trains on [Resting_BPM, Avg_BPM].
The original predictor.py passed [workout_frequency, bmi] which are
different features → the model always returned tier 2.

Until the model is retrained on the correct features (workout_frequency
and BMI), or the training data is regenerated with those columns, the
ML progression hint is DISABLED.  All call sites that previously called
ml_progression_hint() or check_recovery_flag() now receive safe no-op
returns.

The recovery model (IsolationForest, contamination=0.08) flags ~8% of
any population by construction — it has no real signal until labelled
recovery-anomaly examples are gathered.  It is also disabled until then.
"""
import logging

logger = logging.getLogger(__name__)


def ml_progression_hint(stated_tier_label=None, workout_frequency=None, bmi=None):
    """
    Disabled until the progression model is retrained with the features
    that are actually available at inference time (workout_frequency, bmi).
    Returns None so no spurious hint messages are shown.
    """
    logger.debug(
        "ml_progression_hint called but model is disabled pending retraining "
        "(stated_tier=%s, freq=%s, bmi=%s)",
        stated_tier_label,
        workout_frequency,
        bmi,
    )
    return None


def check_recovery_flag(resting_bpm=None, avg_workout_bpm=None):
    """
    Disabled until the IsolationForest is trained on labelled recovery-
    anomaly examples.  Always returns False so no spurious rest messages
    are shown.
    """
    logger.debug(
        "check_recovery_flag called but model is disabled (resting_bpm=%s, avg_bpm=%s)",
        resting_bpm,
        avg_workout_bpm,
    )
    return False
