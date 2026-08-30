from django.db import models


class Exercise(models.Model):
    MOVEMENT_PATTERNS = [
        ('squat', 'Squat'),
        ('hinge', 'Hinge'),
        ('lunge', 'Lunge'),
        ('push_horizontal', 'Horizontal push'),
        ('push_vertical', 'Vertical push'),
        ('pull_horizontal', 'Horizontal pull'),
        ('pull_vertical', 'Vertical pull'),
        ('core', 'Core / anti-rotation'),
        ('carry', 'Carry'),
        ('gait', 'Gait / locomotion'),
        ('mobility', 'Mobility / stretch'),
        ('balance', 'Balance'),
    ]

    MUSCLE_GROUPS = [
        ('quads', 'Quads'), ('hamstrings', 'Hamstrings'), ('glutes', 'Glutes'),
        ('calves', 'Calves'), ('chest', 'Chest'), ('back', 'Back'),
        ('shoulders', 'Shoulders'), ('biceps', 'Biceps'), ('triceps', 'Triceps'),
        ('core', 'Core'), ('full_body', 'Full body'), ('cardio', 'Cardiovascular'),
    ]

    EQUIPMENT_CHOICES = [
        ('none', 'No equipment'), ('dumbbells', 'Dumbbells'), ('barbell', 'Barbell'),
        ('resistance_bands', 'Resistance bands'), ('kettlebell', 'Kettlebell'),
        ('pullup_bar', 'Pull-up bar'), ('bench', 'Bench'), ('full_gym', 'Full gym access'),
        ('cardio_machine', 'Cardio machine'),
    ]

    DIFFICULTY_CHOICES = [
        (1, 'Very easy / regression'),
        (2, 'Beginner'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Very advanced'),
    ]

    EXERCISE_TYPE_CHOICES = [
        ('warmup', 'Warm-up'),
        ('main_strength', 'Main strength'),
        ('accessory', 'Accessory'),
        ('cardio', 'Cardio'),
        ('mobility', 'Mobility / cooldown'),
        ('core', 'Core'),
    ]

    name = models.CharField(max_length=150, unique=True)
    movement_pattern = models.CharField(max_length=20, choices=MOVEMENT_PATTERNS)
    muscle_groups = models.JSONField(default=list, help_text='List of muscle group codes')
    equipment = models.CharField(max_length=20, choices=EQUIPMENT_CHOICES, default='none')
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=2)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPE_CHOICES, default='main_strength')
    instructions = models.TextField(blank=True)

    # Self-referential progressions/regressions
    progressions = models.ManyToManyField('self', symmetrical=False, related_name='regressions_of', blank=True)

    default_sets = models.PositiveSmallIntegerField(default=3)
    default_reps = models.CharField(max_length=30, blank=True, help_text='e.g. "8-12" or blank if duration-based')
    default_duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    default_rest_seconds = models.PositiveIntegerField(default=60)

    is_low_impact = models.BooleanField(default=True)
    is_beginner_safe = models.BooleanField(default=True)
    tags = models.JSONField(default=list, blank=True, help_text='Free-text tags, e.g. "running", "hiit"')

    class Meta:
        ordering = ['exercise_type', 'movement_pattern', 'difficulty']

    def __str__(self):
        return self.name
