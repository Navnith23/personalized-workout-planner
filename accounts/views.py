from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from .forms import SignUpForm


class SignUpView(View):
    template_name = 'accounts/signup.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('assessment:dashboard_redirect')
        return render(request, self.template_name, {'form': SignUpForm()})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('assessment:basic')
        return render(request, self.template_name, {'form': form})


class PlannerLoginView(LoginView):
    template_name = 'accounts/login.html'


class PlannerLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
