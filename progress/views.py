from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from programs.models import Program
from planner.progression import decide_progression, apply_progression, STOP_AND_REFER
from .forms import CheckInForm
from .models import CheckIn, WorkoutLog


@login_required
def weekly_checkin(request):
    program = Program.objects.filter(user=request.user, is_active=True).first()
    if not program:
        messages.info(request, "You don't have an active plan yet.")
        return redirect('assessment:dashboard_redirect')

    if request.method == 'POST':
        form = CheckInForm(request.POST)
        if form.is_valid():
            checkin = form.save(commit=False)
            checkin.user = request.user
            checkin.program = program
            checkin.week_number = program.week_number
            decision = decide_progression(checkin)
            checkin.recommendation = decision.action
            checkin.recommendation_notes = decision.notes
            checkin.save()

            if decision.action != STOP_AND_REFER:
                apply_progression(program, decision)

            messages.success(request, decision.notes)
            return redirect('programs:plan_detail', program_id=program.id)
    else:
        completed_count = WorkoutLog.objects.filter(
            user=request.user, day__program=program, completed=True
        ).count()
        form = CheckInForm(initial={
            'planned_sessions': program.days_per_week,
            'completed_sessions': completed_count,
        })

    return render(request, 'progress/checkin_form.html', {'form': form, 'program': program})


@login_required
def history(request):
    checkins = CheckIn.objects.filter(user=request.user)
    logs = WorkoutLog.objects.filter(user=request.user).select_related('day__program')
    return render(request, 'progress/history.html', {'checkins': checkins, 'logs': logs})
