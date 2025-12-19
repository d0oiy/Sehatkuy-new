from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser
from poliklinik.models import Poliklinik
from doctors.models import Doctor
from appointments.models import AppointmentSlot

class PoliklinikManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.adminp = CustomUser.objects.create_user(username='admpk2', password='pass', role='admin_poliklinik')
        self.doctor_user = CustomUser.objects.create_user(username='doc2', password='pass', role='dokter')
        self.poliklinik = Poliklinik.objects.create(name='PoliTest', slug='politest')
        self.doctor = Doctor.objects.create(user=self.doctor_user, poliklinik=self.poliklinik, specialization='Umum')

    def test_admin_can_create_slot(self):
        self.client.login(username='admpk2', password='pass')
        url = reverse('adminpanel:poliklinik_slot_manage', args=[self.poliklinik.id])
        resp = self.client.post(url, {
            'action': 'create',
            'doctor_id': str(self.doctor.id),
            'date': '2025-12-25',
            'start_time': '09:00',
            'end_time': '10:00',
            'quota': '10'
        })
        self.assertEqual(resp.status_code, 302)
        slots = AppointmentSlot.objects.filter(poliklinik=self.poliklinik)
        self.assertTrue(slots.exists())

    def test_doctor_cannot_modify_slots(self):
        self.client.login(username='doc2', password='pass')
        url = reverse('doctors:slot_manage')
        before = AppointmentSlot.objects.count()
        resp = self.client.post(url, {'action': 'create'})
        self.assertEqual(resp.status_code, 302)
        after = AppointmentSlot.objects.count()
        self.assertEqual(before, after)
