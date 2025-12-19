from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from doctors.models import Doctor
from consultation.models import Consultation, ConsultationMessage
from appointments.models import Appointment, AppointmentSlot, Queue
from poliklinik.models import Poliklinik
from datetime import timedelta


def _require_doctor_access(request):
    """Helper untuk memastikan hanya dokter yang bisa akses"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, "Akses ditolak. Fitur ini hanya untuk dokter.")
        return False
    return True


@login_required
def dashboard(request):
    """Dashboard utama dokter dengan statistik dan ringkasan"""
    if not _require_doctor_access(request):
        return redirect("home")
    
    doctor = request.user.doctor_profile
    today = date.today()
    
    # Statistik Konsultasi
    all_consultations = Consultation.objects.filter(doctor=doctor)
    today_consultations = all_consultations.filter(created_at__date=today)
    active_consultations = all_consultations.filter(status=Consultation.STATUS_ACTIVE)
    
    # Pasien Aktif (pasien dengan konsultasi aktif)
    active_patients = all_consultations.filter(
        status__in=[Consultation.STATUS_ACTIVE, Consultation.STATUS_WAITING]
    ).values('patient').distinct().count()
    
    # Janji Temu yang Perlu Ditinjau
    pending_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='pending'
    ).order_by('date', 'time')
    
    # Nomor Antrian Hari Ini
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        date=today,
        status__in=['pending', 'approved']
    ).order_by('queue_number')
    
    # Konsultasi Terbaru (5 terakhir)
    recent_consultations = all_consultations.select_related(
        'patient', 'doctor', 'doctor__user', 'doctor__poliklinik'
    ).order_by('-created_at')[:5]
    
    # Janji Temu Hari Ini
    today_appointments_count = Appointment.objects.filter(
        doctor=doctor,
        date=today,
        status__in=['pending', 'approved']
    ).count()
    
    context = {
        'doctor': doctor,
        'total_consultations': all_consultations.count(),
        'today_consultations': today_consultations.count(),
        'active_consultations': active_consultations.count(),
        'active_patients': active_patients,
        'pending_appointments': pending_appointments[:10],  # 10 teratas
        'today_appointments': today_appointments,
        'today_appointments_count': today_appointments_count,
        'recent_consultations': recent_consultations,
    }
    return render(request, 'doctors/dashboard.html', context)


@login_required
def consultations(request):
    """Daftar semua konsultasi dokter"""
    if not _require_doctor_access(request):
        return redirect("home")
    
    doctor = request.user.doctor_profile
    
    # Filter berdasarkan status
    status_filter = request.GET.get('status', 'all')
    consultations_qs = Consultation.objects.filter(doctor=doctor).select_related(
        'patient', 'doctor', 'doctor__user', 'doctor__poliklinik'
    ).order_by('-created_at')
    
    # Filter berdasarkan pasien (jika ada)
    patient_id = request.GET.get('patient')
    if patient_id:
        consultations_qs = consultations_qs.filter(patient_id=patient_id)
    
    if status_filter == 'active':
        consultations_qs = consultations_qs.filter(status=Consultation.STATUS_ACTIVE)
    elif status_filter == 'waiting':
        consultations_qs = consultations_qs.filter(status=Consultation.STATUS_WAITING)
    elif status_filter == 'done':
        consultations_qs = consultations_qs.filter(status=Consultation.STATUS_DONE)
    
    context = {
        'consultations': consultations_qs,
        'status_filter': status_filter,
        'doctor': doctor,
    }
    return render(request, 'doctors/consultations.html', context)


@login_required
def consultation_detail(request, consultation_id):
    """Detail konsultasi dan chat dengan pasien"""
    if not _require_doctor_access(request):
        return redirect("home")
    
    doctor = request.user.doctor_profile
    consultation = get_object_or_404(
        Consultation.objects.select_related('patient', 'doctor', 'doctor__user', 'doctor__poliklinik'),
        id=consultation_id,
        doctor=doctor
    )
    
    messages_qs = consultation.messages.all().order_by('created_at')
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            ConsultationMessage.objects.create(
                consultation=consultation,
                sender='doctor',
                message=message_text
            )
            # Update status menjadi aktif jika masih menunggu
            if consultation.status == Consultation.STATUS_WAITING:
                consultation.status = Consultation.STATUS_ACTIVE
                consultation.save(update_fields=['status'])
            messages.success(request, "Pesan berhasil dikirim.")
            return redirect('doctors:consultation_detail', consultation_id=consultation.id)
        else:
            messages.error(request, "Pesan tidak boleh kosong.")
    
    context = {
        'consultation': consultation,
        'messages': messages_qs,
        'doctor': doctor,
    }
    return render(request, 'doctors/consultation_detail.html', context)


@login_required
def appointments(request):
    """Daftar janji temu dokter"""
    if not _require_doctor_access(request):
        return redirect("home")
    
    doctor = request.user.doctor_profile
    
    # Filter berdasarkan status
    status_filter = request.GET.get('status', 'all')
    appointments_qs = Appointment.objects.filter(doctor=doctor).select_related(
        'patient', 'doctor', 'poliklinik', 'slot'
    ).order_by('-date', '-time')
    
    if status_filter == 'pending':
        appointments_qs = appointments_qs.filter(status='pending')
    elif status_filter == 'approved':
        appointments_qs = appointments_qs.filter(status='approved')
    elif status_filter == 'cancelled':
        appointments_qs = appointments_qs.filter(status='cancelled')
    elif status_filter == 'today':
        appointments_qs = appointments_qs.filter(date=date.today())
    
    context = {
        'appointments': appointments_qs,
        'status_filter': status_filter,
        'doctor': doctor,
    }
    return render(request, 'doctors/appointments.html', context)


@login_required
def appointment_detail(request, appointment_id):
    """Detail dan aksi untuk janji temu"""
    if not _require_doctor_access(request):
        return redirect("home")
    
    doctor = request.user.doctor_profile
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient', 'doctor', 'poliklinik', 'slot'),
        id=appointment_id,
        doctor=doctor
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            appointment.status = 'approved'
            appointment.save()
            
            # Buat Queue jika belum ada
            if not hasattr(appointment, 'queue'):
                # Hitung nomor antrian berdasarkan appointment yang sudah approved di hari yang sama
                max_queue = Queue.objects.filter(
                    doctor=appointment.doctor,
                    poliklinik=appointment.poliklinik,
                    appointment__date=appointment.date
                ).count()
                
                Queue.objects.create(
                    appointment=appointment,
                    patient=appointment.patient,
                    doctor=appointment.doctor,
                    poliklinik=appointment.poliklinik,
                    queue_number=max_queue + 1,
                    status=Queue.STATUS_WAITING,
                    estimated_wait_time=max_queue * 15  # Estimasi 15 menit per pasien
                )
            
            messages.success(request, f"Janji temu dengan {appointment.patient.get_full_name()} telah disetujui.")
        elif action == 'cancel':
            appointment.status = 'cancelled'
            appointment.save()
            messages.success(request, f"Janji temu dengan {appointment.patient.get_full_name()} telah dibatalkan.")
        return redirect('doctors:appointment_detail', appointment_id=appointment.id)
    
    context = {
        'appointment': appointment,
        'doctor': doctor,
    }
    return render(request, 'doctors/appointment_detail.html', context)


@login_required
def consultation_mark_done(request, consultation_id):
    """Tandai konsultasi sebagai selesai"""
    if not _require_doctor_access(request):
        return redirect("home")
    
    doctor = request.user.doctor_profile
    consultation = get_object_or_404(
        Consultation,
        id=consultation_id,
        doctor=doctor
    )
    
    consultation.status = Consultation.STATUS_DONE
    consultation.save(update_fields=['status'])
    messages.success(request, "Konsultasi telah ditandai sebagai selesai.")
    return redirect('doctors:consultation_detail', consultation_id=consultation.id)


@login_required
def poliklinik_manage(request):
    """Tampilan read-only untuk dokters: informasikan bahwa pengelolaan dilakukan oleh Admin Poliklinik"""
    if not _require_doctor_access(request):
        return redirect("home")
    
    doctor = request.user.doctor_profile
    
    if not doctor.poliklinik:
        messages.error(request, "Anda belum terdaftar di poliklinik manapun.")
        return redirect('doctors:doctor_dashboard')
    
    poliklinik = doctor.poliklinik

    # Dokter tidak boleh mengubah status poliklinik; hanya melihat status
    if request.method == 'POST':
        messages.error(request, "Pengelolaan poliklinik dilakukan oleh Admin Poliklinik. Hubungi admin untuk melakukan perubahan.")
        return redirect('doctors:poliklinik_manage')

    context = {
        'doctor': doctor,
        'poliklinik': poliklinik,
        'is_open': poliklinik.is_currently_open(),
        'can_manage': False,
    }
    return render(request, 'doctors/poliklinik_manage.html', context)


@login_required
def slot_manage(request):
    """Kelola slot janji temu (tambah/kurang)"""
    if not _require_doctor_access(request):
        return redirect("home")
    
    doctor = request.user.doctor_profile
    
    if not doctor.poliklinik:
        messages.error(request, "Anda belum terdaftar di poliklinik manapun.")
        return redirect('doctors:doctor_dashboard')
    
    today = date.today()
    slots = AppointmentSlot.objects.filter(
        doctor=doctor,
        date__gte=today
    ).order_by('date', 'start_time')
    
    if request.method == 'POST':
        # Pengaturan slot dikontrol oleh Admin Poliklinik; dokter tidak dapat menambah/menghapus/mengubah quota.
        messages.error(request, "Perubahan slot tidak diperbolehkan. Slot dikelola oleh Admin Poliklinik dan setiap hari secara default memiliki 10 slot per hari.")
        return redirect('doctors:slot_manage')
    
    context = {
        'doctor': doctor,
        'slots': slots,
        'poliklinik': doctor.poliklinik,
        'today': today,
    }
    return render(request, 'doctors/slot_manage.html', context)


@login_required
def queue_manage(request):
    """Kelola antrian - dokter update nomor antrian dan konfirmasi check in"""
    if not _require_doctor_access(request):
        return redirect("home")
    
    doctor = request.user.doctor_profile
    today = date.today()
    
    # Ambil antrian hari ini
    queues = Queue.objects.filter(
        doctor=doctor,
        appointment__date=today,
        status__in=[Queue.STATUS_WAITING, Queue.STATUS_CHECKED_IN, Queue.STATUS_IN_PROGRESS]
    ).select_related('patient', 'appointment', 'poliklinik').order_by('queue_number')
    
    # Antrian yang sedang dilayani
    current_queue = Queue.objects.filter(
        doctor=doctor,
        appointment__date=today,
        status=Queue.STATUS_IN_PROGRESS
    ).first()
    
    if request.method == 'POST':
        # Dokter tidak memiliki hak untuk memodifikasi antrian; gunakan Admin Poliklinik
        messages.error(request, "Pengelolaan antrian dilakukan oleh Admin Poliklinik. Hubungi admin untuk tindakan ini.")
        return redirect('doctors:queue_manage')
    
    context = {
        'doctor': doctor,
        'queues': queues,
        'current_queue': current_queue,
        'today': today,
    }
    return render(request, 'doctors/queue_manage.html', context)
