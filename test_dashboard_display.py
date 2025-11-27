#!/usr/bin/env python
"""Test dashboard display dengan orders"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from pharmacy.models import MedicineOrder

User = get_user_model()

# Cek apakah ada admin user
admin_users = User.objects.filter(is_superuser=True)
print(f"Admin users: {admin_users.count()}")
for admin in admin_users[:3]:
    print(f"  - {admin.username} (superuser={admin.is_superuser})")

# Cek orders
orders = MedicineOrder.objects.select_related('patient').prefetch_related('items__medicine').order_by('-created_at')[:12]
print(f"\nTotal orders: {orders.count()}")
for order in orders[:3]:
    print(f"  - {order.order_number} | Patient: {order.patient.username}")

# Test client
client = Client()

# Test akses dashboard tanpa login
print("\n=== Test Dashboard (no login) ===")
response = client.get('/adminpanel/dashboard/', follow=True)
print(f"Status: {response.status_code}")
print(f"Redirects: {len(response.redirect_chain)}")

# Test akses dashboard dengan admin
if admin_users.exists():
    admin = admin_users.first()
    print(f"\n=== Test Dashboard (login as {admin.username}) ===")
    
    # Login
    login_success = client.login(username=admin.username, password='admin123')
    print(f"Login success: {login_success}")
    
    # Test dashboard
    response = client.get('/adminpanel/dashboard/')
    print(f"Status: {response.status_code}")
    
    # Check if 'recent_orders' ada di context
    if hasattr(response, 'context') and response.context:
        print(f"Context keys: {list(response.context.keys())}")
        
        if 'recent_orders' in response.context:
            recent_orders = response.context['recent_orders']
            print(f"Recent orders in context: {recent_orders.count()}")
            
            # Check template rendering
            content = response.content.decode('utf-8')
            if 'Pesanan Obat Terbaru' in content:
                print("✓ 'Pesanan Obat Terbaru' section found in template")
            else:
                print("✗ 'Pesanan Obat Terbaru' section NOT found in template")
            
            if 'ORD-20251126212215-1' in content or 'TEST-' in content:
                print("✓ Order numbers found in template")
            else:
                print("✗ Order numbers NOT found in template")
        else:
            print("✗ 'recent_orders' NOT in context")
    else:
        print("! Context not available")
