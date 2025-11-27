from django.db import models
from django.utils import timezone
from django.urls import reverse
import datetime

DAYS = [
    (0, "Senin"),
    (1, "Selasa"),
    (2, "Rabu"),
    (3, "Kamis"),
    (4, "Jumat"),
    (5, "Sabtu"),
    (6, "Minggu"),
]

class Poliklinik(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    # Admin override status
    force_open = models.BooleanField(default=False)
    force_close = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    # —————— STATUS BUKA/TUTUP ——————
    def is_currently_open(self):
        """Cek apakah poliklinik buka sekarang (dengan timezone Makassar)."""
        now = timezone.localtime()
        weekday = now.weekday()
        current_time = now.time()

        # Override admin
        if self.force_close:
            return False
        if self.force_open:
            return True

        schedules = self.schedules.filter(day=weekday, is_active=True)

        for sch in schedules:
            if sch.start_time <= current_time < sch.end_time:
                return True

        return False

    def get_absolute_url(self):
        return reverse("poliklinik:detail", args=[self.slug])


class Schedule(models.Model):
    poliklinik = models.ForeignKey(Poliklinik, related_name="schedules", on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.poliklinik.name} - {self.get_day_display()} ({self.start_time}-{self.end_time})"



