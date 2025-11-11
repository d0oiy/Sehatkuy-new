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
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['user', 'specialization', 'phone', 'email', 'address']

