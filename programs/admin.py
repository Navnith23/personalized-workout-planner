from django.contrib import admin
from .models import Program, WorkoutDay, Workout


class WorkoutInline(admin.TabularInline):
    model = Workout
    extra = 0


class WorkoutDayInline(admin.TabularInline):
    model = WorkoutDay
    extra = 0
    show_change_link = True


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'phase', 'days_per_week', 'week_number', 'is_active', 'created_at')
    list_filter = ('phase', 'is_active')
    inlines = [WorkoutDayInline]


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    list_display = ('program', 'day_index', 'label', 'day_type')
    inlines = [WorkoutInline]


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('day', 'exercise', 'section', 'sets', 'reps', 'duration_seconds')
