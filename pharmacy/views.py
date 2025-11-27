from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime, timedelta
import json

from .models import Medicine, MedicineOrder, OrderItem, Delivery
from .forms import (
    MedicineForm, MedicineOrderForm, OrderItemForm, 
    DeliveryForm, DeliveryStatusForm
)


# ==================== MEDICINE VIEWS ====================

@login_required
def medicine_list(request):
    """Tampilkan list obat yang tersedia"""
    medicines = Medicine.objects.all()
    
    # Search & Filter
    search = request.GET.get('search', '')
    unit_filter = request.GET.get('unit', '')
    
    if search:
        medicines = medicines.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search)
        )
    
    if unit_filter:
        medicines = medicines.filter(unit=unit_filter)
    
    context = {
        'medicines': medicines,
        'units': Medicine.UNIT_CHOICES,
        'search': search,
        'unit_filter': unit_filter,
    }
    return render(request, 'pharmacy/medicine_list.html', context)


@login_required
def medicine_detail(request, pk):
    """Tampilkan detail obat"""
    medicine = get_object_or_404(Medicine, pk=pk)
    context = {'medicine': medicine}
    return render(request, 'pharmacy/medicine_detail.html', context)


@login_required
def medicine_create(request):
    """Buat obat baru (hanya dokter & admin)"""
    # Izinkan admin/staff atau dokter (role 'dokter') menambah obat
    if not (request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', '') == 'dokter'):
        messages.error(request, 'Anda tidak memiliki akses untuk menambah obat.')
        return redirect('pharmacy:medicine_list')
    
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.created_by = request.user
            medicine.save()
            messages.success(request, f'Obat "{medicine.name}" berhasil ditambahkan.')
            return redirect('pharmacy:medicine_detail', pk=medicine.pk)
    else:
        form = MedicineForm()
    
    context = {'form': form, 'title': 'Tambah Obat Baru'}
    return render(request, 'pharmacy/medicine_form.html', context)


@login_required
def medicine_update(request, pk):
    """Edit obat (hanya dokter & admin)"""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    # Izinkan admin/staff atau dokter (role 'dokter') mengedit obat
    if not (request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', '') == 'dokter'):
        messages.error(request, 'Anda tidak memiliki akses untuk mengedit obat.')
        return redirect('pharmacy:medicine_detail', pk=pk)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, f'Obat "{medicine.name}" berhasil diperbarui.')
            return redirect('pharmacy:medicine_detail', pk=medicine.pk)
    else:
        form = MedicineForm(instance=medicine)
    
    context = {'form': form, 'medicine': medicine, 'title': 'Edit Obat'}
    return render(request, 'pharmacy/medicine_form.html', context)


@login_required
def medicine_delete(request, pk):
    """Hapus obat (hanya dokter & admin)"""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    # Izinkan admin/staff atau dokter (role 'dokter') menghapus obat
    if not (request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', '') == 'dokter'):
        messages.error(request, 'Anda tidak memiliki akses untuk menghapus obat.')
        return redirect('pharmacy:medicine_detail', pk=pk)
    
    if request.method == 'POST':
        medicine_name = medicine.name
        medicine.delete()
        messages.success(request, f'Obat "{medicine_name}" berhasil dihapus.')
        return redirect('pharmacy:medicine_list')
    
    context = {'medicine': medicine}
    return render(request, 'pharmacy/medicine_confirm_delete.html', context)


# ==================== ORDER VIEWS ====================

@login_required
def order_list(request):
    """Tampilkan list pesanan obat"""
    if request.user.is_staff or request.user.is_superuser:
        # Admin & dokter melihat semua pesanan
        orders = MedicineOrder.objects.all()
    else:
        # Pasien hanya melihat pesanan mereka
        orders = MedicineOrder.objects.filter(patient=request.user)
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'statuses': MedicineOrder.STATUS_CHOICES,
        'status_filter': status_filter,
    }
    return render(request, 'pharmacy/order_list.html', context)


@login_required
def order_detail(request, pk):
    """Tampilkan detail pesanan"""
    order = get_object_or_404(MedicineOrder, pk=pk)
    
    # Check permission
    if not request.user.is_staff and order.patient != request.user:
        messages.error(request, 'Anda tidak memiliki akses ke pesanan ini.')
        return redirect('pharmacy:order_list')
    
    context = {'order': order}
    return render(request, 'pharmacy/order_detail.html', context)


@login_required
def order_create(request):
    """Buat pesanan obat baru"""
    if request.method == 'POST':
        form = MedicineOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.patient = request.user
            
            # Generate order number
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            order.order_number = f"ORD-{timestamp}-{request.user.id}"
            
            # Save delivery coordinates from map if provided
            delivery_lat = form.cleaned_data.get('delivery_latitude')
            delivery_lng = form.cleaned_data.get('delivery_longitude')
            
            if delivery_lat:
                order.delivery_latitude = delivery_lat
            if delivery_lng:
                order.delivery_longitude = delivery_lng
            
            order.save()
            messages.success(request, 'Pesanan dibuat. Silakan tambahkan obat.')
            return redirect('pharmacy:order_items', order_id=order.pk)
    else:
        form = MedicineOrderForm()
    
    context = {'form': form, 'title': 'Buat Pesanan Obat'}
    return render(request, 'pharmacy/order_form.html', context)


@login_required
def order_items(request, order_id):
    """Kelola item dalam pesanan"""
    order = get_object_or_404(MedicineOrder, pk=order_id)
    
    # Check permission
    if not request.user.is_staff and order.patient != request.user:
        messages.error(request, 'Anda tidak memiliki akses ke pesanan ini.')
        return redirect('pharmacy:order_list')
    
    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order
            item.price_at_time = item.medicine.price
            
            # Check stock
            if item.medicine.stock < item.quantity:
                messages.error(request, f'Stok {item.medicine.name} tidak cukup.')
            else:
                item.save()
                order.total_price = order.calculate_total()
                order.save()
                messages.success(request, f'{item.medicine.name} ditambahkan ke pesanan.')
                return redirect('pharmacy:order_items', order_id=order.pk)
    else:
        form = OrderItemForm()
    
    context = {
        'order': order,
        'form': form,
        'items': order.items.all(),
    }
    return render(request, 'pharmacy/order_items.html', context)


@login_required
def order_item_delete(request, order_id, item_id):
    """Hapus item dari pesanan"""
    order = get_object_or_404(MedicineOrder, pk=order_id)
    item = get_object_or_404(OrderItem, pk=item_id, order=order)
    
    # Check permission
    if not request.user.is_staff and order.patient != request.user:
        messages.error(request, 'Anda tidak memiliki akses.')
        return redirect('pharmacy:order_list')
    
    if request.method == 'POST':
        item.delete()
        order.total_price = order.calculate_total()
        order.save()
        messages.success(request, 'Item dihapus dari pesanan.')
    
    return redirect('pharmacy:order_items', order_id=order.pk)


@login_required
def order_confirm(request, pk):
    """Konfirmasi pesanan"""
    order = get_object_or_404(MedicineOrder, pk=pk)
    
    # Check permission
    if not request.user.is_staff and order.patient != request.user:
        messages.error(request, 'Anda tidak memiliki akses.')
        return redirect('pharmacy:order_list')
    
    if request.method == 'POST':
        if order.items.count() == 0:
            messages.error(request, 'Pesanan tidak boleh kosong.')
        else:
            order.status = 'confirmed'
            order.save()
            
            # Buat delivery record
            Delivery.objects.create(
                order=order,
                pickup_latitude='-6.2088',  # Default Jakarta
                pickup_longitude='106.8456',
                delivery_latitude='-6.2088',
                delivery_longitude='106.8456',
                estimated_arrival=datetime.now() + timedelta(hours=2)
            )
            
            messages.success(request, 'Pesanan dikonfirmasi. Menunggu verifikasi admin.')
            return redirect('pharmacy:order_detail', pk=pk)
    
    context = {'order': order}
    return render(request, 'pharmacy/order_confirm.html', context)


# ==================== DELIVERY & MAP VIEWS ====================

@login_required
def delivery_map(request, order_id):
    """Tampilkan map pengiriman"""
    order = get_object_or_404(MedicineOrder, pk=order_id)
    delivery = get_object_or_404(Delivery, order=order)
    
    # Check permission
    if not request.user.is_staff and order.patient != request.user:
        messages.error(request, 'Anda tidak memiliki akses.')
        return redirect('pharmacy:order_list')
    
    context = {
        'order': order,
        'delivery': delivery,
        'delivery_json': json.dumps({
            'pickup': {
                'lat': float(delivery.pickup_latitude),
                'lng': float(delivery.pickup_longitude),
            },
            'delivery': {
                'lat': float(delivery.delivery_latitude),
                'lng': float(delivery.delivery_longitude),
            }
        })
    }
    return render(request, 'pharmacy/delivery_map.html', context)


@login_required
def delivery_update(request, pk):
    """Update informasi pengiriman"""
    delivery = get_object_or_404(Delivery, pk=pk)
    
    # Check permission
    if not request.user.is_staff:
        messages.error(request, 'Hanya admin yang dapat mengupdate pengiriman.')
        return redirect('pharmacy:order_list')
    
    if request.method == 'POST':
        form = DeliveryForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informasi pengiriman berhasil diperbarui.')
            return redirect('pharmacy:delivery_map', order_id=delivery.order.pk)
    else:
        form = DeliveryForm(instance=delivery)
    
    context = {'form': form, 'delivery': delivery}
    return render(request, 'pharmacy/delivery_form.html', context)


@login_required
def delivery_status_update(request, pk):
    """Update status pengiriman saja (untuk pengantar)"""
    delivery = get_object_or_404(Delivery, pk=pk)
    
    # Check permission: hanya pengantar atau admin
    if delivery.courier != request.user and not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki akses.')
        return redirect('pharmacy:order_list')
    
    if request.method == 'POST':
        form = DeliveryStatusForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            
            # Update order status berdasarkan delivery status
            order = delivery.order
            if delivery.status == 'delivered':
                order.status = 'delivered'
                order.save()
            
            messages.success(request, 'Status pengiriman berhasil diperbarui.')
            return redirect('pharmacy:delivery_map', order_id=delivery.order.pk)
    else:
        form = DeliveryStatusForm(instance=delivery)
    
    context = {'form': form, 'delivery': delivery}
    return render(request, 'pharmacy/delivery_status_form.html', context)


@login_required
def order_confirm_receipt(request, pk):
    """Konfirmasi penerimaan obat oleh pasien"""
    order = get_object_or_404(MedicineOrder, pk=pk)
    
    # Check permission - hanya pasien pemilik order
    if order.patient != request.user:
        messages.error(request, 'Anda tidak memiliki akses.')
        return redirect('pharmacy:order_list')
    
    # Hanya bisa confirm jika status 'delivered'
    if order.status != 'delivered':
        messages.error(request, 'Pesanan belum dalam status pengiriman.')
        return redirect('pharmacy:order_detail', pk=pk)
    
    if request.method == 'POST':
        from django.utils import timezone
        order.status = 'received'
        order.received_at = timezone.now()
        order.save()
        
        messages.success(request, 'Terima kasih! Obat telah dikonfirmasi diterima.')
        return redirect('pharmacy:order_detail', pk=pk)
    
    context = {'order': order}
    return render(request, 'pharmacy/order_confirm_receipt.html', context)


@login_required
@login_required
def patient_orders(request, patient_id=None):
    """View untuk admin/dokter melihat pesanan pasien"""
    # Check permission - hanya staff/superuser
    # Allow staff, superuser, or users with role 'admin' or 'dokter'
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_staff or request.user.is_superuser or user_role in ('admin', 'dokter')):
        messages.error(request, 'Anda tidak memiliki akses.')
        return redirect('pharmacy:order_list')
    
    # Jika patient_id diberikan, tampilkan pesanan patient tertentu
    if patient_id:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        patient = get_object_or_404(User, pk=patient_id)
        orders = MedicineOrder.objects.filter(patient=patient)
        title = f'Pesanan dari {patient.first_name} {patient.last_name}'
    else:
        # Tampilkan semua pesanan dengan grouping by pasien
        orders = MedicineOrder.objects.all().select_related('patient').order_by('-created_at')
        title = 'Semua Pesanan Pasien'
    
    # Filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'title': title,
        'patient_id': patient_id,
        'statuses': MedicineOrder.STATUS_CHOICES,
        'status_filter': status_filter,
    }
    return render(request, 'pharmacy/patient_orders.html', context)


@login_required
def admin_order_detail(request, pk):
    """View untuk admin/dokter melihat detail pesanan pasien"""
    # Check permission - hanya staff/superuser
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Anda tidak memiliki akses.')
        return redirect('pharmacy:order_list')
    
    order = get_object_or_404(MedicineOrder, pk=pk)
    
    context = {
        'order': order,
        'is_admin_view': True,
    }
    return render(request, 'pharmacy/admin_order_detail.html', context)


# ==================== API VIEWS ====================

@login_required
def api_delivery_location(request, delivery_id):
    """API untuk get lokasi pengiriman real-time (JSON)"""
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    
    # Check permission
    if not request.user.is_staff and delivery.order.patient != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    data = {
        'status': delivery.status,
        'pickup': {
            'lat': float(delivery.pickup_latitude),
            'lng': float(delivery.pickup_longitude),
        },
        'delivery': {
            'lat': float(delivery.delivery_latitude),
            'lng': float(delivery.delivery_longitude),
        },
        'estimated_arrival': delivery.estimated_arrival.isoformat() if delivery.estimated_arrival else None,
        'actual_arrival': delivery.actual_arrival.isoformat() if delivery.actual_arrival else None,
    }
    return JsonResponse(data)

