from django import forms
from doctors.models import Doctor
from .models import Consultation


class ConsultationForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.select_related("user", "poliklinik").all(),
        label="Pilih Dokter",
        required=False,
        help_text="Pilih dokter dari poliklinik untuk konsultasi langsung.",
    )

    class Meta:
        model = Consultation
        fields = ["doctor", "doctor_name", "date", "complaint"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "complaint": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = Doctor.objects.select_related(
            "user", "poliklinik"
        ).order_by("poliklinik__name", "user__first_name")
        self.fields["doctor"].empty_label = "Pilih dokter (opsional)"
        self.fields["doctor_name"].label = "Nama Dokter (opsional)"
        self.fields["doctor_name"].required = False
        self.fields["complaint"].label = "Keluhan"
        self.fields["complaint"].required = False


class ConsultationMessageForm(forms.Form):
    message = forms.CharField(
        label="Pesan kamu",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Tuliskan keluhan atau pertanyaan untuk dokter...",
            }
        ),
        max_length=1000,
    )
