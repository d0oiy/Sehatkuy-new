from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('consultations/', views.consultations, name='doctor_consultations'),
]
