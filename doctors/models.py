from django.db import models
from users.models import CustomUser
from poliklinik.models import Poliklinik

class Doctor(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'dokter'},
        related_name='doctor_profile'
    )
    poliklinik = models.ForeignKey(
        Poliklinik,
        on_delete=models.SET_NULL,
        null=True,
        related_name="doctors"
    )
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.user.first_name or self.user.username} - {self.specialization}"
