import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from pharmacy.models import MedicineOrder

User = get_user_model()

print("=" * 80)
print("TESTING PATIENT DASHBOARD - ORDERS DISPLAY")
print("=" * 80)

patient = User.objects.get(username='user')

# Check orders in DB
print(f"\nPatient: {patient.username}")
patient_orders = MedicineOrder.objects.filter(patient=patient).order_by('-created_at')[:8]
print(f"Orders in DB (last 8): {patient_orders.count()}")
for order in patient_orders:
    print(f"  - {order.order_number}: {order.status}")

# Test dashboard view
print("\n" + "=" * 80)
print("TESTING DASHBOARD VIEW")
print("=" * 80)

client = Client()
client.force_login(patient)

response = client.get('/users/patient/dashboard/')
print(f"\nURL: /users/patient/dashboard/")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Check if orders section exists
    if 'Daftar Pemesanan Obat' in content:
        print("✓ Section 'Daftar Pemesanan Obat' ditemukan")
    else:
        print("✗ Section 'Daftar Pemesanan Obat' TIDAK ditemukan")
    
    # Check if specific orders are shown
    orders_to_check = [
        'ORD-20251126212215-1',
        'ORD-20251126110630-1',
        'ORD-20251126105217-1'
    ]
    
    print("\nCek pesanan di dashboard:")
    for order_num in orders_to_check:
        if order_num in content:
            print(f"  ✓ {order_num} - DITEMUKAN")
        else:
            print(f"  ✗ {order_num} - TIDAK DITEMUKAN")
    
    # Check for "Belum ada pemesanan" message
    if 'Belum ada pemesanan obat' in content:
        print("\n⚠ Dashboard menampilkan 'Belum ada pemesanan obat'")
    elif '<table' in content and 'No. Pesanan' in content:
        print("\n✓ Table pesanan ada di halaman")
    
    # Count tbody rows
    import re
    tbody_match = re.search(r'<tbody>(.*?)</tbody>', content, re.DOTALL)
    if tbody_match:
        tbody_content = tbody_match.group(1)
        rows = tbody_content.count('<tr>')
        print(f"  Rows dalam tabel pesanan: {rows}")
    else:
        print("  No tbody found in orders section")

else:
    print(f"ERROR: Status {response.status_code}")
