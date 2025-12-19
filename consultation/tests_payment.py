from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser
from doctors.models import Doctor
from poliklinik.models import Poliklinik
from consultation.models import Consultation, ConsultationMessage

class ConsultationPaymentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = CustomUser.objects.create_user(username='patient1', password='pass', role='pasien')
        self.doctor_user = CustomUser.objects.create_user(username='doc1', password='pass', role='dokter')
        self.poliklinik = Poliklinik.objects.create(name='Poliklinik A', slug='pola')
        self.doctor = Doctor.objects.create(user=self.doctor_user, poliklinik=self.poliklinik, specialization='Umum')
        self.consult = Consultation.objects.create(patient=self.patient, doctor=self.doctor)

    def test_generate_chatbot_reply_contains_links(self):
        from consultation.services import generate_chatbot_reply
        reply = generate_chatbot_reply('Saya demam', self.doctor, consultation=self.consult)
        self.assertIn('Pesan Konsultasi sudah terkirim', reply)
        self.assertIn('https://wa.me', reply)
        self.assertIn(reverse('consultation:consultation_pay', args=[self.consult.id]), reply)

    def test_consultation_payment_flow(self):
        self.client.login(username='patient1', password='pass')
        pay_url = reverse('consultation:consultation_pay', args=[self.consult.id])
        resp = self.client.get(pay_url)
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(pay_url, {})
        self.assertEqual(resp.status_code, 302)
        self.consult.refresh_from_db()
        self.assertEqual(self.consult.payment_status, 'paid')
        self.assertEqual(self.consult.status, Consultation.STATUS_ACTIVE)
        # Ensure a bot message was created
        self.assertTrue(ConsultationMessage.objects.filter(consultation=self.consult, sender='bot', message__icontains='Pembayaran').exists())
