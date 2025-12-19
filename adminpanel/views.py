from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from users.models import CustomUser
from doctors.models import Doctor
from consultation.models import Consultation
from pharmacy.models import MedicineOrder
from pharmacy.forms import MedicineForm
from articles.models import Article
from .models import ActivityLog
from .forms import UserForm, DoctorForm
from poliklinik.models import Poliklinik
from appointments.models import AppointmentSlot, Queue
from django.utils import timezone
from datetime import date


def is_admin(user):
    # Admin dashboard accessible to system admins only
    return user.is_superuser or getattr(user, 'role', None) in ('admin', 'admin_sistem')


def is_poliklinik_admin(user):
    return user.is_superuser or getattr(user, 'role', None) in ('admin_poliklinik', 'admin_sistem')


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    form = MedicineForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        medicine = form.save(commit=False)
        medicine.created_by = request.user
        medicine.save()
        messages.success(request, f'Obat "{medicine.name}" berhasil ditambahkan.')
        return redirect('adminpanel:admin_dashboard')

    total_users = CustomUser.objects.count()
    total_doctors = Doctor.objects.count()
    total_patients = CustomUser.objects.filter(role='pasien').count()
    total_consultations = Consultation.objects.count()
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(is_published=True).count()
    recent_consultations = Consultation.objects.select_related('patient').order_by('-date')[:12]
    recent_orders = MedicineOrder.objects.select_related('patient').prefetch_related('items__medicine').order_by('-created_at')[:12]
    recent_articles = Article.objects.select_related('author').order_by('-created_at')[:5]
    activities = ActivityLog.objects.order_by('-timestamp')[:8]

    context = {
        'total_users': total_users,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_consultations': total_consultations,
        'total_articles': total_articles,
        'published_articles': published_articles,
        'activities': activities,
        'recent_consultations': recent_consultations,
        'recent_orders': recent_orders,
        'recent_articles': recent_articles,
        'form': form,
        'title': 'Dashboard Admin',
    }
    return render(request, 'adminpanel/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = CustomUser.objects.all().order_by('-id')
    return render(request, 'adminpanel/user_list.html', {
        'users': users,
        'title': 'Daftar Pengguna'
    })


@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(user=request.user, action="Menambahkan pengguna baru")
            messages.success(request, "Pengguna berhasil ditambahkan.")
            return redirect('adminpanel:user_list')
    else:
        form = UserForm()

    return render(request, 'adminpanel/user_form.html', {
        'form': form,
        'title': 'Tambah Pengguna'
    })


@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    form = UserForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        ActivityLog.objects.create(user=request.user, action=f"Mengedit pengguna {user.username}")
        messages.success(request, "Data pengguna berhasil diperbarui.")
        return redirect('adminpanel:user_list')
    return render(request, 'adminpanel/user_form.html', {'form': form, 'title': 'Edit Pengguna'})


@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        ActivityLog.objects.create(user=request.user, action=f"Menghapus pengguna {user.username}")
        user.delete()
        messages.success(request, "Pengguna berhasil dihapus.")
        return redirect('adminpanel:user_list')
    return render(request, 'adminpanel/confirm_delete.html', {'object': user, 'title': 'Hapus Pengguna'})


@login_required
@user_passes_test(is_poliklinik_admin)
def doctor_list(request):
    doctors = Doctor.objects.select_related('user', 'poliklinik').order_by('-id')
    return render(request, 'adminpanel/doctor_list.html', {'doctors': doctors, 'title': 'Kelola Dokter'})


@login_required
@user_passes_test(is_poliklinik_admin)
def poliklinik_dashboard(request):
    """Dashboard khusus untuk Admin Poliklinik"""
    doctors = Doctor.objects.select_related('user', 'poliklinik').order_by('-id')
    pending_payments = MedicineOrder.objects.filter(payment_status='pending').order_by('-created_at')[:12]
    recent_consultations = Consultation.objects.select_related('patient').order_by('-date')[:12]

    context = {
        'doctors': doctors,
        'pending_payments': pending_payments,
        'recent_consultations': recent_consultations,
        'title': 'Dashboard Admin Poliklinik',
    }
    return render(request, 'adminpanel/poliklinik_dashboard.html', context)


@login_required
@user_passes_test(is_poliklinik_admin)
def poliklinik_manage(request, poliklinik_id):
    poliklinik = get_object_or_404(Poliklinik, pk=poliklinik_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'open':
            poliklinik.force_open = True
            poliklinik.force_close = False
            poliklinik.save(update_fields=['force_open', 'force_close'])
            messages.success(request, f"Poliklinik {poliklinik.name} telah dibuka.")
        elif action == 'close':
            poliklinik.force_open = False
            poliklinik.force_close = True
            poliklinik.save(update_fields=['force_open', 'force_close'])
            messages.success(request, f"Poliklinik {poliklinik.name} telah ditutup.")
        elif action == 'auto':
            poliklinik.force_open = False
            poliklinik.force_close = False
            poliklinik.save(update_fields=['force_open', 'force_close'])
            messages.success(request, f"Poliklinik {poliklinik.name} mengikuti jadwal otomatis.")
        return redirect('adminpanel:poliklinik_manage', poliklinik_id=poliklinik.id)

    context = {'poliklinik': poliklinik, 'is_open': poliklinik.is_currently_open()}
    return render(request, 'adminpanel/poliklinik_manage.html', context)


@login_required
@user_passes_test(is_poliklinik_admin)
def slot_manage(request, poliklinik_id):
    poliklinik = get_object_or_404(Poliklinik, pk=poliklinik_id)
    today = date.today()
    slots = AppointmentSlot.objects.filter(poliklinik=poliklinik, date__gte=today).order_by('date', 'start_time')
    doctors_qs = Doctor.objects.filter(poliklinik=poliklinik).select_related('user')

    if request.method == 'POST':
        action = request.POST.get('action')
        slot_id = request.POST.get('slot_id')
        if action == 'create':
            doctor_id = int(request.POST.get('doctor_id'))
            slot_date = request.POST.get('date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            quota = int(request.POST.get('quota', 10))
            doctor = get_object_or_404(Doctor, pk=doctor_id)
            AppointmentSlot.objects.create(
                doctor=doctor,
                poliklinik=poliklinik,
                date=slot_date,
                start_time=start_time,
                end_time=end_time,
                quota=quota
            )
            messages.success(request, 'Slot janji temu berhasil ditambahkan.')
        elif action == 'delete' and slot_id:
            slot = get_object_or_404(AppointmentSlot, id=slot_id, poliklinik=poliklinik)
            if slot.appointments.exists():
                messages.error(request, 'Slot tidak dapat dihapus karena sudah ada janji temu.')
            else:
                slot.delete()
                messages.success(request, 'Slot berhasil dihapus.')
        elif action == 'update_quota' and slot_id:
            slot = get_object_or_404(AppointmentSlot, id=slot_id, poliklinik=poliklinik)
            new_quota = int(request.POST.get('quota', slot.quota))
            if new_quota < slot.used_quota():
                messages.error(request, 'Quota tidak boleh kurang dari jumlah janji yang sudah ada.')
            else:
                slot.quota = new_quota
                slot.save()
                messages.success(request, 'Quota slot berhasil diupdate.')
        return redirect('adminpanel:poliklinik_slot_manage', poliklinik_id=poliklinik.id)

    context = {'poliklinik': poliklinik, 'slots': slots, 'doctors': doctors_qs, 'today': today}
    return render(request, 'adminpanel/slot_manage.html', context)


@login_required
@user_passes_test(is_poliklinik_admin)
def queue_manage(request, poliklinik_id):
    poliklinik = get_object_or_404(Poliklinik, pk=poliklinik_id)
    today = date.today()
    queues = Queue.objects.filter(poliklinik=poliklinik, appointment__date=today, status__in=[Queue.STATUS_WAITING, Queue.STATUS_CHECKED_IN, Queue.STATUS_IN_PROGRESS]).select_related('patient', 'appointment', 'doctor').order_by('queue_number')
    current_queue = Queue.objects.filter(poliklinik=poliklinik, appointment__date=today, status=Queue.STATUS_IN_PROGRESS).first()

    if request.method == 'POST':
        action = request.POST.get('action')
        queue_id = request.POST.get('queue_id')
        if action == 'next' and queue_id:
            if current_queue:
                current_queue.status = Queue.STATUS_COMPLETED
                current_queue.completed_at = timezone.now()
                current_queue.save()
            next_queue = get_object_or_404(Queue, id=queue_id, poliklinik=poliklinik)
            next_queue.status = Queue.STATUS_IN_PROGRESS
            next_queue.started_at = timezone.now()
            next_queue.save()
            messages.success(request, f"Antrian #{next_queue.queue_number} sekarang sedang dilayani.")
        elif action == 'confirm_checkin' and queue_id:
            queue = get_object_or_404(Queue, id=queue_id, poliklinik=poliklinik)
            if queue.status == Queue.STATUS_WAITING:
                queue.status = Queue.STATUS_CHECKED_IN
                queue.checked_in_at = timezone.now()
                queue.save()
                messages.success(request, f"Check in pasien antrian #{queue.queue_number} dikonfirmasi.")
            else:
                messages.error(request, "Pasien sudah check in sebelumnya.")
        return redirect('adminpanel:poliklinik_queue_manage', poliklinik_id=poliklinik.id)

    context = {'poliklinik': poliklinik, 'queues': queues, 'current_queue': current_queue, 'today': today}
    return render(request, 'adminpanel/queue_manage.html', context)


@login_required
@user_passes_test(is_poliklinik_admin)
def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save(commit=False)
            # ensure user role set to doctor
            if doctor.user:
                doctor.user.role = 'dokter'
                doctor.user.save()
            doctor.save()
            ActivityLog.objects.create(user=request.user, action=f"Menambahkan dokter {doctor.user.username if doctor.user else ''}")
            messages.success(request, "Dokter berhasil ditambahkan.")
            return redirect('adminpanel:doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'adminpanel/doctor_form.html', {'form': form, 'title': 'Tambah Dokter'})


@login_required
@user_passes_test(is_poliklinik_admin)
def doctor_edit(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(user=request.user, action=f"Mengedit dokter {doctor.user.username if doctor.user else ''}")
            messages.success(request, "Data dokter berhasil diperbarui.")
            return redirect('adminpanel:doctor_list')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'adminpanel/doctor_form.html', {'form': form, 'title': 'Edit Dokter'})


@login_required
@user_passes_test(is_poliklinik_admin)
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        ActivityLog.objects.create(user=request.user, action=f"Menghapus dokter {doctor.user.username if doctor.user else ''}")
        messages.success(request, "Dokter berhasil dihapus.")
        return redirect('adminpanel:doctor_list')
    return render(request, 'adminpanel/doctor_confirm_delete.html', {'doctor': doctor, 'title': 'Hapus Dokter'})


@login_required
@user_passes_test(is_admin)
def activity_log(request):
    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')
    return render(request, 'adminpanel/activity_log.html', {'logs': logs, 'title': 'Log Aktivitas'})


@login_required
@user_passes_test(is_admin)
def consultation_list(request):
    consultations = Consultation.objects.select_related('patient').order_by('-date') if 'Consultation' in globals() else []
    return render(request, 'adminpanel/consultation_list.html', {'consultations': consultations, 'title': 'Daftar Konsultasi'})
