from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'sex', 'height_cm', 'weight_kg', 'fitness_level')
    search_fields = ('user__username',)
