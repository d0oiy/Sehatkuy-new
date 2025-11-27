from django.urls import path
from . import views

app_name = 'consultation'
urlpatterns = [
    path('', views.consultation_dashboard, name='consultation_dashboard'),
    path('create/', views.consultation_create, name='consultation_create'),
    path('list/', views.consultation_list, name='consultation_list'),
    path('chat/<int:doctor_id>/', views.consultation_chat, name='consultation_chat'),
    path('medical-records/', views.medical_record_list, name='medical_record_list'),
]
