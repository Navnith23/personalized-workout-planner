from django.urls import path
from . import views

app_name = 'progress_history'

urlpatterns = [
    path('', views.history, name='history'),
]
