from django.contrib import admin
from .models import Appointment, AppointmentSlot

@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ("doctor", "poliklinik", "date", "start_time", "end_time", "quota")
    list_filter = ("poliklinik", "doctor", "date")
    search_fields = ("doctor__user__username", "doctor__user__first_name")

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "date", "time", "status", "queue_number")
    list_filter = ("status", "doctor", "poliklinik")
    search_fields = ("patient__username", "doctor__user__username")
