from django.core.management.base import BaseCommand
from poliklinik.models import Poliklinik, Schedule
from datetime import time


class Command(BaseCommand):
    help = 'Menambahkan data poliklinik default'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Memulai proses penambahan data poliklinik...\n'))
        polikliniks_data = [
            {
                'name': 'Poli Umum',
                'slug': 'poli-umum',
                'description': 'Layanan kesehatan umum untuk berbagai keluhan penyakit ringan hingga sedang. Melayani pemeriksaan kesehatan rutin, pengobatan penyakit umum, dan konsultasi kesehatan.',
            },
            {
                'name': 'Poli Kandungan Ibu dan Anak',
                'slug': 'poli-kandungan-ibu-dan-anak',
                'description': 'Layanan kesehatan khusus untuk ibu hamil, ibu menyusui, dan anak-anak. Meliputi pemeriksaan kehamilan, imunisasi, dan perawatan kesehatan ibu dan anak.',
            },
            {
                'name': 'Poli Gigi dan Mulut',
                'slug': 'poli-gigi-dan-mulut',
                'description': 'Layanan kesehatan gigi dan mulut meliputi pemeriksaan, perawatan, pencabutan gigi, dan konsultasi kesehatan gigi dan mulut.',
            },
            {
                'name': 'Poli Imunisasi dan Lansia',
                'slug': 'poli-imunisasi-dan-lansia',
                'description': 'Layanan kesehatan untuk imunisasi anak dan perawatan kesehatan lansia. Meliputi vaksinasi, pemeriksaan kesehatan lansia, dan konsultasi kesehatan.',
            },
        ]

        # Jadwal default: Senin-Jumat 08:00-16:00
        default_schedules = [
            (0, time(8, 0), time(12, 0)),  # Senin pagi
            (0, time(13, 0), time(16, 0)),  # Senin siang
            (1, time(8, 0), time(12, 0)),  # Selasa pagi
            (1, time(13, 0), time(16, 0)),  # Selasa siang
            (2, time(8, 0), time(12, 0)),  # Rabu pagi
            (2, time(13, 0), time(16, 0)),  # Rabu siang
            (3, time(8, 0), time(12, 0)),  # Kamis pagi
            (3, time(13, 0), time(16, 0)),  # Kamis siang
            (4, time(8, 0), time(12, 0)),  # Jumat pagi
            (4, time(13, 0), time(16, 0)),  # Jumat siang
        ]

        created_count = 0
        updated_count = 0

        for poli_data in polikliniks_data:
            poli, created = Poliklinik.objects.get_or_create(
                slug=poli_data['slug'],
                defaults={
                    'name': poli_data['name'],
                    'description': poli_data['description'],
                }
            )

            if not created:
                # Update jika sudah ada
                poli.name = poli_data['name']
                poli.description = poli_data['description']
                poli.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'✓ Updated: {poli.name}')
                )
                
                # Cek apakah sudah ada jadwal, jika belum tambahkan
                if not poli.schedules.exists():
                    for day, start, end in default_schedules:
                        Schedule.objects.create(
                            poliklinik=poli,
                            day=day,
                            start_time=start,
                            end_time=end,
                            is_active=True
                        )
                    self.stdout.write(
                        self.style.SUCCESS(f'  → Jadwal operasional ditambahkan')
                    )
            else:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {poli.name}')
                )

                # Tambahkan jadwal default untuk poliklinik baru
                for day, start, end in default_schedules:
                    Schedule.objects.create(
                        poliklinik=poli,
                        day=day,
                        start_time=start,
                        end_time=end,
                        is_active=True
                    )
                self.stdout.write(
                    self.style.SUCCESS(f'  → Jadwal operasional ditambahkan')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Selesai! Created: {created_count}, Updated: {updated_count}'
            )
        )

