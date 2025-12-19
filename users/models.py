from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('pasien', 'Pasien'),
        ('dokter', 'Dokter'),
        ('admin_sistem', 'Admin Sistem'),
        ('admin_poliklinik', 'Admin Poliklinik'),
        ('admin', 'Admin'),  # backwards compatibility
    )

    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=[('L', 'Laki-laki'), ('P', 'Perempuan')], blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='pasien')

    def __str__(self):
        return f"{self.username} ({self.role})"
