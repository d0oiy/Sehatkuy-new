from django.db import migrations


def seed_emergency_data(apps, schema_editor):
    EmergencyFacility = apps.get_model("emergency", "EmergencyFacility")
    EmergencyContact = apps.get_model("emergency", "EmergencyContact")

    facilities = [
        {
            "name": "RS SehatKuy Pusat",
            "facility_type": "hospital",
            "address": "Jl. Kesehatan No. 12, Jakarta",
            "phone_number": "021-1234567",
            "ambulance_number": "0812-9000-9111",
        },
        {
            "name": "RS Medika Nusantara",
            "facility_type": "hospital",
            "address": "Jl. Medika Raya No. 8, Bandung",
            "phone_number": "022-7654321",
            "ambulance_number": "0813-8899-1122",
        },
        {
            "name": "Puskesmas Harmoni",
            "facility_type": "puskesmas",
            "address": "Jl. Harmoni No. 5, Surabaya",
            "phone_number": "031-4567890",
        },
        {
            "name": "Puskesmas Cendana",
            "facility_type": "puskesmas",
            "address": "Jl. Cendana No. 3, Banjarmasin",
            "phone_number": "0511-223344",
        },
    ]

    contacts = [
        {"label": "Call Center SehatKuy", "phone_number": "1500-911", "description": "Layanan informasi kesehatan 24 jam", "priority": 1},
        {"label": "Ambulans Nasional", "phone_number": "119", "description": "Ambulans layanan cepat tanggap", "priority": 2},
        {"label": "Pemadam Kebakaran", "phone_number": "113", "description": "Untuk kondisi kebakaran & evakuasi", "priority": 3},
    ]

    EmergencyFacility.objects.bulk_create(EmergencyFacility(**data) for data in facilities)
    EmergencyContact.objects.bulk_create(EmergencyContact(**data) for data in contacts)


def remove_emergency_data(apps, schema_editor):
    EmergencyFacility = apps.get_model("emergency", "EmergencyFacility")
    EmergencyContact = apps.get_model("emergency", "EmergencyContact")
    EmergencyFacility.objects.all().delete()
    EmergencyContact.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("emergency", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_emergency_data, remove_emergency_data),
    ]

