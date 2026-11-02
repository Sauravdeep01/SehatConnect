from django.urls import path
from . import views

app_name = 'hospitals'

urlpatterns = [
    path('', views.hospital_list, name='hospital_list'),
    path('map/', views.hospital_map, name='hospital_map'),
    path('<int:pk>/', views.hospital_detail, name='hospital_detail'),
    path('<int:pk>/services/update/', views.hospital_services_update, name='hospital_services_update'),
    path('api/markers/', views.api_hospitals_json, name='api_hospitals_json'),
    path('create/', views.admin_hospital_create, name='hospital_create'),
    path('<int:pk>/edit/', views.admin_hospital_edit, name='hospital_edit'),
]
