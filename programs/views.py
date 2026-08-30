from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Program, WorkoutDay
from progress.models import WorkoutLog


@login_required
def plan_detail(request, program_id):
    program = get_object_or_404(Program, id=program_id, user=request.user)
    days = program.days.prefetch_related('workouts__exercise').all()

    logged_day_ids = set(
        WorkoutLog.objects.filter(user=request.user, day__program=program, completed=True)
        .values_list('day_id', flat=True)
    )

    return render(request, 'planner/plan_detail.html', {
        'program': program,
        'days': days,
        'logged_day_ids': logged_day_ids,
    })


@login_required
def log_workout(request, day_id):
    day = get_object_or_404(WorkoutDay, id=day_id, program__user=request.user)
    if request.method == 'POST':
        completed = request.POST.get('completed', 'true') == 'true'
        WorkoutLog.objects.create(user=request.user, day=day, completed=completed)
        messages.success(request, 'Workout marked ' + ('complete.' if completed else 'skipped.'))
    return redirect('programs:plan_detail', program_id=day.program_id)
