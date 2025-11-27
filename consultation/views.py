from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from doctors.models import Doctor
from poliklinik.models import Poliklinik

from .forms import ConsultationForm, ConsultationMessageForm
from .models import Consultation, ConsultationMessage, MedicalRecord
from .services import generate_chatbot_reply


def _require_patient_access(request):
    if getattr(request.user, "role", None) != "pasien":
        messages.error(request, "Fitur konsultasi online hanya tersedia untuk pasien.")
        return False
    return True


@login_required
def consultation_dashboard(request):
    if not _require_patient_access(request):
        return redirect("home")

    doctor_queryset = Doctor.objects.select_related("user", "poliklinik").order_by(
        "poliklinik__name", "user__first_name", "user__last_name"
    )
    polikliniks = (
        Poliklinik.objects.prefetch_related(
            Prefetch("doctors", queryset=doctor_queryset)
        )
        .all()
        .order_by("name")
    )
    consultations = (
        Consultation.objects.filter(patient=request.user)
        .select_related("doctor", "doctor__user", "doctor__poliklinik")
        .order_by("-created_at")[:5]
    )

    context = {
        "polikliniks": polikliniks,
        "consultations": consultations,
        "account_verified": request.user.is_active,
        "has_doctor": doctor_queryset.exists(),
    }
    return render(request, "consultation/dashboard.html", context)


@login_required
def consultation_list(request):
    if not _require_patient_access(request):
        return redirect("home")
    consultations = (
        Consultation.objects.filter(patient=request.user)
        .select_related("doctor", "doctor__user", "doctor__poliklinik")
        .order_by("-created_at")
    )
    return render(request, "consultation/list.html", {"consultations": consultations})


@login_required
def consultation_create(request):
    if not _require_patient_access(request):
        return redirect("home")

    if request.method == "POST":
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.patient = request.user
            consultation.status = Consultation.STATUS_WAITING
            if consultation.doctor:
                consultation.status = Consultation.STATUS_ACTIVE
            consultation.save()
            messages.success(
                request,
                "Konsultasi berhasil dikirim! Dokter akan meninjau dan merespons melalui chatbot.",
            )
            return redirect("consultation_list")
    else:
        form = ConsultationForm()
    return render(request, "consultation/create.html", {"form": form})


def _get_active_consultation(patient, doctor):
    consultation = (
        Consultation.objects.filter(
            patient=patient,
            doctor=doctor,
            status__in=[Consultation.STATUS_WAITING, Consultation.STATUS_ACTIVE],
        )
        .order_by("-created_at")
        .first()
    )
    if consultation:
        return consultation
    return Consultation.objects.create(
        patient=patient,
        doctor=doctor,
        status=Consultation.STATUS_ACTIVE,
        date=timezone.now().date(),
    )


@login_required
def consultation_chat(request, doctor_id):
    if not _require_patient_access(request):
        return redirect("home")

    doctor = get_object_or_404(
        Doctor.objects.select_related("user", "poliklinik"), pk=doctor_id
    )
    consultation = _get_active_consultation(request.user, doctor)
    messages_qs = consultation.messages.all()

    if request.method == "POST":
        form = ConsultationMessageForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data["message"]
            ConsultationMessage.objects.create(
                consultation=consultation, sender="patient", message=user_message
            )
            bot_reply = generate_chatbot_reply(user_message, doctor)
            ConsultationMessage.objects.create(
                consultation=consultation, sender="bot", message=bot_reply
            )
            if not consultation.complaint:
                consultation.complaint = user_message
            consultation.status = Consultation.STATUS_ACTIVE
            consultation.save(update_fields=["complaint", "status"])
            return redirect("consultation_chat", doctor_id=doctor.id)
    else:
        form = ConsultationMessageForm()

    context = {
        "doctor": doctor,
        "consultation": consultation,
        "messages": messages_qs,
        "form": form,
    }
    return render(request, "consultation/chat.html", context)


@login_required
def medical_record_list(request):
    if not _require_patient_access(request):
        return redirect("home")
    records = MedicalRecord.objects.filter(patient=request.user).order_by("-created_at")
    return render(request, "medical_record/list.html", {"records": records})
