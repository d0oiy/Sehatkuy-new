import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatkuy_project.settings')
django.setup()

from pharmacy.models import MedicineOrder

# Update the confirmed order to delivered status
order = MedicineOrder.objects.get(order_number='ORD-20251126212215-1')
print(f'Order: {order.order_number}')
print(f'Status lama: {order.status} ({order.get_status_display()})')

order.status = 'delivered'
order.save()

print(f'Status baru: {order.status} ({order.get_status_display()})')
print(f'✓ Pesanan berhasil diubah ke status "Terkirim"')
print(f'\nSekarang pasien bisa melihat tombol "Konfirmasi Penerimaan" untuk pesanan ini!')
