from django.contrib import admin

from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("__str__", "poliklinik", "email", "phone")
    search_fields = ("user__username", "user__first_name", "user__last_name", "specialization")
    list_filter = ("poliklinik",)
    autocomplete_fields = ("user", "poliklinik")
