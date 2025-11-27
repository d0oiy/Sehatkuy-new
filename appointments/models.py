from django.db import models
from django.conf import settings
from doctors.models import Doctor
from poliklinik.models import Poliklinik


class AppointmentSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="slots")
    poliklinik = models.ForeignKey(Poliklinik, on_delete=models.CASCADE)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    quota = models.IntegerField(default=10)

    def used_quota(self):
        # Hitung hanya appointment yang pending atau approved
        return self.appointments.exclude(status='cancelled').count()

    def available(self):
        return self.used_quota() < self.quota

    def available_numbers(self):
        return [i for i in range(1, self.quota + 1)
                if i not in self.appointments.exclude(status='cancelled').values_list("queue_number", flat=True)]

    @property
    def remaining_quota(self):
        return self.quota - self.used_quota()

    def __str__(self):
        return f"{self.doctor} - {self.date} {self.start_time}"


class Appointment(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    poliklinik = models.ForeignKey(Poliklinik, on_delete=models.CASCADE)
    slot = models.ForeignKey(AppointmentSlot, on_delete=models.CASCADE, related_name="appointments")

    date = models.DateField()
    time = models.TimeField()
    queue_number = models.IntegerField(null=True, blank=True)

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('cancelled', 'Cancelled')],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.doctor} ({self.date})"
