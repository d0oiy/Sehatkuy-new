from django.contrib import admin
from .models import LabService, LabBooking


@admin.register(LabService)
class LabServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_package", "is_active")
    list_filter = ("category", "is_package", "is_active")
    search_fields = ("name", "description", "included_tests")
    list_editable = ("is_active",)


@admin.register(LabBooking)
class LabBookingAdmin(admin.ModelAdmin):
    list_display = ("patient", "service", "preferred_date", "preferred_time", "status")
    list_filter = ("status", "preferred_date")
    search_fields = ("patient__username", "patient__email", "service__name")
    autocomplete_fields = ("patient", "service")
