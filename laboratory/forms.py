from django import forms
from django.utils import timezone

from .models import LabBooking, LabService


class LabBookingForm(forms.ModelForm):
    accept_terms = forms.BooleanField(
        required=True,
        label="Saya telah membaca ketentuan pemeriksaan laboratorium."
    )

    class Meta:
        model = LabBooking
        fields = [
            "service",
            "preferred_date",
            "preferred_time",
            "contact_phone",
            "fasting_confirmation",
            "notes",
        ]
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "preferred_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Catatan tambahan (opsional)"}),
            "contact_phone": forms.TextInput(attrs={"placeholder": "08xxxxxxxxxx"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-control").strip()

        self.fields["service"].queryset = LabService.objects.filter(is_active=True)
        self.fields["service"].empty_label = "Pilih layanan lab"
        self.fields["fasting_confirmation"].widget.attrs["class"] = "form-check-input"
        self.fields["accept_terms"].widget.attrs["class"] = "form-check-input"

    def clean_preferred_date(self):
        date_value = self.cleaned_data["preferred_date"]
        if date_value < timezone.now().date():
            raise forms.ValidationError("Tanggal tidak boleh di masa lalu.")
        return date_value

