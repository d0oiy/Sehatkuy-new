from django import forms
from users.models import CustomUser
from doctors.models import Doctor

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['user', 'poliklinik', 'specialization', 'phone', 'email', 'address']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'poliklinik': forms.Select(attrs={'class': 'form-control', 'id': 'poliSelect'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'id': 'specializationField'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        qs = CustomUser.objects.filter(role='dokter').exclude(doctor_profile__isnull=False)

        if self.instance.pk:
            qs = qs | CustomUser.objects.filter(pk=self.instance.user.pk)

        self.fields['user'].queryset = qs.order_by('username')