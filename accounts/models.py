from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Basic personal information (Section 6, Step 1)."""

    SEX_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )
    age = models.PositiveIntegerField(null=True, blank=True)
    sex = models.CharField(max_length=20, choices=SEX_CHOICES, blank=True)
    height_cm = models.FloatField(null=True, blank=True, help_text='Height in centimeters')
    weight_kg = models.FloatField(null=True, blank=True, help_text='Weight in kilograms')
    waist_cm = models.FloatField(null=True, blank=True, help_text='Optional waist measurement in cm')

    # Denormalized classification, set by the profile builder in planner/
    fitness_level = models.CharField(max_length=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile({self.user.username})"

    @property
    def bmi(self):
        if self.height_cm and self.weight_kg:
            h_m = self.height_cm / 100
            if h_m > 0:
                return round(self.weight_kg / (h_m ** 2), 1)
        return None
