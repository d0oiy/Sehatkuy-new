# Generated manually: add payment_qr_url field to MedicineOrder
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0004_add_payment_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicineorder',
            name='payment_qr_url',
            field=models.CharField(max_length=1024, null=True, blank=True),
        ),
    ]
