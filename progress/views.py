from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect

from programs.models import Program
from planner.progression import decide_progression, apply_progression, maybe_promote_phase, STOP_AND_REFER
from .forms import CheckInForm
from .models import CheckIn, WorkoutLog


@login_required
def weekly_checkin(request):
    program = Program.objects.filter(user=request.user, is_active=True).first()
    if not program:
        messages.info(request, "You don't have an active plan yet.")
        return redirect('assessment:dashboard_redirect')

    # ---- Rate-limit: one check-in per program-week ----
    already_checked_in = CheckIn.objects.filter(
        user=request.user,
        program=program,
        week_number=program.week_number,
    ).exists()
    if already_checked_in:
        messages.warning(
            request,
            f"You've already submitted your week {program.week_number} check-in. "
            "Come back next week!"
        )
        return redirect('programs:plan_detail', program_id=program.id)

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

            try:
                checkin.save()
            except IntegrityError:
                # Race condition — second submission arrived simultaneously.
                messages.warning(
                    request,
                    f"You've already submitted your week {program.week_number} check-in."
                )
                return redirect('programs:plan_detail', program_id=program.id)

            if decision.action != STOP_AND_REFER:
                apply_progression(program, decision)
                promoted = maybe_promote_phase(program, decision)
                if promoted:
                    program = Program.objects.get(user=request.user, is_active=True)
                    messages.success(request, "Great progress — you've graduated to the next training phase!")

            messages.success(request, decision.notes)

            return redirect('programs:plan_detail', program_id=program.id)
    else:
        # Pre-fill completed_sessions: count *distinct days* logged this week
        # (not raw log rows, so logging the same day twice doesn't inflate the count).
        completed_count = (
            WorkoutLog.objects
            .filter(user=request.user, day__program=program, completed=True)
            .values('day_id')
            .distinct()
            .count()
        )
        # Cap at the program's scheduled days so the prefill is always ≤ planned.
        completed_count = min(completed_count, program.days_per_week)
        form = CheckInForm(initial={
            'planned_sessions': program.days_per_week,
            'completed_sessions': completed_count,
        })

    return render(request, 'progress/checkin_form.html', {
        'form': form,
        'program': program,
        'already_checked_in': already_checked_in,
    })


@login_required
def history(request):
    checkins = CheckIn.objects.filter(user=request.user)
    logs = WorkoutLog.objects.filter(user=request.user).select_related('day__program')
    return render(request, 'progress/history.html', {'checkins': checkins, 'logs': logs})
