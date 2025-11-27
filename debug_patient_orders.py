import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("DEBUGGING PATIENT ORDER LIST")
print("=" * 80)

patient = User.objects.get(username='user')
client = Client()
client.force_login(patient)

# Test different URLs
urls_to_test = [
    '/pharmacy/orders/',
    '/pharmacy/order/list/',
    '/pharmacy/order/',
]

for url in urls_to_test:
    response = client.get(url, follow=True)
    print(f"\nURL: {url}")
    print(f"  Status: {response.status_code}")
    if response.status_code == 404:
        print(f"  Result: NOT FOUND (404)")
    elif response.status_code == 200:
        if 'ORD-' in response.content.decode('utf-8'):
            print(f"  Result: OK - Pesanan ditemukan")
        else:
            print(f"  Result: OK - Tapi pesanan tidak ditemukan")
    else:
        print(f"  Result: Other status code")

# Check URL patterns
print("\n" + "=" * 80)
print("CHECKING URL PATTERNS")
print("=" * 80)

from django.urls import get_resolver
from django.urls.exceptions import Resolver404

resolver = get_resolver()
patterns = resolver.url_patterns

print("\nPharmacy URL patterns:")
for pattern in patterns:
    if 'pharmacy' in str(pattern.pattern):
        print(f"  {pattern.pattern}")
