from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('hospital/<int:pk>/verify/', views.admin_verify_hospital, name='admin_verify_hospital'),
    path('users/', views.admin_users_list, name='admin_users_list'),
    path('users/<int:pk>/toggle-active/', views.admin_user_toggle_active, name='admin_user_toggle_active'),
]
