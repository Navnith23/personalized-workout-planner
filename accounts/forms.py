from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Profile

# Must match planner.profile_builder.AGE_MINIMUM
_AGE_MINIMUM = 16


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Required. Used for password reset.',
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError('Email address is required.')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email.lower()


class BasicInfoForm(forms.ModelForm):
    """Step 1 of the assessment: basic information."""

    class Meta:
        model = Profile
        fields = ['age', 'sex', 'height_cm', 'weight_kg', 'waist_cm']
        widgets = {
            # Server-side clean_age below enforces AGE_MINIMUM; widget attr is a UX hint only.
            'age':       forms.NumberInput(attrs={'min': _AGE_MINIMUM, 'max': 100}),
            'height_cm': forms.NumberInput(attrs={'step': '0.1', 'min': 100, 'max': 250}),
            'weight_kg': forms.NumberInput(attrs={'step': '0.1', 'min': 25,  'max': 300}),
            'waist_cm':  forms.NumberInput(attrs={'step': '0.1', 'min': 40,  'max': 200}),
        }
        help_texts = {
            'waist_cm': 'Optional',
            'sex': 'Optional — used only to contextualize results, never required.',
        }

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None:
            if age < _AGE_MINIMUM:
                raise ValidationError(
                    f"This planner is designed for users aged {_AGE_MINIMUM} and over. "
                    "If you are under {_AGE_MINIMUM}, please seek guidance from a qualified "
                    "fitness professional or your doctor."
                )
            if age > 120:
                raise ValidationError("Please enter a valid age.")
        return age

    def clean_height_cm(self):
        v = self.cleaned_data.get('height_cm')
        if v is not None and not (100 <= v <= 250):
            raise ValidationError('Height must be between 100 cm and 250 cm.')
        return v

    def clean_weight_kg(self):
        v = self.cleaned_data.get('weight_kg')
        if v is not None and not (25 <= v <= 300):
            raise ValidationError('Weight must be between 25 kg and 300 kg.')
        return v
