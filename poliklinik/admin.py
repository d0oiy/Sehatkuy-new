from django.contrib import admin
from .models import Poliklinik, Schedule

# Admin actions
@admin.action(description="Force OPEN poliklinik")
def force_open(modeladmin, request, queryset):
    queryset.update(force_open=True, force_close=False)

@admin.action(description="Force CLOSE poliklinik")
def force_close(modeladmin, request, queryset):
    queryset.update(force_open=False, force_close=True)

# Poliklinik Admin
@admin.register(Poliklinik)
class PoliklinikAdmin(admin.ModelAdmin):
    list_display = ("name", "force_open", "force_close", "status_now")
    actions = [force_open, force_close]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")

    def status_now(self, obj):
        return "BUKA" if obj.is_currently_open() else "Tutup"


# Schedule Admin
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("poliklinik", "day", "start_time", "end_time", "is_active")
    list_filter = ("poliklinik", "day")
