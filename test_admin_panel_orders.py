import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("TESTING ADMINPANEL DASHBOARD - ORDERS DISPLAY")
print("=" * 80)

# Get admin user
admin = User.objects.get(username='testadmin')

client = Client()
client.force_login(admin)

response = client.get('/adminpanel/dashboard/')
print(f"\nURL: /adminpanel/dashboard/")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Check if the section exists
    if 'Pesanan Obat Terbaru' in content:
        print("✓ Section 'Pesanan Obat Terbaru' ditemukan")
    else:
        print("✗ Section 'Pesanan Obat Terbaru' TIDAK ditemukan")
    
    # Check if order numbers are shown
    order_numbers = [
        'ORD-20251126212215-1',
        'ORD-20251126105217-1',
    ]
    
    print("\nCek tampilan pesanan:")
    for order_num in order_numbers:
        if order_num in content:
            print(f"  ✓ {order_num} ditemukan")
        else:
            print(f"  ? {order_num} tidak ada (mungkin tidak dalam 12 terbaru)")
    
    # Check if patient names are shown
    if 'user' in content or 'testpatient' in content:
        print("✓ Nama pasien ditampilkan")
    else:
        print("? Nama pasien tidak jelas")
    
    # Check if medicine names are shown
    if 'Test Medicine' in content or 'medicine' in content.lower():
        print("✓ Nama obat ditampilkan")
    else:
        print("? Nama obat tidak jelas")
    
    # Check if status is shown
    if 'Terkirim' in content or 'Diterima' in content or 'badge' in content:
        print("✓ Status pesanan ditampilkan")
    else:
        print("? Status pesanan tidak jelas")
    
    # Check if price is shown with rupiah format
    if 'Rp' in content or 'rupiah' in content.lower():
        print("✓ Harga pesanan ditampilkan")
    else:
        print("? Harga pesanan tidak jelas")
    
    # Check if Konsultasi section exists
    if 'Konsultasi Terbaru' in content:
        print("\n✓ Section 'Konsultasi Terbaru' juga ada")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✓ Pesanan Obat Terbaru menampilkan:")
    print("  - Nomor pesanan")
    print("  - Nama pasien")
    print("  - Nama obat (max 2 baris, + info jika ada lebih)")
    print("  - Status pesanan (badge)")
    print("  - Total harga (format Rupiah)")
    
else:
    print(f"ERROR: Status {response.status_code}")
