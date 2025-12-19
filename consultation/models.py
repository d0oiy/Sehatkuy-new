from django.db import models
from django.conf import settings
from django.utils import timezone
from doctors.models import Doctor


class Consultation(models.Model):
    STATUS_WAITING = "Menunggu"
    STATUS_ACTIVE = "Berlangsung"
    STATUS_DONE = "Selesai"

    STATUS_CHOICES = [
        (STATUS_WAITING, "Menunggu"),
        (STATUS_ACTIVE, "Berlangsung"),
        (STATUS_DONE, "Selesai"),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consultations"
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultations",
    )
    doctor_name = models.CharField(max_length=100, blank=True)
    date = models.DateField(default=timezone.now, blank=True, null=True)
    complaint = models.TextField(blank=True)

    # Payment fields
    from decimal import Decimal
    from django.core.validators import MinValueValidator

    fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50000.00'), validators=[MinValueValidator(Decimal('0.00'))])
    payment_status = models.CharField(max_length=20, choices=[('unpaid','Belum Bayar'), ('pending','Menunggu Konfirmasi'), ('paid','Lunas'), ('failed','Gagal')], default='unpaid')
    payment_proof = models.FileField(upload_to='payments/consultation/', null=True, blank=True)
    payment_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_WAITING)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        doctor_label = self.doctor_name or (self.doctor.user.get_full_name() if self.doctor else "-")
        return f"{self.patient.username} - {doctor_label}"

    def save(self, *args, **kwargs):
        if self.doctor and not self.doctor_name:
            full_name = self.doctor.user.get_full_name()
            self.doctor_name = full_name or self.doctor.user.username
        if not self.date:
            self.date = timezone.now().date()
        super().save(*args, **kwargs)


class ConsultationMessage(models.Model):
    SENDER_CHOICES = [
        ("patient", "Pasien"),
        ("bot", "Chatbot"),
        ("doctor", "Dokter"),
    ]

    consultation = models.ForeignKey(
        Consultation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_sender_display()} - {self.created_at:%d %b %Y %H:%M}"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    consultation = models.ForeignKey(
        "Consultation", on_delete=models.CASCADE, null=True, blank=True
    )
    diagnosis = models.TextField()
    treatment = models.TextField(blank=True, null=True)
    prescription = models.TextField(blank=True, null=True)
    doctor_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rekam Medis {self.patient.username} - {self.created_at.strftime('%d %b %Y')}"
