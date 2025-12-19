from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser
from pharmacy.models import Medicine, MedicineOrder, OrderItem

class AdminPaymentVerifyTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = CustomUser.objects.create_user(username='pat2', password='pass', role='pasien')
        # admin poliklinik
        self.adminp = CustomUser.objects.create_user(username='admpk', password='pass', role='admin_poliklinik')
        self.medicine = Medicine.objects.create(name='MedA', dosage='10mg', unit='tablet', price=20000, stock=10)
        self.order = MedicineOrder.objects.create(order_number='ORD-VER', patient=self.patient, delivery_address='Addr', delivery_phone='0812')
        self.item = OrderItem.objects.create(order=self.order, medicine=self.medicine, quantity=1, price_at_time=self.medicine.price)
        self.order.total_price = self.order.calculate_total()
        self.order.payment_status = 'pending'
        self.order.save()

    def test_admin_poliklinik_verify_payment(self):
        self.client.login(username='admpk', password='pass')
        url = reverse('pharmacy:admin_verify_payment', args=[self.order.pk])
        resp = self.client.post(url, {'action': 'verify'})
        self.assertEqual(resp.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertEqual(self.order.status, 'confirmed')
