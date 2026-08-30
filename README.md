# Personalized Fitness & Lifestyle Planner

A Django web app that assesses a user's lifestyle, physical condition,
goals, preferences, constraints, and exercise experience, then generates a
safe, realistic, progressive exercise + lifestyle plan using a rule-based
(no-ML) recommendation engine.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py makemigrations accounts assessment exercises programs progress
python manage.py migrate

# Seed the exercise library — required before any plan can be generated
python manage.py seed_exercises

# Create an admin account (optional, for /admin/)
python manage.py createsuperuser

python manage.py runserver
```

Then visit `http://127.0.0.1:8000/`.

## How it works

```
Landing → Sign up → Assessment (7 steps) → Safety screen → Review
        → Recommendation engine → Weekly plan
        → Log workouts → Weekly check-in → Plan adapts → repeat
```

The recommendation engine lives entirely under `planner/` and is plain
Python — it does not import Django views, so it can be unit tested in
isolation:

- `planner/profile_builder.py` — safety screen + fitness-test scoring +
  experience classification
- `planner/phase_selector.py` — picks Phase 1–4 conservatively
- `planner/program_selector.py` — decides weekly structure (days, split,
  session length)
- `planner/exercise_selector.py` — filters the exercise library by
  equipment, safety, preferences, and difficulty ceiling
- `planner/workout_generator.py` — writes `Program` / `WorkoutDay` /
  `Workout` rows to the database
- `planner/progression.py` — weekly adaptive progression from check-in data
- `planner/recommendation.py` — orchestrates the above; this is the single
  entry point (`generate_plan(user, assessment)`) that Django views call

If the safety screen finds a hard-stop flag (cardiovascular symptoms,
dizziness/fainting, unusual shortness of breath), the engine never
generates an exercise plan — it routes the user to a page recommending
professional evaluation instead. This app never diagnoses medical
conditions.

## Apps

| App          | Responsibility                                             |
|--------------|--------------------------------------------------------------|
| `accounts`   | Auth, basic profile info                                   |
| `assessment` | The 7-step questionnaire + safety screening                |
| `exercises`  | The exercise library                                       |
| `programs`   | Generated weekly plans (Program/WorkoutDay/Workout)         |
| `progress`   | Workout logging + weekly check-ins + adaptive progression   |
| `planner`    | Pure-Python recommendation engine (no Django dependency)    |

## Notes

- Database is SQLite by default (`db.sqlite3`); swap `DATABASES` in
  `config/settings.py` for PostgreSQL in production.
- `SECRET_KEY` and `DEBUG` read from environment variables
  (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`) with dev-safe defaults — set real
  values before deploying.
- The exercise library seeded by `seed_exercises` is a starter set (~55
  exercises) covering every movement pattern, equipment type, and
  difficulty level the engine needs. Add more via `/admin/` or by
  extending `exercises/management/commands/seed_exercises.py`.
