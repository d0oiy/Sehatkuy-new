from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser
from pharmacy.models import Medicine, MedicineOrder, OrderItem

class PharmacyPaymentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = CustomUser.objects.create_user(username='pat1', password='pass', role='pasien')
        self.medicine = Medicine.objects.create(name='TestMed', dosage='10mg', unit='tablet', price=50000, stock=10)
        self.order = MedicineOrder.objects.create(order_number='ORD-TEST', patient=self.patient, delivery_address='Addr', delivery_phone='0812')
        self.item = OrderItem.objects.create(order=self.order, medicine=self.medicine, quantity=1, price_at_time=self.medicine.price)
        self.order.total_price = self.order.calculate_total()
        self.order.save()

    def test_order_payment_flow(self):
        self.client.login(username='pat1', password='pass')
        confirm_url = reverse('pharmacy:order_confirm', args=[self.order.pk])
        resp = self.client.post(confirm_url, {})
        self.assertEqual(resp.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'pending')
        pay_url = reverse('pharmacy:order_payment', args=[self.order.pk])
        resp = self.client.post(pay_url, {})
        self.assertEqual(resp.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
