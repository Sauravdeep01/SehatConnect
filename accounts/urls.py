from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('worker-dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('profile/', views.profile_view, name='profile'),
]
