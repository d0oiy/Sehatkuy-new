from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('consultations/', views.consultations, name='consultations'),
    path('consultations/<int:consultation_id>/', views.consultation_detail, name='consultation_detail'),
    path('consultations/<int:consultation_id>/done/', views.consultation_mark_done, name='consultation_mark_done'),
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('poliklinik/manage/', views.poliklinik_manage, name='poliklinik_manage'),
    path('slots/manage/', views.slot_manage, name='slot_manage'),
    path('queue/manage/', views.queue_manage, name='queue_manage'),
]
