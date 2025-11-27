from django.contrib import admin
from django.utils.html import format_html
from .models import Medicine, MedicineOrder, OrderItem, Delivery


def mark_as_delivered(modeladmin, request, queryset):
    """Admin action untuk mengubah status pesanan menjadi delivered"""
    updated = queryset.update(status='delivered')
    modeladmin.message_user(request, f'{updated} pesanan berhasil diubah menjadi "Terkirim"')

mark_as_delivered.short_description = "Ubah status ke Terkirim (Delivered)"


def mark_as_confirmed(modeladmin, request, queryset):
    """Admin action untuk mengubah status pesanan menjadi confirmed"""
    updated = queryset.update(status='confirmed')
    modeladmin.message_user(request, f'{updated} pesanan berhasil diubah menjadi "Dikonfirmasi"')

mark_as_confirmed.short_description = "Ubah status ke Dikonfirmasi (Confirmed)"


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'dosage', 'unit', 'price', 'stock', 'created_by', 'created_at')
    list_filter = ('unit', 'created_at')
    search_fields = ('name', 'dosage')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('name', 'dosage', 'unit', 'description')
        }),
        ('Harga & Stok', {
            'fields': ('price', 'stock')
        }),
        ('Informasi Tambahan', {
            'fields': ('side_effects', 'created_by')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('medicine', 'quantity', 'price_at_time', 'subtotal')

@admin.register(MedicineOrder)
class MedicineOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'patient', 'status_badge', 'total_price', 'received_at', 'created_at')
    list_filter = ('status', 'created_at', 'received_at')
    search_fields = ('order_number', 'patient__username')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'received_at', 'delivery_latitude', 'delivery_longitude')
    actions = [mark_as_delivered, mark_as_confirmed]
    inlines = [OrderItemInline]
    fieldsets = (
        ('Informasi Pesanan', {
            'fields': ('order_number', 'patient', 'status')
        }),
        ('Pengiriman', {
            'fields': ('delivery_address', 'delivery_phone', 'delivery_latitude', 'delivery_longitude')
        }),
        ('Konfirmasi Penerimaan', {
            'fields': ('received_at',),
            'classes': ('collapse',)
        }),
        ('Harga', {
            'fields': ('total_price',)
        }),
        ('Catatan', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Tampilkan status dengan warna"""
        status_colors = {
            'pending': 'FFA500',      # Orange
            'confirmed': '4169E1',    # Blue
            'processing': '1E90FF',   # Light Blue
            'ready': '32CD32',        # Lime Green
            'shipped': 'FFD700',      # Gold
            'delivered': '00CED1',    # Dark Turquoise
            'received': '228B22',     # Forest Green
            'completed': '008000',    # Green
            'cancelled': 'DC143C',    # Crimson
        }
        color = status_colors.get(obj.status, '808080')
        return format_html(
            '<span style="background-color: #{}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'courier', 'status', 'estimated_arrival', 'actual_arrival')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'courier__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Pesanan & Pengantar', {
            'fields': ('order', 'courier', 'status')
        }),
        ('Lokasi Pickup (Apotek)', {
            'fields': ('pickup_latitude', 'pickup_longitude')
        }),
        ('Lokasi Pengiriman (Pasien)', {
            'fields': ('delivery_latitude', 'delivery_longitude')
        }),
        ('Waktu', {
            'fields': ('estimated_arrival', 'actual_arrival')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
