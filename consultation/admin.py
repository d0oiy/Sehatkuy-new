from django.contrib import admin

from .models import Consultation, ConsultationMessage, MedicalRecord


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "doctor_name",
        "status",
        "created_at",
    )
    list_filter = ("status", "doctor__poliklinik")
    search_fields = ("patient__username", "doctor_name", "complaint")
    autocomplete_fields = ("patient", "doctor")


@admin.register(ConsultationMessage)
class ConsultationMessageAdmin(admin.ModelAdmin):
    list_display = ("consultation", "sender", "created_at")
    list_filter = ("sender",)
    search_fields = ("consultation__patient__username", "message")


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("patient", "consultation", "created_at")
    search_fields = ("patient__username", "diagnosis")
    autocomplete_fields = ("patient", "consultation")
