from django.urls import path
from . import views

app_name = 'consultation'
urlpatterns = [
    path('create/', views.consultation_create, name='consultation_create'),
    path('list/', views.consultation_list, name='consultation_list'),
    path('medical-records/', views.medical_record_list, name='medical_record_list'),

]
