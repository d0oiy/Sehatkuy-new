import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from pharmacy.models import MedicineOrder, Medicine
from django.utils import timezone

User = get_user_model()

# Test Script to verify new order confirmation features
print("=" * 60)
print("TESTING ORDER CONFIRMATION FEATURES")
print("=" * 60)

# Get or create test user (patient)
patient, created = User.objects.get_or_create(
    username='testpatient',
    defaults={
        'email': 'testpatient@example.com',
        'first_name': 'Test',
        'last_name': 'Patient',
        'role': 'pasien'
    }
)
print(f"\nPatient: {patient.username} (created: {created})")

# Get or create test medicine
medicine, created = Medicine.objects.get_or_create(
    name='Test Medicine',
    defaults={
        'dosage': '500mg',
        'unit': 'tablet',
        'price': 50000,
        'stock': 100,
        'description': 'Test medicine for confirmation feature',
        'created_by': User.objects.filter(is_staff=True).first() or patient
    }
)
print(f"Medicine: {medicine.name} (created: {created})")

# Create a test order with new fields
order_number = f"TEST-{timezone.now().strftime('%Y%m%d%H%M%S')}-{patient.id}"
order = MedicineOrder.objects.create(
    order_number=order_number,
    patient=patient,
    delivery_address='Jl. Test Street No. 123, Jakarta',
    delivery_phone='081234567890',
    delivery_latitude=-6.2088,  # Jakarta coordinates
    delivery_longitude=106.8456,
    status='delivered',  # Set to delivered to test confirmation
    total_price=50000,
)

print(f"\nOrder Created:")
print(f"  - Order Number: {order.order_number}")
print(f"  - Status: {order.status}")
print(f"  - Delivery Address: {order.delivery_address}")
print(f"  - Delivery Coordinates: ({order.delivery_latitude}, {order.delivery_longitude})")
print(f"  - Received At: {order.received_at}")

# Test the confirmation workflow
print("\n" + "=" * 60)
print("TESTING CONFIRMATION WORKFLOW")
print("=" * 60)

client = Client()

# Login as patient
login_success = client.login(username='testpatient', password=None)
print(f"\nLogin (no password set): {login_success}")

# If login fails, set a password and try again
if not login_success:
    patient.set_password('testpass123')
    patient.save()
    login_success = client.login(username='testpatient', password='testpass123')
    print(f"Login (with password): {login_success}")

if login_success:
    # Test order detail view
    print("\nTesting order detail view...")
    response = client.get(f'/pharmacy/orders/{order.pk}/')
    print(f"  - Status: {response.status_code}")
    print(f"  - Template used: {[t.name for t in response.templates]}")
    
    # Test confirmation page
    print("\nTesting order confirmation receipt view...")
    response = client.get(f'/pharmacy/orders/{order.pk}/confirm-receipt/')
    print(f"  - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  - Template used: {[t.name for t in response.templates]}")
        print("  - Confirmation page accessible! ✓")
    else:
        print(f"  - Error: {response.content.decode()[:200]}")
    
    # Test confirmation submission
    print("\nTesting order confirmation submission...")
    response = client.post(f'/pharmacy/orders/{order.pk}/confirm-receipt/', follow=True)
    print(f"  - Status: {response.status_code}")
    
    # Check order status after confirmation
    order.refresh_from_db()
    print(f"  - New Status: {order.status}")
    print(f"  - Received At: {order.received_at}")
    
    if order.status == 'received' and order.received_at:
        print("  - Confirmation successful! ✓")
    else:
        print("  - Confirmation failed! ✗")
else:
    print("\nLogin failed - cannot test confirmation workflow")

print("\n" + "=" * 60)
print("TESTING FORM FIELDS")
print("=" * 60)

# Test form with coordinates
from pharmacy.forms import MedicineOrderForm

form_data = {
    'delivery_address': 'Test Address',
    'delivery_phone': '081234567890',
    'delivery_latitude': '-6.2088',
    'delivery_longitude': '106.8456',
    'notes': 'Test notes'
}

form = MedicineOrderForm(data=form_data)
print(f"\nForm validation: {form.is_valid()}")
if not form.is_valid():
    print(f"Errors: {form.errors}")
else:
    print("Form is valid! ✓")
    # Check that coordinates are in cleaned_data
    cleaned_lat = form.cleaned_data.get('delivery_latitude')
    cleaned_lng = form.cleaned_data.get('delivery_longitude')
    print(f"  - Cleaned Latitude: {cleaned_lat}")
    print(f"  - Cleaned Longitude: {cleaned_lng}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
