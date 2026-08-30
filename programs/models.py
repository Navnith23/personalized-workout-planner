from django.conf import settings
from django.db import models

from exercises.models import Exercise


class Program(models.Model):
    """A generated weekly program instance belonging to a user."""

    PHASE_CHOICES = [
        ('phase1', 'Phase 1 — Habit & Tolerance'),
        ('phase2', 'Phase 2 — Foundation'),
        ('phase3', 'Phase 3 — Development'),
        ('phase4', 'Phase 4 — Specialized'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='programs')
    assessment = models.ForeignKey(
        'assessment.Assessment', on_delete=models.SET_NULL, null=True, blank=True, related_name='programs'
    )
    name = models.CharField(max_length=150)
    goal = models.CharField(max_length=30, blank=True)
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES)
    difficulty = models.CharField(max_length=30, blank=True)
    days_per_week = models.PositiveSmallIntegerField()
    duration_weeks = models.PositiveSmallIntegerField(default=4)

    is_active = models.BooleanField(default=True)
    week_number = models.PositiveSmallIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (week {self.week_number}) — {self.user.username}"

    def save(self, *args, **kwargs):
        if self.is_active:
            Program.objects.filter(user=self.user, is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class WorkoutDay(models.Model):
    """A single day within a Program's week (e.g. Monday)."""

    DAY_TYPE_CHOICES = [
        ('training', 'Training'),
        ('active_recovery', 'Active recovery'),
        ('rest', 'Rest'),
    ]

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='days')
    day_index = models.PositiveSmallIntegerField(help_text='0=Monday .. 6=Sunday')
    label = models.CharField(max_length=100, blank=True)
    day_type = models.CharField(max_length=20, choices=DAY_TYPE_CHOICES, default='training')

    class Meta:
        ordering = ['day_index']
        unique_together = ('program', 'day_index')

    def __str__(self):
        return f"{self.get_day_type_display()} — {self.label}"


class Workout(models.Model):
    """A single exercise prescription within a WorkoutDay."""

    SECTION_CHOICES = [
        ('warmup', 'Warm-up'),
        ('main', 'Main'),
        ('accessory', 'Accessory'),
        ('cardio', 'Cardio'),
        ('cooldown', 'Cool-down / mobility'),
    ]

    day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name='workouts')
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name='workouts')
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='main')
    order = models.PositiveSmallIntegerField(default=0)

    sets = models.PositiveSmallIntegerField(default=3)
    reps = models.CharField(max_length=30, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    rest_seconds = models.PositiveIntegerField(default=60)
    intensity_target = models.CharField(
        max_length=60, blank=True,
        help_text='e.g. "RPE 6-7", "conversational pace", "RIR 2-3"'
    )
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['section', 'order']

    def __str__(self):
        return f"{self.exercise.name} — {self.sets}x{self.reps or self.duration_seconds}"
