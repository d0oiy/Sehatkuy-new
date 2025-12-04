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


class Queue(models.Model):
    """Model untuk antrian online pasien"""
    STATUS_WAITING = "waiting"
    STATUS_CHECKED_IN = "checked_in"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    
    STATUS_CHOICES = [
        (STATUS_WAITING, "Menunggu"),
        (STATUS_CHECKED_IN, "Sudah Check In"),
        (STATUS_IN_PROGRESS, "Sedang Dilayani"),
        (STATUS_COMPLETED, "Selesai"),
        (STATUS_CANCELLED, "Dibatalkan"),
    ]
    
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="queue"
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="queues"
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="queues")
    poliklinik = models.ForeignKey(Poliklinik, on_delete=models.CASCADE, related_name="queues")
    
    queue_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_WAITING)
    
    # Waktu antrian
    created_at = models.DateTimeField(auto_now_add=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Estimasi waktu tunggu (dalam menit)
    estimated_wait_time = models.IntegerField(default=0, help_text="Estimasi waktu tunggu dalam menit")
    
    class Meta:
        ordering = ['queue_number']
        # Note: Unique constraint dengan condition tidak didukung oleh MariaDB
        # Validasi unik dilakukan di level aplikasi
    
    def __str__(self):
        return f"Antrian #{self.queue_number} - {self.patient.username} - {self.doctor}"
    
    @property
    def position_in_queue(self):
        """Posisi dalam antrian (berapa orang di depan)"""
        if self.status == self.STATUS_COMPLETED or self.status == self.STATUS_CANCELLED:
            return 0
        
        # Hitung antrian yang masih menunggu dengan nomor lebih kecil
        current_queues = Queue.objects.filter(
            doctor=self.doctor,
            poliklinik=self.poliklinik,
            appointment__date=self.appointment.date,
            status__in=[self.STATUS_WAITING, self.STATUS_CHECKED_IN],
            queue_number__lt=self.queue_number
        ).count()
        return current_queues
    
    @property
    def is_current(self):
        """Cek apakah ini antrian yang sedang dilayani"""
        return self.status == self.STATUS_IN_PROGRESS