from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from consultation.models import Consultation
from appointments.models import Appointment
from pharmacy.models import MedicineOrder, Medicine
from pharmacy.forms import MedicineForm
from django.utils import timezone


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
            return redirect('doctor_dashboard')
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


# 🧩 LOGOUT VIEW
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Anda berhasil logout.')
    return redirect('login')


# 🩺 DASHBOARD PASIEN
@login_required
def patient_dashboard(request):
    if request.user.role != 'pasien':
        messages.error(request, 'Akses ditolak.')
        return redirect('login')
    # Ambil data konsultasi, janji temu, dan pesanan pasien
    consultations = Consultation.objects.filter(patient=request.user).order_by('-date')[:8]
    appointments = Appointment.objects.filter(patient=request.user).order_by('-date')[:8]
    orders = MedicineOrder.objects.filter(patient=request.user).order_by('-created_at')[:8]

    context = {
        'consultations': consultations,
        'appointments': appointments,
        'orders': orders,
    }
    return render(request, 'users/patient_dashboard.html', context)


# 👨‍⚕️ DASHBOARD DOKTER
@login_required
def doctor_dashboard(request):
    if request.user.role != 'dokter':
        messages.error(request, 'Akses ditolak.')
        return redirect('login')
    # Tampilkan konsultasi yang terkait dengan dokter ini
    name_key = request.user.username
    consultations = Consultation.objects.filter(doctor_name__icontains=name_key).order_by('-date')[:12]
    # Tampilkan pesanan yang berkaitan dengan pasien dokter ini (jangan menampilkan semua pesanan)
    patient_ids = consultations.values_list('patient_id', flat=True).distinct()
    orders = MedicineOrder.objects.filter(patient_id__in=patient_ids).order_by('-created_at')[:12]
    context = {
        'consultations': consultations,
        'orders': orders,
    }
    return render(request, 'users/doctor_dashboard.html', context)


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

