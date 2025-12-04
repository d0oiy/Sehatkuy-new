from django import forms
from .models import CustomUser


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'birth_date',
            'gender',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Depan'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Belakang'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nomor HP'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Alamat Lengkap'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'first_name': 'Nama Depan',
            'last_name': 'Nama Belakang',
            'email': 'Email',
            'phone': 'Nomor HP',
            'address': 'Alamat',
            'birth_date': 'Tanggal Lahir',
            'gender': 'Jenis Kelamin',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Field yang wajib diisi
        self.fields['first_name'].required = True
        self.fields['last_name'].required = False
        self.fields['email'].required = True
        self.fields['phone'].required = False
        self.fields['address'].required = True
        self.fields['birth_date'].required = True
        self.fields['gender'].required = False

