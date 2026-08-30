from django.urls import path
from . import views

app_name = 'programs'

urlpatterns = [
    path('<int:program_id>/', views.plan_detail, name='plan_detail'),
    path('day/<int:day_id>/log/', views.log_workout, name='log_workout'),
]
