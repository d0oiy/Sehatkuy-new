from django.urls import reverse
from django.utils import timezone


def generate_chatbot_reply(message: str, doctor, consultation=None) -> str:
    """Return a simple, non-diagnostic reply that instructs user to pay and/or contact via WhatsApp."""
    doctor_name = doctor.user.get_full_name() or doctor.user.username
    phone = (doctor.phone or "").replace("+", "").replace(" ", "")
    wa_link = f"https://wa.me/{phone}" if phone else "https://wa.me/"
    payment_url = reverse("consultation:consultation_pay", args=[consultation.id]) if consultation else "#"

    return (
        "Pesan Konsultasi sudah terkirim dan sedang di proses mohon menunggu. "
        f"Untuk melanjutkan konsultasi via WhatsApp: {wa_link} . "
        "Layanan konsultasi dikenai biaya. "
        f"Silakan lakukan pembayaran di {payment_url}. Setelah pembayaran sukses, konsultasi akan dilanjutkan."
    )

