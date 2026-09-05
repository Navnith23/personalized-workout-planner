from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from programs.models import Program
from planner.progression import decide_progression, apply_progression, maybe_promote_phase, STOP_AND_REFER
from ml_models.predictor import ml_progression_hint, check_recovery_flag
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
                promoted = maybe_promote_phase(program, decision)
                if promoted:
                    program = Program.objects.get(user=request.user, is_active=True)
                    messages.success(request, "Great progress — you've graduated to the next training phase!")

            messages.success(request, decision.notes)

            profile = getattr(request.user, 'profile', None)
            if profile and profile.bmi:
                hint = ml_progression_hint(
                    stated_tier_label=profile.fitness_level,
                    workout_frequency=program.days_per_week,
                    bmi=profile.bmi,
                )
                if hint:
                    messages.info(request, hint)

            if checkin.resting_bpm and checkin.avg_workout_bpm:
                if check_recovery_flag(checkin.resting_bpm, checkin.avg_workout_bpm):
                    messages.info(
                        request,
                        "Your heart rate pattern this week looks a bit unusual compared to typical "
                        "training data — consider prioritizing extra rest. This isn't a diagnosis, "
                        "just a pattern flag."
                    )

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
