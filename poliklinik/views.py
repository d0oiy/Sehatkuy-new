from django.shortcuts import render, get_object_or_404
from django.db.models import Count, F
from .models import Poliklinik
from appointments.models import AppointmentSlot
from datetime import date


# ============================
# LIST POLIKLINIK
# ============================
def index(request):
    polikliniks = Poliklinik.objects.all().order_by("name")
    return render(request, "poliklinik/index.html", {
        "polikliniks": polikliniks
    })


# ============================
# DETAIL POLIKLINIK
# ============================
def detail(request, slug):
    poli = get_object_or_404(Poliklinik, slug=slug)

    schedules = poli.schedules.all()
    doctors = poli.doctors.filter(user__is_active=True)

    today = date.today()
    doctor_slots = {}

    for d in doctors:
        doctor_slots[d.id] = (
            AppointmentSlot.objects
            .filter(
                doctor=d,
                date__gte=today
            )
            .annotate(total=Count("appointments"))
            .filter(total__lt=F("quota"))  # slot masih available
            .order_by("date", "start_time")[:5]
        )

    return render(request, "poliklinik/detail.html", {
        "poli": poli,
        "schedules": schedules,
        "doctors": doctors,
        "doctor_slots": doctor_slots,
        "is_open": poli.is_currently_open(),
    })
