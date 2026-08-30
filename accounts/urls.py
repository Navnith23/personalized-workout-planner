from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.PlannerLoginView.as_view(), name='login'),
    path('logout/', views.PlannerLogoutView.as_view(), name='logout'),
]
