from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('', views.weekly_checkin, name='checkin'),
]
