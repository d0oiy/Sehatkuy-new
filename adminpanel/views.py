from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import CustomUser
from doctors.models import Doctor
from consultation.models import Consultation  # ← pastikan model Consultation sudah ada
from .models import ActivityLog
from .forms import UserForm, DoctorForm

# =====================================================
# Fungsi pengecekan role admin
# =====================================================
def is_admin(user):
    return user.is_superuser or getattr(user, 'role', None) == 'admin'


# =====================================================
# Dashboard Admin
# =====================================================
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = CustomUser.objects.count()
    total_doctors = Doctor.objects.count()
    total_consultations = Consultation.objects.count() if 'consultations' in globals() else 0
    activities = ActivityLog.objects.order_by('-timestamp')[:5]

    context = {
        'title': 'Dashboard Admin',
        'total_users': total_users,
        'total_doctors': total_doctors,
        'total_consultations': total_consultations,
        'activities': activities,
    }
    return render(request, 'adminpanel/dashboard.html', context)


# =====================================================
# USER CRUD
# =====================================================
@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = CustomUser.objects.all().order_by('-id')
    return render(request, 'adminpanel/user_list.html', {'users': users, 'title': 'Daftar Pengguna'})


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
    return render(request, 'adminpanel/user_form.html', {'form': form, 'title': 'Tambah Pengguna'})


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


# =====================================================
# DOCTOR CRUD
# =====================================================
@login_required
@user_passes_test(is_admin)
def doctor_list(request):
    doctors = Doctor.objects.select_related('user').all().order_by('-id')
    return render(request, 'adminpanel/doctor_list.html', {'doctors': doctors, 'title': 'Daftar Dokter'})


@login_required
@user_passes_test(is_admin)
def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save(commit=False)
            # pastikan user dokter otomatis diset role 'doctor'
            if doctor.user:
                doctor.user.role = 'doctor'
                doctor.user.save()
            doctor.save()
            ActivityLog.objects.create(user=request.user, action=f"Menambahkan dokter {doctor.user.username}")
            messages.success(request, "Dokter berhasil ditambahkan.")
            return redirect('doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'adminpanel/doctor_form.html', {'form': form, 'title': 'Tambah Dokter'})


@login_required
@user_passes_test(is_admin)
def doctor_edit(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    form = DoctorForm(request.POST or None, instance=doctor)
    if request.method == 'POST' and form.is_valid():
        form.save()
        ActivityLog.objects.create(user=request.user, action=f"Mengedit data dokter {doctor.user.username}")
        messages.success(request, "Data dokter berhasil diperbarui.")
        return redirect('doctor_list')
    return render(request, 'adminpanel/doctor_form.html', {'form': form, 'title': 'Edit Dokter'})


@login_required
@user_passes_test(is_admin)
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        ActivityLog.objects.create(user=request.user, action=f"Menghapus dokter {doctor.user.username}")
        doctor.delete()
        messages.success(request, "Dokter berhasil dihapus.")
        return redirect('doctor_list')
    return render(request, 'adminpanel/confirm_delete.html', {'object': doctor, 'title': 'Hapus Dokter'})


# =====================================================
# ACTIVITY LOG LIST
# =====================================================
@login_required
@user_passes_test(is_admin)
def activity_log(request):
    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')
    return render(request, 'adminpanel/activity_log.html', {'logs': logs, 'title': 'Log Aktivitas'})


# =====================================================
# CONSULTATION LIST
# =====================================================
@login_required
@user_passes_test(is_admin)
def consultation_list(request):
    consultations = (
        Consultation.objects
        .select_related('patient')  # hanya patient yang ForeignKey
        .all()
        .order_by('-date')
    )

    return render(request, 'adminpanel/consultation_list.html', {
        'consultations': consultations,
        'title': 'Daftar Konsultasi',
    })

