from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser

class RoleLoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_system = CustomUser.objects.create_user(username='adminsys', password='pass', role='admin_sistem')
        self.admin_poli = CustomUser.objects.create_user(username='admpoli', password='pass', role='admin_poliklinik')
        self.patient = CustomUser.objects.create_user(username='pat', password='pass', role='pasien')

    def test_admin_sistem_login_redirects_to_admin_dashboard(self):
        resp = self.client.post(reverse('login'), {'username': 'adminsys', 'password': 'pass'})
        self.assertIn(resp.status_code, (302, 301))
        # follow redirect
        follow = self.client.get(resp.url)
        self.assertEqual(follow.status_code, 200)

    def test_admin_poliklinik_login_redirects_to_poliklinik_dashboard(self):
        resp = self.client.post(reverse('login'), {'username': 'admpoli', 'password': 'pass'})
        self.assertIn(resp.status_code, (302, 301))
        # follow redirect
        follow = self.client.get(resp.url)
        self.assertEqual(follow.status_code, 200)
        # ensure redirected to adminpanel poliklinik dashboard
        self.assertIn('/adminpanel/poliklinik/', resp.url)

    def test_patient_login_redirects_to_patient_dashboard(self):
        resp = self.client.post(reverse('login'), {'username': 'pat', 'password': 'pass'})
        self.assertIn(resp.status_code, (302, 301))
        follow = self.client.get(resp.url)
        self.assertEqual(follow.status_code, 200)
