from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Appointment, AppointmentSlot, Queue
from doctors.models import Doctor
from .forms import AppointmentForm


@login_required
def appointment_create_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    user = request.user

    if not user.birth_date or not user.address:
        messages.error(request, "Lengkapi data diri Anda sebelum membuat janji.")
        return redirect('patient_dashboard')

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
    poliklinik = slot.poliklinik

    # Cek apakah poliklinik buka
    if not poliklinik.is_currently_open():
        messages.error(
            request,
            f"Poliklinik {poliklinik.name} sedang tutup. Silakan cek jadwal operasional terlebih dahulu."
        )
        return redirect("poliklinik:detail", slug=poliklinik.slug)

    # Cek slot tersedia
    if not slot.available():
        messages.error(request, "Slot sudah penuh. Pilih slot lain.")
        return redirect("poliklinik:detail", slug=poliklinik.slug)

    # Jika POST, buat appointment
    if request.method == 'POST':
        # Validasi data pasien sebelum membuat appointment
        if not user.birth_date or not user.address:
            messages.error(request, "Lengkapi data diri Anda (tanggal lahir dan alamat) sebelum membuat janji.")
            form = AppointmentForm(request.POST)
        else:
            form = AppointmentForm(request.POST)
            if form.is_valid():
                # Hitung nomor antrian
                used_numbers = list(slot.available_numbers())
                nomor_antrian = 1
                while nomor_antrian in used_numbers:
                    nomor_antrian += 1

                # Buat appointment baru
                appointment = Appointment.objects.create(
                    patient=user,
                    doctor=doctor,
                    poliklinik=poliklinik,
                    slot=slot,
                    date=slot.date,
                    time=slot.start_time,
                    queue_number=nomor_antrian,
                    reason=form.cleaned_data['reason'] or "Konsultasi kesehatan",
                    status="pending",
                )

                messages.success(request, f"Janji berhasil dibuat di {poliklinik.name}, menunggu konfirmasi dokter.")
                return redirect("appointments:appointment_list")
    else:
        # Tampilkan form konfirmasi
        form = AppointmentForm(initial={'reason': 'Konsultasi kesehatan'})
        # Cek data pasien untuk warning
        if not user.birth_date or not user.address:
            messages.warning(request, "Lengkapi data diri Anda (tanggal lahir dan alamat) sebelum membuat janji temu.")

    context = {
        'slot': slot,
        'doctor': doctor,
        'poliklinik': poliklinik,
        'form': form,
        'user': user,
    }
    return render(request, 'appointments/appointment_confirm.html', context)


@login_required
def appointment_list(request):
    today = date.today()

    # Ambil janji user dengan queue
    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related('doctor', 'doctor__user', 'poliklinik').prefetch_related('queue').order_by("-date", "-time")
    
    # Tambahkan informasi queue untuk setiap appointment
    for appt in appointments:
        # Cek apakah appointment memiliki queue (OneToOneField)
        # Gunakan hasattr untuk cek di Python level
        if hasattr(appt, 'queue'):
            try:
                queue = appt.queue
                appt.has_queue = True
                appt.queue_id = queue.id
            except (Queue.DoesNotExist, AttributeError):
                appt.has_queue = False
                appt.queue_id = None
        else:
            appt.has_queue = False
            appt.queue_id = None

    # Ambil dokter dan slot tersedia
    doctors = Doctor.objects.prefetch_related('slots').all()
    for doctor in doctors:
        doctor.available_slots = doctor.slots.filter(date__gte=today).order_by('date', 'start_time')

    return render(request, "appointments/appointment_list.html", {
        "appointments": appointments,
        "doctors": doctors,
        "today": today,
    })


@login_required
def queue_take(request, appointment_id):
    """Pasien mengambil antrian online"""
    appointment = get_object_or_404(
        Appointment.objects.select_related('doctor', 'poliklinik', 'patient'),
        id=appointment_id,
        patient=request.user,
        status='approved'
    )
    
    # Cek apakah sudah ada queue
    if hasattr(appointment, 'queue'):
        messages.info(request, "Anda sudah memiliki antrian untuk janji temu ini.")
        return redirect('appointments:queue_status', queue_id=appointment.queue.id)
    
    # Hitung nomor antrian
    today_queues = Queue.objects.filter(
        doctor=appointment.doctor,
        poliklinik=appointment.poliklinik,
        appointment__date=appointment.date,
        status__in=[Queue.STATUS_WAITING, Queue.STATUS_CHECKED_IN, Queue.STATUS_IN_PROGRESS]
    ).count()
    
    # Hitung estimasi waktu tunggu (15 menit per pasien)
    estimated_wait = today_queues * 15
    
    # Buat queue
    queue = Queue.objects.create(
        appointment=appointment,
        patient=appointment.patient,
        doctor=appointment.doctor,
        poliklinik=appointment.poliklinik,
        queue_number=today_queues + 1,
        status=Queue.STATUS_WAITING,
        estimated_wait_time=estimated_wait
    )
    
    messages.success(request, f"Antrian berhasil diambil! Nomor antrian Anda: #{queue.queue_number}")
    return redirect('appointments:queue_status', queue_id=queue.id)


@login_required
def queue_status(request, queue_id):
    """Lihat status antrian dengan informasi lengkap"""
    queue = get_object_or_404(
        Queue.objects.select_related('appointment', 'doctor', 'poliklinik', 'patient'),
        id=queue_id,
        patient=request.user
    )
    
    # Hitung sisa antrian
    queues_ahead = Queue.objects.filter(
        doctor=queue.doctor,
        poliklinik=queue.poliklinik,
        appointment__date=queue.appointment.date,
        status__in=[Queue.STATUS_WAITING, Queue.STATUS_CHECKED_IN],
        queue_number__lt=queue.queue_number
    ).count()
    
    # Antrian yang sedang dilayani
    current_queue = Queue.objects.filter(
        doctor=queue.doctor,
        poliklinik=queue.poliklinik,
        appointment__date=queue.appointment.date,
        status=Queue.STATUS_IN_PROGRESS
    ).first()
    
    # Update estimasi waktu tunggu
    queue.estimated_wait_time = queues_ahead * 15
    queue.save(update_fields=['estimated_wait_time'])
    
    context = {
        'queue': queue,
        'queues_ahead': queues_ahead,
        'current_queue': current_queue,
    }
    return render(request, 'appointments/queue_status.html', context)


@login_required
def queue_checkin(request, queue_id):
    """Pasien melakukan check in"""
    queue = get_object_or_404(
        Queue.objects.select_related('appointment', 'doctor', 'poliklinik', 'patient'),
        id=queue_id,
        patient=request.user
    )
    
    if queue.status != Queue.STATUS_WAITING:
        messages.error(request, "Anda sudah check in atau status antrian tidak valid.")
        return redirect('appointments:queue_status', queue_id=queue.id)
    
    # Update status ke checked_in (menunggu konfirmasi dokter)
    queue.status = Queue.STATUS_CHECKED_IN
    queue.checked_in_at = timezone.now()
    queue.save(update_fields=['status', 'checked_in_at'])
    
    messages.success(request, "Check in berhasil! Menunggu konfirmasi dari dokter.")
    return redirect('appointments:queue_status', queue_id=queue.id)
