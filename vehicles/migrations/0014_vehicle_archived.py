# Generated by Django 5.1.4 on 2025-01-02 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0013_alter_vehicle_first_reg_alter_vehicle_last_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
