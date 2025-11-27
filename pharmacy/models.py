from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

# Model untuk Obat
class Medicine(models.Model):
    UNIT_CHOICES = [
        ('tablet', 'Tablet'),
        ('kapsula', 'Kapsula'),
        ('mL', 'Mililiter'),
        ('gram', 'Gram'),
        ('botol', 'Botol'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nama Obat')
    description = models.TextField(verbose_name='Deskripsi')
    dosage = models.CharField(max_length=100, verbose_name='Dosis')  # Contoh: 500mg, 10mL
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, verbose_name='Satuan')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Harga'
    )
    stock = models.IntegerField(validators=[MinValueValidator(0)], verbose_name='Stok')
    side_effects = models.TextField(blank=True, verbose_name='Efek Samping')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='medicines_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Medicines'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.dosage} {self.unit}"


# Model untuk Pesanan Obat
class MedicineOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu Konfirmasi'),
        ('confirmed', 'Dikonfirmasi'),
        ('processing', 'Sedang Diproses'),
        ('ready', 'Siap Dikirim'),
        ('shipped', 'Dalam Pengiriman'),
        ('delivered', 'Terkirim'),
        ('received', 'Diterima Pasien'),
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, verbose_name='Nomor Pesanan')
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medicine_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_address = models.TextField(verbose_name='Alamat Pengiriman')
    delivery_phone = models.CharField(max_length=15, verbose_name='Nomor Telepon Pengiriman')
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Latitude Pengiriman')
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Longitude Pengiriman')
    notes = models.TextField(blank=True, verbose_name='Catatan Pesanan')
    received_at = models.DateTimeField(null=True, blank=True, verbose_name='Waktu Diterima')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.patient.username}"
    
    def calculate_total(self):
        return sum(item.subtotal() for item in self.items.all())


# Model untuk Item dalam Pesanan (One-to-Many)
class OrderItem(models.Model):
    order = models.ForeignKey(MedicineOrder, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('order', 'medicine')
    
    def __str__(self):
        return f"{self.medicine.name} x{self.quantity}"
    
    def subtotal(self):
        return self.price_at_time * self.quantity


# Model untuk Pengiriman dengan Map
class Delivery(models.Model):
    DELIVERY_STATUS = [
        ('waiting', 'Menunggu Pengantar'),
        ('in_transit', 'Dalam Pengiriman'),
        ('delivered', 'Terkirim'),
        ('failed', 'Pengiriman Gagal'),
    ]
    
    order = models.OneToOneField(MedicineOrder, on_delete=models.CASCADE, related_name='delivery')
    courier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='waiting')
    
    # Lokasi untuk Map
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitude Apotek')
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitude Apotek')
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitude Tujuan')
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitude Tujuan')
    
    # Waktu
    estimated_arrival = models.DateTimeField(blank=True, null=True, verbose_name='Estimasi Tiba')
    actual_arrival = models.DateTimeField(blank=True, null=True, verbose_name='Waktu Tiba Aktual')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pengiriman {self.order.order_number}"
