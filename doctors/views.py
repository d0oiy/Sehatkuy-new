from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# ================================
#   Dashboard Dokter
# ================================
@login_required
def dashboard(request):
    return render(request, 'doctors/dashboard.html')


# ================================
#   Konsultasi Dokter (opsional)
# ================================
@login_required
def consultations(request):
    """
    View dummy untuk menghindari error 'NoReverseMatch'
    Bisa diisi data konsultasi dokter nanti.
    """
    return render(request, 'doctors/consultations.html')
