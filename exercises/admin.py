from django.contrib import admin
from .models import Exercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'exercise_type', 'movement_pattern', 'equipment', 'difficulty', 'is_beginner_safe')
    list_filter = ('exercise_type', 'movement_pattern', 'equipment', 'difficulty', 'is_beginner_safe', 'is_low_impact')
    search_fields = ('name',)
    filter_horizontal = ('progressions',)
