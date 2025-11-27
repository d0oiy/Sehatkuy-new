from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("new/<int:doctor_id>/", views.appointment_create_doctor, name="appointment_create_doctor"),
    path("list/", views.appointment_list, name="appointment_list"),
    path("slot/<int:slot_id>/", views.appointment_choose_slot, name="appointment_choose_slot"),
]
