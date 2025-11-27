from datetime import datetime


SYMPTOM_LIBRARY = {
    "demam": "Suhu tubuh yang meningkat dapat diatasi dengan cukup istirahat, minum air hangat, dan konsumsi parasetamol sesuai dosis. "
    "Jika demam lebih dari 3 hari atau disertai sesak napas, segera buat janji tatap muka.",
    "batuk": "Batuk bisa disebabkan iritasi tenggorokan atau infeksi. Minum air hangat, hindari makanan berminyak, dan gunakan obat batuk herbal. "
    "Jika batuk berdarah atau lebih dari 2 minggu, periksa langsung ke poliklinik {poliklinik}.",
    "pusing": "Pastikan kamu sudah makan teratur dan cukup minum. Coba duduk/berbaring dulu sampai kondisi stabil. "
    "Jika pusing disertai pandangan kabur atau muntah terus-menerus, segera ke IGD.",
    "diare": "Jaga hidrasi dengan oralit setiap selesai BAB. Hindari makanan pedas/dingin. "
    "Jika diare lebih dari 3 hari atau feses berdarah, temui dokter spesialis penyakit dalam.",
    "flu": "Istirahat cukup, konsumsi vitamin C, dan gunakan masker untuk mencegah penularan. "
    "Jika suhu >38.5°C atau sesak, segera konsultasi lanjutan.",
}


def generate_chatbot_reply(message: str, doctor) -> str:
    """
    Rule-based helper yang memberikan respon awal sebelum dokter ikut serta.
    """
    normalized = message.lower()
    doctor_name = doctor.user.get_full_name() or doctor.user.username
    poliklinik_name = getattr(doctor.poliklinik, "name", "terkait")

    for keyword, advice in SYMPTOM_LIBRARY.items():
        if keyword in normalized:
            return (
                f"Saya bantu sampaikan ke Dr. {doctor_name}. "
                f"{advice.format(poliklinik=poliklinik_name)} "
                "Dokter akan meninjau percakapan ini dan memberi respons lanjutan."
            )

    current_time = datetime.now().strftime("%H:%M")
    return (
        f"Pesan kamu sudah diterima pada {current_time}. "
        f"Dr. {doctor_name} akan meninjau dan membalas secepatnya. "
        "Sementara itu, catat gejala penting seperti durasi sakit, obat yang sedang dikonsumsi, dan hasil pemeriksaan terakhir."
    )

