# ML Training Setup

## 1. Install dependencies
```bash
pip install pandas scikit-learn joblib
```

## 2. Download the dataset
Get `gym_members_exercise_tracking.csv` from:
https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset

Place it at: `data/gym_members_exercise_tracking.csv`

## 3. Folder structure
```
ml_training/
  data/
    gym_members_exercise_tracking.csv
  models/          <- created automatically when you run the scripts
  train_recommender.py
  train_progression.py
  train_recovery_signal.py
```

## 4. Run each script
```bash
python train_recommender.py
python train_progression.py
python train_recovery_signal.py
```

Each prints a quick accuracy report and saves a `.pkl` file into `models/`.

## 5. What you'll have afterward
- `models/workout_recommender.pkl`
- `models/progression_predictor.pkl`
- `models/recovery_signal.pkl`

These 3 files are small (a few hundred KB to a couple MB) — copy them into
your Django project (e.g. a new `ml_models/` folder) and commit them to
your repo like any other file. No training happens on PythonAnywhere —
it only ever loads these pre-trained files with `joblib.load(...)`.

## Notes on model quality
- Model 2's labels are a heuristic I derived (there's no "should progress"
  column in the raw data) — treat it as a reasonable starting point, not
  ground truth. Once you have real weekly check-in data from actual users,
  retrain on that instead for much better accuracy.
- Model 3 is unsupervised (no true "injury" labels exist in this dataset).
  Frame it in your UI as a soft caution signal, not a diagnosis.
