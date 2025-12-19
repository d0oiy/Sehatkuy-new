# Generated manually: add payment_url field to MedicineOrder
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0003_medicineorder_paid_at_medicineorder_payment_proof_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicineorder',
            name='payment_url',
            field=models.CharField(max_length=1024, null=True, blank=True),
        ),
    ]
