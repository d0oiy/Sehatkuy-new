from django.db import migrations


def seed_services(apps, schema_editor):
    LabService = apps.get_model("laboratory", "LabService")
    services = [
        {
            "category": "general",
            "name": "Paket Medical Check Up Basic",
            "description": "Paket screening umum termasuk darah lengkap, urin lengkap, fungsi hati dan ginjal.",
            "included_tests": "Darah lengkap, Urin lengkap, Gula darah, Profil lipid, SGOT, SGPT, Kreatinin",
            "sample_type": "Darah & Urin",
            "result_time": "2 Hari Kerja",
            "price": 650000,
            "is_package": True,
        },
        {
            "category": "heart",
            "name": "Profil Jantung & Lipid",
            "description": "Memantau kolesterol dan risiko penyakit kardiovaskular.",
            "included_tests": "Kolesterol total, LDL, HDL, Trigliserida, hs-CRP",
            "sample_type": "Darah",
            "preparation": "Puasa 10 jam",
            "result_time": "1 Hari Kerja",
            "price": 420000,
            "is_package": True,
        },
        {
            "category": "women",
            "name": "Paket Kesehatan Wanita",
            "description": "Pemeriksaan hormon dasar dan skrining anemia.",
            "included_tests": "Hemoglobin, Ferritin, TSH, FT4, Vitamin D",
            "sample_type": "Darah",
            "result_time": "3 Hari Kerja",
            "price": 780000,
            "is_package": True,
        },
        {
            "category": "immunity",
            "name": "Tes Serologi Imunitas",
            "description": "Menilai antibodi terhadap infeksi umum.",
            "sample_type": "Darah",
            "result_time": "2 Hari Kerja",
            "price": 350000,
            "preparation": "Tidak perlu puasa",
            "is_package": False,
        },
        {
            "category": "child",
            "name": "Panel Kesehatan Anak",
            "description": "Memantau tumbuh kembang dan status gizi anak.",
            "sample_type": "Darah",
            "result_time": "2 Hari Kerja",
            "price": 390000,
            "included_tests": "Darah lengkap, Vitamin D, Kalsium",
            "is_package": True,
        },
    ]
    LabService.objects.bulk_create(LabService(**data) for data in services)


def remove_services(apps, schema_editor):
    LabService = apps.get_model("laboratory", "LabService")
    names = [
        "Paket Medical Check Up Basic",
        "Profil Jantung & Lipid",
        "Paket Kesehatan Wanita",
        "Tes Serologi Imunitas",
        "Panel Kesehatan Anak",
    ]
    LabService.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("laboratory", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_services, remove_services),
    ]

