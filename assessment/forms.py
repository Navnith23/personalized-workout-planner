from django import forms
from .models import Assessment


YES_NO_CHOICES = [(True, 'Yes'), (False, 'No')]


class SafetyScreeningForm(forms.ModelForm):
    has_current_pain_or_injury = forms.TypedChoiceField(
        choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect, label='Do you currently have any pain or injury?'
    )
    has_medical_condition_affecting_exercise = forms.TypedChoiceField(
        choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect,
        label='Do you have a medical condition that could affect exercise?'
    )
    has_cardiovascular_symptoms = forms.TypedChoiceField(
        choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect,
        label='Do you ever get chest pain, pressure, or an irregular heartbeat during activity?'
    )
    has_dizziness_or_fainting = forms.TypedChoiceField(
        choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect,
        label='Do you experience dizziness or fainting?'
    )
    has_unusual_shortness_of_breath = forms.TypedChoiceField(
        choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect,
        label='Do you experience unusual shortness of breath, even with light activity?'
    )
    has_prior_exercise_restrictions = forms.TypedChoiceField(
        choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect,
        label='Has a doctor ever restricted your physical activity?'
    )
    had_recent_surgery_or_injury = forms.TypedChoiceField(
        choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect,
        label='Have you had recent surgery or a significant injury (last 3 months)?'
    )

    class Meta:
        model = Assessment
        fields = [
            'has_current_pain_or_injury', 'pain_or_injury_details',
            'has_medical_condition_affecting_exercise', 'medical_condition_details',
            'has_cardiovascular_symptoms',
            'has_dizziness_or_fainting',
            'has_unusual_shortness_of_breath',
            'has_prior_exercise_restrictions', 'exercise_restriction_details',
            'had_recent_surgery_or_injury', 'recent_surgery_details',
            'other_safety_concern',
        ]
        widgets = {
            'pain_or_injury_details': forms.Textarea(attrs={'rows': 2}),
            'medical_condition_details': forms.Textarea(attrs={'rows': 2}),
            'exercise_restriction_details': forms.Textarea(attrs={'rows': 2}),
            'recent_surgery_details': forms.Textarea(attrs={'rows': 2}),
            'other_safety_concern': forms.Textarea(attrs={'rows': 2}),
        }


class LifestyleForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = [
            'wake_time', 'sleep_time', 'sleep_duration_hours',
            'occupation_schedule', 'sedentary_hours_per_day', 'daily_activity_level',
            'meals_per_day', 'meal_schedule_consistency', 'stress_level',
            'schedule_consistency', 'available_workout_windows',
        ]
        widgets = {
            'wake_time': forms.TimeInput(attrs={'type': 'time'}),
            'sleep_time': forms.TimeInput(attrs={'type': 'time'}),
            'available_workout_windows': forms.TextInput(
                attrs={'placeholder': 'e.g. early morning, lunch break, evening'}
            ),
        }


class GoalsForm(forms.ModelForm):
    secondary_goals = forms.MultipleChoiceField(
        choices=Assessment._meta.get_field('primary_goal').choices,
        required=False, widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Assessment
        fields = ['primary_goal', 'secondary_goals']

    def clean_secondary_goals(self):
        return list(self.cleaned_data.get('secondary_goals', []))


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = [
            'training_experience', 'past_training_frequency_per_week', 'past_training_type',
            'time_since_last_trained', 'familiar_exercises', 'reason_stopped',
        ]
        widgets = {
            'past_training_type': forms.TextInput(attrs={'placeholder': 'e.g. running, weightlifting, yoga'}),
            'familiar_exercises': forms.TextInput(attrs={'placeholder': 'e.g. squat, push-up, plank'}),
            'reason_stopped': forms.Textarea(attrs={'rows': 2}),
        }


class FitnessTestForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = [
            'walking_duration_minutes', 'walking_pace', 'stair_tolerance',
            'sit_to_stand_reps_30s', 'squat_variation', 'pushup_variation',
            'plank_hold_seconds', 'mobility_balance_rating', 'perceived_exertion_after_tests',
        ]
        help_texts = {
            'walking_duration_minutes': 'Roughly how many minutes can you walk continuously at a normal pace?',
            'sit_to_stand_reps_30s': 'How many times can you sit-to-stand from a chair in 30 seconds?',
            'plank_hold_seconds': 'How long can you hold a plank (any variation), in seconds?',
            'perceived_exertion_after_tests': 'Rate your effort during these tests, 1 (very easy) to 10 (max effort).',
        }
        widgets = {
            'perceived_exertion_after_tests': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }


class ConstraintsForm(forms.ModelForm):
    EQUIPMENT_CHOICES = [
        ('none', 'No equipment'),
        ('dumbbells', 'Dumbbells'),
        ('barbell', 'Barbell'),
        ('resistance_bands', 'Resistance bands'),
        ('kettlebell', 'Kettlebell'),
        ('pullup_bar', 'Pull-up bar'),
        ('bench', 'Bench'),
        ('full_gym', 'Full gym access'),
        ('cardio_machine', 'Cardio machine (bike/treadmill/rower)'),
    ]
    available_equipment = forms.MultipleChoiceField(
        choices=EQUIPMENT_CHOICES, required=False, widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Assessment
        fields = [
            'training_location', 'available_equipment', 'days_per_week_available',
            'minutes_per_session', 'preferred_workout_time',
            'exercise_preferences', 'exercises_to_avoid',
        ]
        widgets = {
            'days_per_week_available': forms.NumberInput(attrs={'min': 1, 'max': 7}),
            'minutes_per_session': forms.NumberInput(attrs={'min': 10, 'max': 180}),
            'exercise_preferences': forms.TextInput(attrs={'placeholder': 'e.g. bodyweight, walking, cycling'}),
            'exercises_to_avoid': forms.TextInput(attrs={'placeholder': 'e.g. running, overhead pressing'}),
        }

    def clean_available_equipment(self):
        return list(self.cleaned_data.get('available_equipment', []))
