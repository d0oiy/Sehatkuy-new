from django.urls import path

from . import views

app_name = "laboratory"

urlpatterns = [
    path("", views.lab_home, name="home"),
    path("booking/", views.lab_booking, name="booking"),
    path("booking/<int:service_id>/", views.lab_booking, name="booking_with_service"),
    path("booking/success/<int:booking_id>/", views.lab_booking_success, name="booking_success"),
]

