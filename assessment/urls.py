from django.urls import path
from . import views

app_name = 'assessment'

urlpatterns = [
    path('basic/', views.BasicInfoStepView.as_view(), name='basic'),
    path('safety/', views.SafetyStepView.as_view(), name='safety'),
    path('lifestyle/', views.LifestyleStepView.as_view(), name='lifestyle'),
    path('goals/', views.GoalsStepView.as_view(), name='goals'),
    path('experience/', views.ExperienceStepView.as_view(), name='experience'),
    path('fitness/', views.FitnessTestStepView.as_view(), name='fitness'),
    path('constraints/', views.ConstraintsStepView.as_view(), name='constraints'),
    path('review/', views.review, name='review'),
    path('blocked/<int:assessment_id>/', views.blocked, name='blocked'),
    path('start/', views.dashboard_redirect, name='dashboard_redirect'),
]
