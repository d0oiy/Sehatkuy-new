from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .forms import ProfileEditForm
from consultation.models import Consultation
from appointments.models import Appointment, Queue
from pharmacy.models import MedicineOrder, Medicine
from pharmacy.forms import MedicineForm
from django.utils import timezone
from datetime import date


# 🧩 REGISTER VIEW
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        # Validasi input sederhana
        if not username or not email or not password:
            messages.error(request, 'Semua kolom harus diisi!')
            return redirect('register')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah digunakan.')
            return redirect('register')

        # Buat user baru
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )
        user.save()
        messages.success(request, 'Akun berhasil dibuat! Silakan login.')
        return redirect('login')

    return render(request, 'users/register.html')


# 🧩 LOGIN VIEW (bisa pakai email atau username)
def login_view(request):
    # 🔹 Kalau user sudah login, langsung arahkan ke dashboard sesuai role
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'dokter':
            return redirect('doctors:doctor_dashboard')
        elif request.user.role == 'pasien':
            return redirect('patient_dashboard')
        else:
            return redirect('home')

    if request.method == 'POST':
        input_username = request.POST.get('username')
        password = request.POST.get('password')
        User = get_user_model()

        # 🔹 Jika input berupa email, ubah ke username
        if '@' in input_username:
            try:
                user_obj = User.objects.get(email=input_username)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, 'Email tidak ditemukan.')
                return render(request, 'users/login.html')
        else:
            username = input_username

        # 🔹 Autentikasi user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # 🔹 Redirect sesuai role user
            if user.is_superuser or user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'dokter':
                return redirect('doctor_dashboard')
            elif user.role == 'pasien':
                return redirect('patient_dashboard')
            else:
                logout(request)
                messages.error(request, 'Role tidak dikenali.')
                return redirect('login')
        else:
            messages.error(request, 'Username atau password salah.')

    return render(request, 'users/login.html')



# 🩺 DASHBOARD PASIEN
@login_required
def patient_dashboard(request):
    if request.user.role != 'pasien':
        messages.error(request, 'Akses ditolak.')
        return redirect('login')
    
    # Ambil data konsultasi, janji temu, dan pesanan pasien
    consultations = Consultation.objects.filter(
        patient=request.user
    ).select_related('doctor', 'doctor__user', 'doctor__poliklinik').order_by('-created_at')[:8]
    
    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related('doctor', 'doctor__user', 'poliklinik').order_by('-date', '-time')[:8]
    
    orders = MedicineOrder.objects.filter(
        patient=request.user
    ).order_by('-created_at')[:8]

    # Statistik
    total_consultations = Consultation.objects.filter(patient=request.user).count()
    total_appointments = Appointment.objects.filter(patient=request.user).count()
    total_orders = MedicineOrder.objects.filter(patient=request.user).count()
    approved_appointments = Appointment.objects.filter(
        patient=request.user, 
        status='approved'
    ).count()
    
    # Ambil antrian aktif hari ini
    today = date.today()
    active_queues = Queue.objects.filter(
        patient=request.user,
        appointment__date=today,
        status__in=[Queue.STATUS_WAITING, Queue.STATUS_CHECKED_IN, Queue.STATUS_IN_PROGRESS]
    ).select_related('appointment', 'doctor', 'poliklinik').order_by('queue_number')

    context = {
        'consultations': consultations,
        'appointments': appointments,
        'orders': orders,
        'total_consultations': total_consultations,
        'total_appointments': total_appointments,
        'total_orders': total_orders,
        'approved_appointments': approved_appointments,
        'active_queues': active_queues,
        'today': today,
    }
    return render(request, 'users/patient_dashboard.html', context)


# 👨‍⚕️ DASHBOARD DOKTER (Legacy - redirect ke doctors app)
@login_required
def doctor_dashboard(request):
    if request.user.role != 'dokter':
        messages.error(request, 'Akses ditolak.')
        return redirect('login')
    # Redirect ke dashboard dokter yang baru
    return redirect('doctors:doctor_dashboard')


# 🧑‍💼 DASHBOARD ADMIN
@login_required
def admin_dashboard(request):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Akses ditolak.')
        return redirect('login')

    # Handle medicine form submission
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.created_by = request.user
            medicine.save()
            messages.success(request, f'Obat "{medicine.name}" berhasil ditambahkan.')
            return redirect('admin_dashboard')
    else:
        form = MedicineForm()

    # Ambil data statistik
    total_users = CustomUser.objects.count()
    total_patients = CustomUser.objects.filter(role='pasien').count()
    total_doctors = CustomUser.objects.filter(role='dokter').count()
    total_consultations = Consultation.objects.count()
    
    # Ambil konsultasi terbaru untuk admin view
    recent_consultations = Consultation.objects.order_by('-date')[:12]
    
    # Tambahkan statistik pesanan untuk admin
    total_orders = MedicineOrder.objects.count()
    recent_orders = MedicineOrder.objects.order_by('-created_at')[:12]

    context = {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_consultations': total_consultations,
        'consultations': recent_consultations,
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'form': form,
    }

    return render(request, 'users/admin_dashboard.html', context)


# ✏️ EDIT PROFIL USER
@login_required
def profile_edit(request):
    """Halaman edit profil untuk semua user"""
    user = request.user
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil diperbarui!')
            
            # Redirect sesuai role
            if user.role == 'pasien':
                return redirect('patient_dashboard')
            elif user.role == 'dokter':
                return redirect('doctors:doctor_dashboard')
            elif user.role == 'admin' or user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Terdapat kesalahan dalam form. Silakan periksa kembali.')
    else:
        form = ProfileEditForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'users/profile_edit.html', context)

