#!/usr/bin/env python
"""Test dashboard rendering with orders"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Test client
client = Client()

# Get admin user
admin = User.objects.filter(is_superuser=True).first()
if not admin:
    print("❌ No admin user found!")
    sys.exit(1)

print(f"Admin user: {admin.username}")

# Login
login_ok = client.login(username=admin.username, password='admin123')
if not login_ok:
    print("❌ Login failed!")
    sys.exit(1)

print("✓ Login successful")

# Test dashboard
response = client.get('/adminpanel/dashboard/')
print(f"Status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Check for orders section
    if 'Pesanan Obat Terbaru' in content:
        print("✓ 'Pesanan Obat Terbaru' section found")
    else:
        print("❌ 'Pesanan Obat Terbaru' section NOT found")
    
    # Check for order numbers
    if 'ORD-' in content or 'TEST-' in content:
        print("✓ Order numbers found in page")
        # Count how many orders are shown
        import re
        orders = re.findall(r'(ORD-[\w-]+|TEST-[\w-]+)', content)
        print(f"  Found {len(set(orders))} unique orders: {set(orders)}")
    else:
        print("❌ No order numbers found in page")
    
    # Check for medicine names
    if 'Test Medicine' in content or 'Paracetamol' in content or 'TestMed' in content:
        print("✓ Medicine names found in page")
    else:
        print("❌ No medicine names found in page")
    
    # Check if table is there
    if '<table' in content and 'recent_orders' not in str(response.context):
        print("⚠ Table found but recent_orders might be empty")
    elif 'recent_orders' in response.context:
        print(f"✓ recent_orders in context: {response.context['recent_orders'].count()} orders")
else:
    print(f"❌ Failed to access dashboard: {response.status_code}")
    sys.exit(1)

print("\n✓ Dashboard test completed successfully!")
