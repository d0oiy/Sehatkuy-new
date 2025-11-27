from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from users.models import CustomUser
from doctors.models import Doctor
<<<<<<< HEAD
from consultation.models import Consultation  # ← pastikan model Consultation sudah ada
from pharmacy.models import MedicineOrder
from pharmacy.forms import MedicineForm
=======
from consultation.models import Consultation
>>>>>>> b0efa40 (update konsultasi)
from .models import ActivityLog
from .forms import UserForm, DoctorForm


def is_admin(user):
    return user.is_superuser or getattr(user, 'role', None) == 'admin'


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Handle medicine form submission
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.created_by = request.user
            medicine.save()
            messages.success(request, f'Obat "{medicine.name}" berhasil ditambahkan.')
            return redirect('adminpanel:admin_dashboard')
    else:
        form = MedicineForm()
    
    total_users = CustomUser.objects.count()
    total_doctors = Doctor.objects.count()
<<<<<<< HEAD
    total_consultations = Consultation.objects.count() if 'consultations' in globals() else 0
    total_patients = CustomUser.objects.filter(role='pasien').count()
    recent_consultations = Consultation.objects.select_related('patient').order_by('-date')[:12]
    recent_orders = MedicineOrder.objects.select_related('patient').prefetch_related('items__medicine').order_by('-created_at')[:12]
    activities = ActivityLog.objects.order_by('-timestamp')[:5]
=======
    total_consultations = Consultation.objects.count() if 'Consultation' in globals() else 0
    activity_logs = ActivityLog.objects.order_by('-timestamp')[:8]
>>>>>>> b0efa40 (update konsultasi)

    return render(request, 'adminpanel/dashboard.html', {
        'total_users': total_users,
        'total_doctors': total_doctors,
        'total_consultations': total_consultations,
<<<<<<< HEAD
        'total_patients': total_patients,
        'activities': activities,
        'recent_consultations': recent_consultations,
        'recent_orders': recent_orders,
        'form': form,
    }
    return render(request, 'adminpanel/dashboard.html', context)
=======
        'activity_logs': activity_logs,
        'title': 'Dashboard Admin'
    })
>>>>>>> b0efa40 (update konsultasi)


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
            return redirect('user_list')
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
        return redirect('user_list')
    return render(request, 'adminpanel/user_form.html', {'form': form, 'title': 'Edit Pengguna'})


@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        ActivityLog.objects.create(user=request.user, action=f"Menghapus pengguna {user.username}")
        user.delete()
        messages.success(request, "Pengguna berhasil dihapus.")
        return redirect('user_list')
    return render(request, 'adminpanel/confirm_delete.html', {'object': user, 'title': 'Hapus Pengguna'})


@login_required
@user_passes_test(is_admin)
def doctor_list(request):
    doctors = Doctor.objects.select_related('user', 'poliklinik').order_by('-id')
    return render(request, 'adminpanel/doctor_list.html', {'doctors': doctors, 'title': 'Kelola Dokter'})


@login_required
@user_passes_test(is_admin)
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
            return redirect('doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'adminpanel/doctor_form.html', {'form': form, 'title': 'Tambah Dokter'})


@login_required
@user_passes_test(is_admin)
def doctor_edit(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(user=request.user, action=f"Mengedit dokter {doctor.user.username if doctor.user else ''}")
            messages.success(request, "Data dokter berhasil diperbarui.")
            return redirect('doctor_list')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'adminpanel/doctor_form.html', {'form': form, 'title': 'Edit Dokter'})


@login_required
@user_passes_test(is_admin)
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        ActivityLog.objects.create(user=request.user, action=f"Menghapus dokter {doctor.user.username if doctor.user else ''}")
        messages.success(request, "Dokter berhasil dihapus.")
        return redirect('doctor_list')
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
