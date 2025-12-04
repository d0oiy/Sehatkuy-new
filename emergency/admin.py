from django.contrib import admin
from .models import EmergencyContact, EmergencyFacility


@admin.register(EmergencyFacility)
class EmergencyFacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "facility_type", "phone_number", "ambulance_number", "emergency_unit")
    list_filter = ("facility_type", "emergency_unit")
    search_fields = ("name", "address", "phone_number", "ambulance_number")


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ("label", "phone_number", "is_24h", "priority")
    list_filter = ("is_24h",)
    ordering = ("priority",)
