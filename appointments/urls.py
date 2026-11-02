from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('book/', views.appointment_book, name='appointment_book'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/print/', views.appointment_print, name='appointment_print'),
    path('<int:pk>/status/<str:new_status>/', views.appointment_status_update, name='appointment_status_update'),
    path('<int:pk>/consultation/', views.appointment_consultation, name='appointment_consultation'),
    path('<int:pk>/reschedule/', views.appointment_reschedule, name='appointment_reschedule'),
    path('api/doctors-by-hospital/<int:hospital_id>/', views.api_doctors_by_hospital, name='api_doctors_by_hospital'),
    path('api/available-slots/', views.api_available_slots, name='api_available_slots'),
]
