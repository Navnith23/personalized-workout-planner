from django.conf import settings
from django.db import models

from programs.models import Program, WorkoutDay


class WorkoutLog(models.Model):
    """Records that a user completed (or skipped) a given workout day."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workout_logs')
    day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name='logs')
    completed = models.BooleanField(default=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    perceived_difficulty = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text='RPE 1-10 for the session as a whole'
    )
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} — {self.day} — {'done' if self.completed else 'skipped'}"


class CheckIn(models.Model):
    """Weekly check-in per Section 14 of the spec."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checkins')
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True, related_name='checkins')
    week_number = models.PositiveSmallIntegerField()

    planned_sessions = models.PositiveSmallIntegerField(default=0)
    completed_sessions = models.PositiveSmallIntegerField(default=0)

    difficulty = models.PositiveSmallIntegerField(help_text='1 (too easy) - 10 (too hard)')
    energy = models.PositiveSmallIntegerField(help_text='1 (very low) - 10 (very high)')
    resting_bpm = models.PositiveSmallIntegerField(
            null=True, blank=True, help_text='Optional: resting heart rate, if you track it'
        )
    avg_workout_bpm = models.PositiveSmallIntegerField(
            null=True, blank=True, help_text='Optional: average heart rate during sessions, if you track it'
        )
    recovery = models.PositiveSmallIntegerField(help_text='1 (poor) - 10 (excellent)')
    pain_flag = models.BooleanField(default=False)
    pain_details = models.TextField(blank=True)
    sessions_too_long = models.BooleanField(default=False)
    enjoyment = models.PositiveSmallIntegerField(null=True, blank=True, help_text='1-10')
    disliked_exercises = models.CharField(max_length=255, blank=True)
    performance_change = models.CharField(
        max_length=20,
        choices=[('better', 'Better'), ('same', 'About the same'), ('worse', 'Worse')],
        blank=True,
    )
    barrier_to_completion = models.TextField(blank=True, help_text='What prevented completing sessions, if anything')

    # Result of the progression engine
    recommendation = models.CharField(max_length=30, blank=True)
    recommendation_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    @property
    def completion_rate(self):
        if self.planned_sessions:
            return round(100 * self.completed_sessions / self.planned_sessions)
        return 0

    def __str__(self):
        return f"CheckIn(week {self.week_number}, {self.user.username})"
