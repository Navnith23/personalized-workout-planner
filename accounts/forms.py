from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class BasicInfoForm(forms.ModelForm):
    """Step 1 of the assessment: basic information."""

    class Meta:
        model = Profile
        fields = ['age', 'sex', 'height_cm', 'weight_kg', 'waist_cm']
        widgets = {
            'age': forms.NumberInput(attrs={'min': 10, 'max': 100}),
            'height_cm': forms.NumberInput(attrs={'step': '0.1', 'min': 100, 'max': 250}),
            'weight_kg': forms.NumberInput(attrs={'step': '0.1', 'min': 25, 'max': 300}),
            'waist_cm': forms.NumberInput(attrs={'step': '0.1', 'min': 40, 'max': 200}),
        }
        help_texts = {
            'waist_cm': 'Optional',
            'sex': 'Optional — used only to contextualize results, never required.',
        }
