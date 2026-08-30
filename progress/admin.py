from django.contrib import admin
from .models import WorkoutLog, CheckIn


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'day', 'completed', 'completed_at')
    list_filter = ('completed',)


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'week_number', 'completion_rate', 'difficulty', 'recovery', 'recommendation', 'created_at')
    list_filter = ('recommendation', 'pain_flag')
