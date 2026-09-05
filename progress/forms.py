from django import forms
from .models import CheckIn


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
            'difficulty': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'energy': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'recovery': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'enjoyment': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'pain_details': forms.Textarea(attrs={'rows': 2}),
            'barrier_to_completion': forms.Textarea(attrs={'rows': 2}),
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
