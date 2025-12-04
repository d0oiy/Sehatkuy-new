from django.shortcuts import render
from django.db.models import Count, F
from poliklinik.models import Poliklinik
from doctors.models import Doctor
from appointments.models import AppointmentSlot
from articles.models import Article
from datetime import date

def index(request):
    today = date.today()

    active_doctors = Doctor.objects.filter(user__is_active=True).count()

    # Slot dianggap tersedia jika jumlah appointment di slot tersebut < quota
    available_slots = AppointmentSlot.objects.annotate(
        booked=Count("appointments")
    ).filter(
        date__gte=today,
        booked__lt=F("quota")
    ).count()

    open_poliklinik = [p for p in Poliklinik.objects.all() if p.is_currently_open()]
    open_poli_count = len(open_poliklinik)
    
    # Ambil artikel terbaru untuk ditampilkan di landing page
    latest_articles = Article.objects.filter(is_published=True).order_by('-created_at')[:3]

    return render(request, "home/index.html", {
        "active_doctors": active_doctors,
        "available_slots": available_slots,
        "open_poli_count": open_poli_count,
        "latest_articles": latest_articles,
    })
