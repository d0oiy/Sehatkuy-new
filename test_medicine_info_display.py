import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("TESTING PATIENT ORDERS WITH MEDICINE INFO")
print("=" * 80)

# Get admin user
admin = User.objects.get(username='testadmin')

client = Client()
client.force_login(admin)

response = client.get('/pharmacy/admin/patients/')
print(f"\nURL: /pharmacy/admin/patients/")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Check if medicine names are displayed
    print("\nCek tampilan nama obat:")
    
    medicine_names = [
        'Test Medicine',
        'Paracetamol',
        'Ibuprofen',
    ]
    
    for med_name in medicine_names:
        if med_name in content:
            print(f"  ✓ '{med_name}' ditemukan")
        else:
            # Try to find any medicine
            if 'medicine' in content.lower():
                print(f"  ? '{med_name}' tidak ditemukan, tapi ada informasi medicine")
            else:
                print(f"  ✗ '{med_name}' TIDAK ditemukan")
    
    # Check if "Jumlah" or "Quantity" is shown
    if 'Jumlah:' in content:
        print("\n✓ Label 'Jumlah' ditemukan")
    else:
        print("\n✗ Label 'Jumlah' TIDAK ditemukan")
    
    # Check if dosage is shown
    if 'mg' in content or 'mL' in content or '500' in content:
        print("✓ Informasi dosis ditampilkan")
    else:
        print("✗ Informasi dosis TIDAK ditemukan")
    
    # Check if unit is shown
    if 'tablet' in content or 'botol' in content or 'unit' in content.lower():
        print("✓ Unit obat ditampilkan")
    else:
        print("? Unit obat tidak jelas")
    
    # Check table structure
    if 'Obat' in content:
        print("\n✓ Kolom 'Obat' ada di header tabel")
    else:
        print("\n✗ Kolom 'Obat' TIDAK ada")
    
    # Check if the table has the correct columns
    columns = ['No. Pesanan', 'Pasien', 'Obat', 'Status', 'Total', 'Tanggal', 'Aksi']
    print("\nCek kolom tabel:")
    for col in columns:
        if col in content:
            print(f"  ✓ {col}")
        else:
            print(f"  ✗ {col} TIDAK DITEMUKAN")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Kolom 'Obat' menampilkan:")
    print("  - Nama obat")
    print("  - Dosis obat (contoh: 500mg)")
    print("  - Unit obat (contoh: tablet)")
    print("  - Jumlah pesanan")
    
else:
    print(f"ERROR: Status {response.status_code}")
