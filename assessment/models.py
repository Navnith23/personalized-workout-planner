from django.conf import settings
from django.db import models


class Assessment(models.Model):
    """
    One full pass through the assessment workflow (Section 6 of the spec).
    A user may retake the assessment over time; each retake produces a new
    row so history is preserved and the planner can compare against the
    previous snapshot.
    """

    STATUS_CHOICES = [
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked — needs professional evaluation'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assessments'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

    # ---- Step 2: Safety screening --------------------------------------
    has_current_pain_or_injury = models.BooleanField(null=True, blank=True)
    pain_or_injury_details = models.TextField(blank=True)
    has_medical_condition_affecting_exercise = models.BooleanField(null=True, blank=True)
    medical_condition_details = models.TextField(blank=True)
    has_cardiovascular_symptoms = models.BooleanField(
        null=True, blank=True,
        help_text='Chest pain/pressure, irregular heartbeat, etc. during activity'
    )
    has_dizziness_or_fainting = models.BooleanField(null=True, blank=True)
    has_unusual_shortness_of_breath = models.BooleanField(null=True, blank=True)
    has_prior_exercise_restrictions = models.BooleanField(null=True, blank=True)
    exercise_restriction_details = models.TextField(blank=True)
    had_recent_surgery_or_injury = models.BooleanField(null=True, blank=True)
    recent_surgery_details = models.TextField(blank=True)
    other_safety_concern = models.TextField(blank=True)

    safety_cleared = models.BooleanField(
        null=True, blank=True,
        help_text='Result of the safety validator. Null until evaluated.'
    )
    safety_flags = models.JSONField(default=list, blank=True)

    # ---- Step 3: Lifestyle ----------------------------------------------
    wake_time = models.TimeField(null=True, blank=True)
    sleep_time = models.TimeField(null=True, blank=True)
    sleep_duration_hours = models.FloatField(null=True, blank=True)
    occupation_schedule = models.CharField(
        max_length=30,
        choices=[
            ('desk_fixed', 'Desk job, fixed hours'),
            ('desk_flexible', 'Desk job, flexible hours'),
            ('student', 'Student'),
            ('on_feet', 'On my feet most of the day'),
            ('physical_labor', 'Physical labor'),
            ('shift_work', 'Shift work / irregular'),
            ('unemployed_home', 'Not currently working / home'),
        ],
        blank=True,
    )
    sedentary_hours_per_day = models.FloatField(null=True, blank=True)
    daily_activity_level = models.CharField(
        max_length=20,
        choices=[
            ('very_low', 'Very low — mostly sitting'),
            ('low', 'Low — light walking'),
            ('moderate', 'Moderate — regularly on my feet'),
            ('high', 'High — physically active job/life'),
        ],
        blank=True,
    )
    meals_per_day = models.PositiveIntegerField(null=True, blank=True)
    meal_schedule_consistency = models.CharField(
        max_length=20,
        choices=[('consistent', 'Consistent'), ('somewhat', 'Somewhat consistent'), ('irregular', 'Irregular')],
        blank=True,
    )
    stress_level = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High'), ('very_high', 'Very high')],
        blank=True,
    )
    schedule_consistency = models.CharField(
        max_length=20,
        choices=[('very_consistent', 'Very consistent'), ('somewhat', 'Somewhat variable'), ('unpredictable', 'Unpredictable')],
        blank=True,
    )
    available_workout_windows = models.CharField(
        max_length=255, blank=True,
        help_text='Comma-separated free-text windows, e.g. "early morning, evening"'
    )

    # ---- Step 4: Goals ----------------------------------------------------
    primary_goal = models.CharField(
        max_length=30,
        choices=[
            ('fat_loss', 'Fat loss'),
            ('muscle_gain', 'Muscle gain'),
            ('strength', 'Strength'),
            ('endurance', 'Endurance'),
            ('general_fitness', 'General fitness'),
            ('mobility', 'Mobility'),
            ('maintenance', 'Maintenance'),
        ],
        blank=True,
    )
    secondary_goals = models.JSONField(default=list, blank=True)

    # ---- Step 5: Exercise experience --------------------------------------
    training_experience = models.CharField(
        max_length=20,
        choices=[
            ('none', 'None / never trained'),
            ('under_6mo', 'Under 6 months'),
            ('6mo_2y', '6 months – 2 years'),
            ('2y_5y', '2 – 5 years'),
            ('5y_plus', '5+ years'),
        ],
        blank=True,
    )
    past_training_frequency_per_week = models.PositiveIntegerField(null=True, blank=True)
    past_training_type = models.CharField(max_length=255, blank=True)
    time_since_last_trained = models.CharField(
        max_length=20,
        choices=[
            ('currently_training', 'Currently training'),
            ('under_1mo', 'Less than a month ago'),
            ('1_6mo', '1 – 6 months ago'),
            ('6mo_2y', '6 months – 2 years ago'),
            ('2y_plus', 'More than 2 years ago'),
            ('never', 'Never'),
        ],
        blank=True,
    )
    familiar_exercises = models.TextField(blank=True, help_text='Comma-separated')
    reason_stopped = models.TextField(blank=True)

    experience_level = models.CharField(
        max_length=30,
        choices=[
            ('beginner', 'Beginner'),
            ('deconditioned_beginner', 'Deconditioned Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        blank=True,
    )

    # ---- Step 6: Fitness assessment ---------------------------------------
    walking_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    walking_pace = models.CharField(
        max_length=20,
        choices=[('slow', 'Slow'), ('moderate', 'Moderate'), ('brisk', 'Brisk'), ('fast', 'Fast/can jog')],
        blank=True,
    )
    stair_tolerance = models.CharField(
        max_length=20,
        choices=[
            ('poor', 'Struggle with 1 flight'), ('fair', 'OK with 1-2 flights'),
            ('good', 'OK with 3+ flights'), ('very_good', 'No issue, several flights'),
        ],
        blank=True,
    )
    sit_to_stand_reps_30s = models.PositiveIntegerField(null=True, blank=True, help_text='Reps in 30 seconds')
    squat_variation = models.CharField(
        max_length=20,
        choices=[
            ('none', "Can't squat comfortably"), ('assisted', 'Assisted / partial range'),
            ('bodyweight', 'Full bodyweight squat'), ('loaded', 'Loaded squat'),
        ],
        blank=True,
    )
    pushup_variation = models.CharField(
        max_length=20,
        choices=[
            ('none', "Can't do a push-up"), ('wall_incline', 'Wall / incline push-up'),
            ('knee', 'Knee push-up'), ('full', 'Full push-up'), ('advanced', 'Advanced variation'),
        ],
        blank=True,
    )
    plank_hold_seconds = models.PositiveIntegerField(null=True, blank=True)
    mobility_balance_rating = models.CharField(
        max_length=20,
        choices=[('poor', 'Poor'), ('fair', 'Fair'), ('good', 'Good'), ('very_good', 'Very good')],
        blank=True,
    )
    perceived_exertion_after_tests = models.PositiveIntegerField(
        null=True, blank=True, help_text='RPE 1-10 after the fitness tests'
    )

    # Derived capacity scores (0-100), set by the planner's profile builder
    strength_capacity = models.FloatField(null=True, blank=True)
    cardio_capacity = models.FloatField(null=True, blank=True)
    work_capacity = models.FloatField(null=True, blank=True)
    mobility_score = models.FloatField(null=True, blank=True)
    balance_score = models.FloatField(null=True, blank=True)

    # ---- Step 7: Training constraints --------------------------------------
    training_location = models.CharField(
        max_length=20,
        choices=[('home_no_equip', 'Home, no equipment'), ('home_some_equip', 'Home, some equipment'),
                  ('gym', 'Gym'), ('outdoor', 'Outdoor'), ('mixed', 'Mixed')],
        blank=True,
    )
    available_equipment = models.JSONField(default=list, blank=True)
    days_per_week_available = models.PositiveIntegerField(null=True, blank=True)
    minutes_per_session = models.PositiveIntegerField(null=True, blank=True)
    preferred_workout_time = models.CharField(
        max_length=20,
        choices=[('early_morning', 'Early morning'), ('morning', 'Morning'), ('midday', 'Midday'),
                  ('afternoon', 'Afternoon'), ('evening', 'Evening'), ('late_night', 'Late night'),
                  ('varies', 'Varies')],
        blank=True,
    )
    exercise_preferences = models.TextField(blank=True, help_text='Comma-separated, free text')
    exercises_to_avoid = models.TextField(blank=True, help_text='Comma-separated, free text')

    # ---- Derived outputs from the recommendation engine --------------------
    training_phase = models.CharField(
        max_length=20,
        choices=[('phase1', 'Phase 1 — Habit & Tolerance'), ('phase2', 'Phase 2 — Foundation'),
                  ('phase3', 'Phase 3 — Development'), ('phase4', 'Phase 4 — Specialized')],
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Assessment({self.user.username}, {self.status}, {self.created_at:%Y-%m-%d})"
