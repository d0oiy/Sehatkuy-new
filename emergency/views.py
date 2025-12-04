from django.shortcuts import render

from .models import EmergencyContact, EmergencyFacility


def emergency_dashboard(request):
    hospitals = EmergencyFacility.objects.filter(facility_type=EmergencyFacility.TYPE_HOSPITAL)
    puskesmas = EmergencyFacility.objects.filter(facility_type=EmergencyFacility.TYPE_PUSKESMAS)
    contacts = EmergencyContact.objects.all()

    context = {
        "hospitals": hospitals,
        "puskesmas": puskesmas,
        "contacts": contacts,
    }
    return render(request, "emergency/dashboard.html", context)
