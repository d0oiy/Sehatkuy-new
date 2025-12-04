from django.conf import settings
from django.db import models
from django.utils import timezone


class LabService(models.Model):
    CATEGORY_General = "general"
    CATEGORY_WOMEN = "women"
    CATEGORY_CHILD = "child"
    CATEGORY_HEART = "heart"
    CATEGORY_IMMUNITY = "immunity"

    CATEGORY_CHOICES = [
        (CATEGORY_General, "Paket Pemeriksaan Umum"),
        (CATEGORY_WOMEN, "Kesehatan Wanita"),
        (CATEGORY_CHILD, "Kesehatan Anak"),
        (CATEGORY_HEART, "Jantung & Pembuluh Darah"),
        (CATEGORY_IMMUNITY, "Imunitas & Infeksi"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_General)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    preparation = models.CharField(
        max_length=255,
        blank=True,
        help_text="Persiapan sebelum pemeriksaan. Contoh: Puasa 8 jam."
    )
    sample_type = models.CharField(max_length=100, blank=True)
    result_time = models.CharField(max_length=100, default="2-3 Hari Kerja")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_package = models.BooleanField(default=False)
    included_tests = models.TextField(blank=True, help_text="Daftar tes yang termasuk (jika paket).")
    icon = models.CharField(max_length=50, blank=True, help_text="Nama ikon (misal: bi-droplet).")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self) -> str:
        return self.name


class LabBooking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Menunggu Konfirmasi"),
        (STATUS_CONFIRMED, "Sudah Dikonfirmasi"),
        (STATUS_COMPLETED, "Selesai"),
        (STATUS_CANCELLED, "Dibatalkan"),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lab_bookings",
    )
    service = models.ForeignKey(
        LabService,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    notes = models.TextField(blank=True)
    fasting_confirmation = models.BooleanField(default=False)
    contact_phone = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.patient} - {self.service.name} ({self.preferred_date})"
