from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Appointment, AppointmentSlot
from doctors.models import Doctor
from .forms import AppointmentForm


@login_required
def appointment_create_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    user = request.user

    if not user.birth_date or not user.address:
        messages.error(request, "Lengkapi data diri Anda sebelum membuat janji.")
        return redirect('users:profile_edit')

    today = date.today()
    slots = AppointmentSlot.objects.filter(
        doctor=doctor,
        date__gte=today
    ).order_by("date", "start_time")

    return render(request, "appointments/appointment_create.html", {
        "doctor": doctor,
        "slots": slots,
    })


@login_required
def appointment_choose_slot(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)
    user = request.user
    doctor = slot.doctor

    # Cek slot tersedia
    if not slot.available():
        messages.error(request, "Slot sudah penuh. Pilih slot lain.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    # Hitung nomor antrian
    used_numbers = list(slot.available_numbers())
    nomor_antrian = 1
    while nomor_antrian in used_numbers:
        nomor_antrian += 1

    # Buat appointment baru
    Appointment.objects.create(
        patient=user,
        doctor=doctor,
        poliklinik=doctor.poliklinik,
        slot=slot,
        date=slot.date,
        time=slot.start_time,
        queue_number=nomor_antrian,
        status="pending",
    )

    messages.success(request, "Janji berhasil dibuat, menunggu konfirmasi.")
    return redirect("appointments:appointment_list")


@login_required
def appointment_list(request):
    today = date.today()

    # Ambil janji user
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by("-date", "-time")

    # Ambil dokter dan slot tersedia
    doctors = Doctor.objects.prefetch_related('slots').all()
    for doctor in doctors:
        doctor.available_slots = doctor.slots.filter(date__gte=today).order_by('date', 'start_time')

    return render(request, "appointments/appointment_list.html", {
        "appointments": appointments,
        "doctors": doctors,
    })
