import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from pharmacy.models import MedicineOrder
from django.contrib.auth import get_user_model

User = get_user_model()

# Check all orders and their statuses
print('=== DAFTAR SEMUA PESANAN ===')
orders = MedicineOrder.objects.all()
if orders.exists():
    for order in orders:
        print(f'Order: {order.order_number}')
        print(f'  Pasien: {order.patient.username}')
        print(f'  Status: {order.status} ({order.get_status_display()})')
        print(f'  Total: Rp {order.total_price}')
        print()
else:
    print('Tidak ada pesanan di database')

# Check if there are any orders with 'delivered' status
delivered_orders = MedicineOrder.objects.filter(status='delivered')
print(f'\nTotal pesanan dengan status "delivered": {delivered_orders.count()}')

# Check if there are any patients
patients = User.objects.filter(role='pasien')
print(f'Total pasien: {patients.count()}')
for patient in patients:
    patient_orders = MedicineOrder.objects.filter(patient=patient)
    print(f'  {patient.username}: {patient_orders.count()} pesanan')
    for po in patient_orders:
        print(f'    - {po.order_number}: {po.status}')
