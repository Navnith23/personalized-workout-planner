"""
Model 3: Recovery / overtraining signal (NOT a medical diagnosis)
Flags statistical outlier patterns in heart-rate and training-load data
that correlate with overtraining risk in this dataset. This is a soft
signal for your UI ("consider an extra rest day"), not an injury predictor.

Dataset: gym_members_exercise_tracking.csv
"""
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

df = pd.read_csv("data/gym_members_exercise_tracking.csv")

FEATURES = ["Resting_BPM", "Avg_BPM"]
df = df.dropna(subset=FEATURES)

X = df[FEATURES]

# Unsupervised: learns what "normal" load/HR patterns look like,
# flags outliers as a caution signal. contamination=0.08 means it'll
# flag roughly the most unusual 8% of patterns.
model = IsolationForest(contamination=0.08, random_state=42)
model.fit(X)

joblib.dump({
    "model": model,
    "feature_order": list(X.columns),
}, "models/recovery_signal.pkl")

print("Saved to models/recovery_signal.pkl")
print("Use model.predict(X) at inference time: -1 = flagged/unusual, 1 = normal")
