from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

from accounts.forms import BasicInfoForm
from .forms import (
    SafetyScreeningForm, LifestyleForm, GoalsForm, ExperienceForm,
    FitnessTestForm, ConstraintsForm,
)
from .models import Assessment
from .services import run_recommendation_engine

STEP_ORDER = ['basic', 'safety', 'lifestyle', 'goals', 'experience', 'fitness', 'constraints']

STEP_LABELS = {
    'basic': 'Basic Information',
    'safety': 'Safety Screening',
    'lifestyle': 'Lifestyle',
    'goals': 'Goals',
    'experience': 'Exercise Experience',
    'fitness': 'Fitness Assessment',
    'constraints': 'Training Constraints',
}


def _get_or_create_in_progress_assessment(user):
    assessment = Assessment.objects.filter(user=user, status='in_progress').first()
    if not assessment:
        assessment = Assessment.objects.create(user=user)
    return assessment


def _step_context(step, user):
    idx = STEP_ORDER.index(step)
    return {
        'step': step,
        'step_label': STEP_LABELS[step],
        'step_number': idx + 1,
        'total_steps': len(STEP_ORDER),
        'progress_pct': round(100 * (idx + 1) / len(STEP_ORDER)),
    }


class BasicInfoStepView(LoginRequiredMixin, View):
    template_name = 'assessment/step_form.html'

    def get(self, request):
        form = BasicInfoForm(instance=request.user.profile)
        ctx = _step_context('basic', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)

    def post(self, request):
        form = BasicInfoForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('assessment:safety')
        ctx = _step_context('basic', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)


class SafetyStepView(LoginRequiredMixin, View):
    template_name = 'assessment/step_form.html'

    def get(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = SafetyScreeningForm(instance=assessment)
        ctx = _step_context('safety', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)

    def post(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = SafetyScreeningForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            return redirect('assessment:lifestyle')
        ctx = _step_context('safety', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)


class LifestyleStepView(LoginRequiredMixin, View):
    template_name = 'assessment/step_form.html'

    def get(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = LifestyleForm(instance=assessment)
        ctx = _step_context('lifestyle', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)

    def post(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = LifestyleForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            return redirect('assessment:goals')
        ctx = _step_context('lifestyle', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)


class GoalsStepView(LoginRequiredMixin, View):
    template_name = 'assessment/step_form.html'

    def get(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = GoalsForm(instance=assessment)
        ctx = _step_context('goals', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)

    def post(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = GoalsForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            return redirect('assessment:experience')
        ctx = _step_context('goals', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)


class ExperienceStepView(LoginRequiredMixin, View):
    template_name = 'assessment/step_form.html'

    def get(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = ExperienceForm(instance=assessment)
        ctx = _step_context('experience', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)

    def post(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = ExperienceForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            return redirect('assessment:fitness')
        ctx = _step_context('experience', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)


class FitnessTestStepView(LoginRequiredMixin, View):
    template_name = 'assessment/step_form.html'

    def get(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = FitnessTestForm(instance=assessment)
        ctx = _step_context('fitness', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)

    def post(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = FitnessTestForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            return redirect('assessment:constraints')
        ctx = _step_context('fitness', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)


class ConstraintsStepView(LoginRequiredMixin, View):
    template_name = 'assessment/step_form.html'

    def get(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = ConstraintsForm(instance=assessment)
        ctx = _step_context('constraints', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)

    def post(self, request):
        assessment = _get_or_create_in_progress_assessment(request.user)
        form = ConstraintsForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            return redirect('assessment:review')
        ctx = _step_context('constraints', request.user)
        ctx['form'] = form
        return render(request, self.template_name, ctx)


@login_required
def review(request):
    assessment = get_object_or_404(Assessment, user=request.user, status='in_progress')
    if request.method == 'POST':
        result = run_recommendation_engine(request.user, assessment)
        if result.blocked:
            return redirect('assessment:blocked', assessment_id=assessment.id)
        messages.success(request, "Your personalized plan is ready.")
        return redirect('programs:plan_detail', program_id=result.program.id)
    return render(request, 'assessment/review.html', {'assessment': assessment})


@login_required
def blocked(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    return render(request, 'assessment/blocked.html', {'assessment': assessment})


@login_required
def dashboard_redirect(request):
    """Entry point after login: send the user to their plan, or start an assessment."""
    from programs.models import Program
    active = Program.objects.filter(user=request.user, is_active=True).first()
    if active:
        return redirect('programs:plan_detail', program_id=active.id)
    in_progress = Assessment.objects.filter(user=request.user, status='in_progress').first()
    if in_progress:
        return redirect('assessment:basic')
    return redirect('assessment:basic')
