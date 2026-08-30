from django.contrib import admin
from .models import Assessment


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'primary_goal', 'experience_level', 'training_phase', 'safety_cleared', 'created_at')
    list_filter = ('status', 'primary_goal', 'experience_level', 'training_phase', 'safety_cleared')
    search_fields = ('user__username',)
