import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("CHECKING PATIENT ORDER LIST PAGE")
print("=" * 80)

# Get patient user
patient = User.objects.get(username='user')

# Test the view with patient login
client = Client()
client.force_login(patient)

response = client.get('/pharmacy/orders/')
print(f"\nURL: /pharmacy/orders/")
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Look for specific orders in the page
    orders_to_check = [
        'ORD-20251126212215-1',
        'ORD-20251126110630-1',
        'ORD-20251126105217-1'
    ]
    
    print("\nCek keberadaan pesanan di halaman:")
    for order_num in orders_to_check:
        if order_num in content:
            print(f"✓ {order_num} - DITEMUKAN")
        else:
            print(f"✗ {order_num} - TIDAK DITEMUKAN")
    
    # Check if page has no orders message
    if 'Belum ada pesanan' in content or 'Tidak ada' in content:
        print("\n⚠ Halaman menampilkan pesan 'Tidak ada pesanan'")
    elif '<tbody>' in content:
        print("\n✓ Halaman memiliki tabel pesanan (tbody ditemukan)")
    
    # Extract the table content
    if '<table' in content:
        print("\n✓ Halaman memiliki tabel")
        
        # Count rows in table
        import re
        rows = re.findall(r'<tr[^>]*>.*?</tr>', content, re.DOTALL)
        print(f"  Total baris (termasuk header): {len(rows)}")
    
    # Check if there's an error message
    if 'error' in content.lower() or 'tidak memiliki akses' in content.lower():
        print("\n⚠ Ada pesan error di halaman")
    
else:
    print(f"\nERROR: Status code {response.status_code}")
