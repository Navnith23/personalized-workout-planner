from django import forms
from django.core.exceptions import ValidationError

from .models import CheckIn

# Hard limits — identical to the widget attrs so server agrees with the UI
FIELD_LIMITS = {
    'difficulty':          (1, 10),
    'energy':              (1, 10),
    'recovery':            (1, 10),
    'enjoyment':           (1, 10),
    'planned_sessions':    (0, 14),
    'completed_sessions':  (0, 14),
    'resting_bpm':         (30, 220),
    'avg_workout_bpm':     (30, 220),
}


def _validate_range(value, lo, hi, name):
    if value is not None and not (lo <= value <= hi):
        raise ValidationError(
            f"{name} must be between {lo} and {hi} (got {value})."
        )


class CheckInForm(forms.ModelForm):
    class Meta:
        model = CheckIn
        fields = [
            'planned_sessions', 'completed_sessions', 'difficulty', 'energy', 'recovery',
            'resting_bpm', 'avg_workout_bpm',
            'pain_flag', 'pain_details', 'sessions_too_long', 'enjoyment',
            'disliked_exercises', 'performance_change', 'barrier_to_completion',
        ]
        widgets = {
            'difficulty':   forms.NumberInput(attrs={'min': 1,  'max': 10}),
            'energy':       forms.NumberInput(attrs={'min': 1,  'max': 10}),
            'recovery':     forms.NumberInput(attrs={'min': 1,  'max': 10}),
            'enjoyment':    forms.NumberInput(attrs={'min': 1,  'max': 10}),
            'planned_sessions':   forms.NumberInput(attrs={'min': 0, 'max': 14}),
            'completed_sessions': forms.NumberInput(attrs={'min': 0, 'max': 14}),
            'resting_bpm':        forms.NumberInput(attrs={'min': 30, 'max': 220}),
            'avg_workout_bpm':    forms.NumberInput(attrs={'min': 30, 'max': 220}),
            'pain_details':             forms.Textarea(attrs={'rows': 2}),
            'barrier_to_completion':    forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'difficulty': 'How difficult were your sessions? (1 easy – 10 very hard)',
            'energy': 'Energy levels this week? (1 low – 10 high)',
            'recovery': 'How well have you been recovering? (1 poor – 10 excellent)',
            'resting_bpm': 'Resting heart rate (optional, if you track it)',
            'avg_workout_bpm': 'Average heart rate during workouts (optional)',
            'pain_flag': 'Any pain or discomfort during training?',
            'sessions_too_long': 'Were sessions too long for your schedule?',
            'barrier_to_completion': 'What prevented you from completing sessions, if anything?',
        }

    # ---- Server-side range validators (widget attrs only protect the browser) ----

    def clean_difficulty(self):
        v = self.cleaned_data.get('difficulty')
        _validate_range(v, 1, 10, 'Difficulty')
        return v

    def clean_energy(self):
        v = self.cleaned_data.get('energy')
        _validate_range(v, 1, 10, 'Energy')
        return v

    def clean_recovery(self):
        v = self.cleaned_data.get('recovery')
        _validate_range(v, 1, 10, 'Recovery')
        return v

    def clean_enjoyment(self):
        v = self.cleaned_data.get('enjoyment')
        _validate_range(v, 1, 10, 'Enjoyment')
        return v

    def clean_planned_sessions(self):
        v = self.cleaned_data.get('planned_sessions')
        _validate_range(v, 0, 14, 'Planned sessions')
        return v

    def clean_completed_sessions(self):
        v = self.cleaned_data.get('completed_sessions')
        _validate_range(v, 0, 14, 'Completed sessions')
        return v

    def clean_resting_bpm(self):
        v = self.cleaned_data.get('resting_bpm')
        _validate_range(v, 30, 220, 'Resting BPM')
        return v

    def clean_avg_workout_bpm(self):
        v = self.cleaned_data.get('avg_workout_bpm')
        _validate_range(v, 30, 220, 'Average workout BPM')
        return v

    def clean(self):
        cleaned = super().clean()
        planned   = cleaned.get('planned_sessions', 0) or 0
        completed = cleaned.get('completed_sessions', 0) or 0
        if completed > planned and planned > 0:
            raise ValidationError(
                "Completed sessions cannot exceed planned sessions."
            )
        return cleaned
