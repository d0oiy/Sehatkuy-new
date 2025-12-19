from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Medicine, MedicineOrder, OrderItem

User = get_user_model()

class PharmacyPaymentFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        # create patient
        self.patient = User.objects.create_user(username='patient1', password='pass')
        # create admin_poliklinik
        self.admin_poli = User.objects.create_user(username='adminpoli', password='pass')
        self.admin_poli.role = 'admin_poliklinik'
        self.admin_poli.save()
        # create medicine
        self.med = Medicine.objects.create(name='Paracetamol', price=5000, stock=100)

    def test_patient_confirm_redirects_to_payment_and_sets_pending(self):
        self.client.login(username='patient1', password='pass')
        # create order
        create_url = reverse('pharmacy:order_create')
        resp = self.client.post(create_url, {
            'delivery_address': 'Jl. Test',
            'delivery_phone': '081234',
        })
        order = MedicineOrder.objects.latest('created_at')
        # add item
        add_item_url = reverse('pharmacy:order_items', args=[order.pk])
        resp = self.client.post(add_item_url, {
            'medicine': self.med.pk,
            'quantity': 2,
        })
        order.refresh_from_db()
        self.assertEqual(order.items.count(), 1)
        # confirm (POST) should redirect to payment and set payment_status pending
        confirm_url = reverse('pharmacy:order_confirm', args=[order.pk])
        resp = self.client.post(confirm_url)
        self.assertRedirects(resp, reverse('pharmacy:order_payment', args=[order.pk]))
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'pending')

    def test_create_ipaymu_payment_creates_payment_and_redirects(self):
        from unittest.mock import patch, Mock
        self.client.login(username='patient1', password='pass')
        # create order & item
        create_url = reverse('pharmacy:order_create')
        resp = self.client.post(create_url, {
            'delivery_address': 'Jl. Test',
            'delivery_phone': '081234',
        })
        order = MedicineOrder.objects.latest('created_at')
        add_item_url = reverse('pharmacy:order_items', args=[order.pk])
        resp = self.client.post(add_item_url, {
            'medicine': self.med.pk,
            'quantity': 1,
        })
        # confirm to set pending
        self.client.post(reverse('pharmacy:order_confirm', args=[order.pk]))

        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.content = b'{}'
        mock_resp.json.return_value = {'ReferenceId': 'REF123', 'Url': 'https://sandbox.pay/REF123'}

        with patch('pharmacy.views.requests.post', return_value=mock_resp) as mock_post:
            resp = self.client.post(reverse('pharmacy:order_create_ipaymu', args=[order.pk]))
            # After successful creation, should redirect to external payment link
            self.assertEqual(resp.status_code, 302)
            self.assertIn('sandbox.pay', resp['Location'])
            # Assert header included VA and signature
            headers = mock_post.call_args[1]['headers']
            payload_sent = mock_post.call_args[1]['json']
            from django.conf import settings
            import hmac, hashlib, json as _json
            self.assertEqual(headers.get('va'), settings.IPAYMU_VA)
            secret = getattr(settings, 'IPAYMU_API_SECRET', settings.IPAYMU_API_KEY)
            expected_sig = hmac.new(secret.encode('utf-8'), _json.dumps(payload_sent, separators=(',', ':'), sort_keys=True).encode('utf-8'), hashlib.sha256).hexdigest()
            self.assertEqual(headers.get('signature'), expected_sig)
            self.assertEqual(headers.get('Signature'), expected_sig)
            self.assertIn('timestamp', headers)
            order.refresh_from_db()
            self.assertEqual(order.payment_status, 'pending')
            self.assertEqual(order.payment_transaction_id, 'REF123')
            self.assertEqual(order.payment_url, 'https://sandbox.pay/REF123' )

    def test_create_ipaymu_qris_creates_qr_and_shows_it(self):
        from unittest.mock import patch, Mock
        self.client.login(username='patient1', password='pass')
        # create order & item
        create_url = reverse('pharmacy:order_create')
        resp = self.client.post(create_url, {
            'delivery_address': 'Jl. Test',
            'delivery_phone': '081234',
        })
        order = MedicineOrder.objects.latest('created_at')
        add_item_url = reverse('pharmacy:order_items', args=[order.pk])
        resp = self.client.post(add_item_url, {
            'medicine': self.med.pk,
            'quantity': 1,
        })
        self.client.post(reverse('pharmacy:order_confirm', args=[order.pk]))

        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.content = b'{}'
        mock_resp.json.return_value = {'ReferenceId': 'REFQR', 'QrisUrl': 'https://sandbox.qr/REFQR'}

        with patch('pharmacy.views.requests.post', return_value=mock_resp) as mock_post:
            resp = self.client.post(reverse('pharmacy:order_create_qris', args=[order.pk]))
            # should redirect to order_payment to show QR
            self.assertRedirects(resp, reverse('pharmacy:order_payment', args=[order.pk]))
            # Assert header included VA and signature
            headers = mock_post.call_args[1]['headers']
            payload_sent = mock_post.call_args[1]['json']
            from django.conf import settings
            import hmac, hashlib, json as _json
            self.assertEqual(headers.get('va'), settings.IPAYMU_VA)
            secret = getattr(settings, 'IPAYMU_API_SECRET', settings.IPAYMU_API_KEY)
            expected_sig = hmac.new(secret.encode('utf-8'), _json.dumps(payload_sent, separators=(',', ':'), sort_keys=True).encode('utf-8'), hashlib.sha256).hexdigest()
            self.assertEqual(headers.get('signature'), expected_sig)
            self.assertEqual(headers.get('Signature'), expected_sig)
            self.assertIn('timestamp', headers)
            order.refresh_from_db()
            self.assertEqual(order.payment_status, 'pending')
            self.assertEqual(order.payment_transaction_id, 'REFQR')
            self.assertEqual(order.payment_qr_url, 'https://sandbox.qr/REFQR')
    def test_admin_poliklinik_can_view_orders(self):
        # create an order by patient
        order = MedicineOrder.objects.create(patient=self.patient, order_number='ORD-TEST')
        # login as admin_poliklinik
        self.client.login(username='adminpoli', password='pass')
        # order_list
        resp = self.client.get(reverse('pharmacy:order_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'ORD-TEST')
        # patient_orders
        resp = self.client.get(reverse('pharmacy:patient_orders'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'ORD-TEST')
        # admin_order_detail
        resp = self.client.get(reverse('pharmacy:admin_order_detail', args=[order.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'ORD-TEST')
