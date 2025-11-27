from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["reason"]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 3, "class": "form-control"})
        }
