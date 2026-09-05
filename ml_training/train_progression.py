"""
Model 2 (fixed): Experience-tier predictor, used to derive progression suggestions.

Predicts a user's Experience_Level (1=beginner, 2=intermediate, 3=expert) from
physiological/behavioral signals ALONE — Experience_Level itself is never an
input feature, so there's no label leakage.

How this becomes a "progress/hold/regress" suggestion:
In your Django code, compare this model's PREDICTED tier against the user's
STATED tier (from their profile/assessment):
    predicted > stated  -> suggest "progress"
    predicted < stated  -> suggest "hold" or "regress"
    predicted == stated -> suggest "hold"
That comparison is plain business logic — the model's job is only to predict
the tier from behavior, honestly, with no shortcuts.

Dataset: gym_members_exercise_tracking.csv
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

df = pd.read_csv("data/gym_members_exercise_tracking.csv")

# Independent features only — NOT including Experience_Level
FEATURES = ["Resting_BPM", "Avg_BPM"]
TARGET = "Experience_Level"  # 1, 2, 3 in the raw data

df = df.dropna(subset=FEATURES + [TARGET])

X = df[FEATURES]
y = df[TARGET]  # already numeric (1/2/3), no encoding needed

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)
print(classification_report(y_test, preds))

joblib.dump({
    "model": model,
    "feature_order": FEATURES,
}, "models/progression_predictor.pkl")

print("Saved to models/progression_predictor.pkl")
print("Predicted tiers: 1=beginner, 2=intermediate, 3=expert")
