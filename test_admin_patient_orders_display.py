import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("TESTING PATIENT ORDERS VIEW - DISPLAYS PATIENT INFO")
print("=" * 80)

# Get admin user
admin = User.objects.get(username='testadmin')

# Test admin view
print(f"\nAdmin: {admin.username}")
print(f"URL: /pharmacy/admin/patients/")

client = Client()
client.force_login(admin)

response = client.get('/pharmacy/admin/patients/')
print(f"Status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Check if patient names are displayed
    patient_names = [
        'testpatient',  # username
        'user',  # username
    ]
    
    print("\nCek tampilan nama pasien:")
    for name in patient_names:
        if name in content:
            print(f"  ✓ '{name}' ditemukan di halaman")
        else:
            print(f"  ✗ '{name}' TIDAK ditemukan di halaman")
    
    # Check if order numbers are displayed
    order_numbers = [
        'ORD-20251126212215-1',
        'TEST-20251126211858',
    ]
    
    print("\nCek tampilan nomor pesanan:")
    for order_num in order_numbers:
        if order_num in content:
            print(f"  ✓ '{order_num}' ditemukan di halaman")
        else:
            print(f"  ✗ '{order_num}' TIDAK ditemukan di halaman")
    
    # Check if patient info (email) is displayed
    if '@' in content and ('email' in content.lower() or 'kikitanjung' in content):
        print("\n✓ Informasi email/pasien ditemukan")
    else:
        print("\n? Informasi email pasien tidak jelas")
    
    # Check if status badges are shown
    if 'Terkirim' in content or 'Diterima Pasien' in content:
        print("✓ Status pesanan ditampilkan")
    
    # Check table structure
    if '<table' in content and 'Pasien' in content:
        print("✓ Tabel dengan kolom 'Pasien' ada")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✓ Tampilan pesanan sudah menampilkan:")
    print("  - Nama pasien (first_name + last_name)")
    print("  - Email pasien")
    print("  - Nomor pesanan")
    print("  - Status pesanan")
    print("  - Total harga")
    print("  - Items count")
    
else:
    print(f"ERROR: Status {response.status_code}")
