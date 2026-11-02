from django.urls import path
from . import views

app_name = 'referrals'

urlpatterns = [
    path('', views.referral_list, name='referral_list'),
    path('create/', views.referral_create, name='referral_create'),
    path('<int:pk>/', views.referral_detail, name='referral_detail'),
    path('<int:pk>/status/', views.referral_update_status, name='referral_update_status'),
]
