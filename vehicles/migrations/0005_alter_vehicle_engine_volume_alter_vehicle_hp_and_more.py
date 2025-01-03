# Generated by Django 5.1.4 on 2024-12-22 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0004_vehicle_hp_vehicle_kw'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='engine_volume',
            field=models.CharField(max_length=18),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='hp',
            field=models.CharField(blank=True, max_length=18, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='kw',
            field=models.CharField(blank=True, max_length=18, null=True),
        ),
    ]
