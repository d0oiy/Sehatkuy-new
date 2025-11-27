from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # User CRUD
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),

    # Doctor CRUD
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/add/', views.doctor_create, name='doctor_create'),
    path('doctors/edit/<int:pk>/', views.doctor_edit, name='doctor_edit'),
    path('doctors/delete/<int:pk>/', views.doctor_delete, name='doctor_delete'),

    # Consultation
    path('consultations/', views.consultation_list, name='consultation_list'),

    # Activity Log
    path('activity-log/', views.activity_log, name='activity_log'),
]
