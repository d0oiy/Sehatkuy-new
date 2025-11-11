from django import forms
from .models import Doctor
from users.models import CustomUser

class DoctorForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='dokter'),
        label='Akun Dokter',
        help_text='Pilih akun pengguna yang memiliki role dokter'
    )

    class Meta:
        model = Doctor
        fields = ['user', 'specialization', 'phone', 'email', 'address']
