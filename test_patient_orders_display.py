import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from pharmacy.models import MedicineOrder
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

print("=" * 80)
print("TESTING PATIENT ORDER LIST DISPLAY")
print("=" * 80)

# Get patient user
patient = User.objects.get(username='user')
print(f"\nPatient: {patient.username}")
print(f"Email: {patient.email}")
print(f"Role: {patient.role}")

# Check patient's orders
patient_orders = MedicineOrder.objects.filter(patient=patient)
print(f"\nTotal pesanan milik pasien: {patient_orders.count()}")
for order in patient_orders:
    print(f"  - {order.order_number}: Status = {order.status} ({order.get_status_display()})")

# Test the view with patient login
print("\n" + "=" * 80)
print("TESTING ORDER LIST VIEW AS PATIENT")
print("=" * 80)

client = Client()
client.force_login(patient)

response = client.get('/pharmacy/orders/')
print(f"\nResponse Status: {response.status_code}")

if response.status_code == 200:
    # Check if orders are in response context
    if response.context and 'orders' in response.context:
        orders_in_context = response.context['orders']
        print(f"Orders in context: {orders_in_context.count()}")
        for order in orders_in_context:
            print(f"  - {order.order_number}: {order.status}")
    else:
        print("No context or 'orders' not found in context")
    
    # Check HTML content
    content = response.content.decode('utf-8')
    if 'ORD-20251126212215-1' in content:
        print("\n✓ Pesanan ORD-20251126212215-1 ditemukan di HTML")
    else:
        print("\n✗ Pesanan ORD-20251126212215-1 TIDAK ditemukan di HTML")
    
    if 'ORD-20251126105217-1' in content:
        print("✓ Pesanan ORD-20251126105217-1 ditemukan di HTML")
    else:
        print("✗ Pesanan ORD-20251126105217-1 TIDAK ditemukan di HTML")
    
    if 'ORD-20251126110630-1' in content:
        print("✓ Pesanan ORD-20251126110630-1 ditemukan di HTML")
    else:
        print("✗ Pesanan ORD-20251126110630-1 TIDAK ditemukan di HTML")
    
    # Check if the table has rows
    if '<tbody>' in content:
        print("\n✓ Table tbody ditemukan di HTML")
        # Count order rows
        order_rows = content.count('<tr>')
        print(f"Total <tr> tags: {order_rows}")
    else:
        print("\n✗ Table tbody TIDAK ditemukan di HTML")

else:
    print(f"ERROR: Got status code {response.status_code}")
