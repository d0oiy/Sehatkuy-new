from django import forms
from .models import Medicine, MedicineOrder, OrderItem, Delivery
from django.contrib.auth.models import User


class MedicineForm(forms.ModelForm):
    """Form untuk menambah/edit obat - hanya untuk dokter dan admin"""
    
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'dosage', 'unit', 'price', 'stock', 'side_effects']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Obat'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Deskripsi Obat',
                'rows': 3
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 500mg, 10mL'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Harga',
                'step': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jumlah Stok'
            }),
            'side_effects': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Efek Samping',
                'rows': 3
            }),
        }


class MedicineOrderForm(forms.ModelForm):
    """Form untuk membuat pesanan obat"""
    delivery_latitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    delivery_longitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = MedicineOrder
        fields = ['delivery_address', 'delivery_phone', 'notes']
        widgets = {
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Alamat Lengkap Pengiriman',
                'rows': 3
            }),
            'delivery_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nomor Telepon (08xxxxxxxxx)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Catatan tambahan (opsional)',
                'rows': 2
            }),
        }


class OrderItemForm(forms.ModelForm):
    """Form untuk menambah item ke pesanan"""
    medicine = forms.ModelChoiceField(
        queryset=Medicine.objects.filter(stock__gt=0),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Pilih Obat'
    )
    
    class Meta:
        model = OrderItem
        fields = ['medicine', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jumlah',
                'min': 1
            }),
        }


class DeliveryForm(forms.ModelForm):
    """Form untuk update pengiriman"""
    
    class Meta:
        model = Delivery
        fields = ['courier', 'status', 'pickup_latitude', 'pickup_longitude', 
                  'delivery_latitude', 'delivery_longitude', 'estimated_arrival']
        widgets = {
            'courier': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'pickup_latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': 'Latitude Apotek'
            }),
            'pickup_longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': 'Longitude Apotek'
            }),
            'delivery_latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': 'Latitude Tujuan'
            }),
            'delivery_longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': 'Longitude Tujuan'
            }),
            'estimated_arrival': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }


class DeliveryStatusForm(forms.ModelForm):
    """Form untuk update status pengiriman saja"""
    
    class Meta:
        model = Delivery
        fields = ['status', 'actual_arrival']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'actual_arrival': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
