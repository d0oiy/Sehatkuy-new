from django.db import models


class EmergencyFacility(models.Model):
    TYPE_HOSPITAL = "hospital"
    TYPE_PUSKESMAS = "puskesmas"

    FACILITY_CHOICES = [
        (TYPE_HOSPITAL, "Rumah Sakit"),
        (TYPE_PUSKESMAS, "Puskesmas"),
    ]

    name = models.CharField(max_length=150)
    facility_type = models.CharField(max_length=20, choices=FACILITY_CHOICES, default=TYPE_HOSPITAL)
    address = models.TextField()
    phone_number = models.CharField(max_length=30)
    ambulance_number = models.CharField(max_length=30, blank=True)
    emergency_unit = models.BooleanField(default=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["facility_type", "name"]

    def __str__(self) -> str:
        return self.name


class EmergencyContact(models.Model):
    label = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=30)
    description = models.CharField(max_length=255, blank=True)
    is_24h = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["priority", "label"]

    def __str__(self) -> str:
        return f"{self.label} ({self.phone_number})"
