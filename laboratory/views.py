from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LabBookingForm
from .models import LabBooking, LabService


def lab_home(request):
    services = LabService.objects.filter(is_active=True)
    grouped = {}
    for service in services:
        grouped.setdefault(service.category, []).append(service)

    featured = services.filter(is_package=True)[:3]
    quick_services = services.order_by("price")[:6]

    context = {
        "grouped_services": grouped,
        "featured_packages": featured,
        "quick_services": quick_services,
    }
    return render(request, "laboratory/home.html", context)


@login_required
def lab_booking(request, service_id=None):
    service = None
    if service_id:
        service = get_object_or_404(LabService, pk=service_id, is_active=True)

    if request.method == "POST":
        form = LabBookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.patient = request.user
            booking.status = LabBooking.STATUS_PENDING
            booking.save()
            messages.success(
                request,
                "Permintaan booking lab berhasil dikirim. Tim kami akan menghubungi Anda.",
            )
            return redirect("laboratory:booking_success", booking_id=booking.id)
    else:
        initial = {"service": service.id} if service else {}
        form = LabBookingForm(user=request.user, initial=initial)

    return render(
        request,
        "laboratory/booking_form.html",
        {
            "form": form,
            "selected_service": service,
        },
    )


@login_required
def lab_booking_success(request, booking_id):
    booking = get_object_or_404(LabBooking, pk=booking_id, patient=request.user)
    return render(
        request,
        "laboratory/booking_success.html",
        {"booking": booking},
    )
