# Generated by Django 5.1.4 on 2024-12-22 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0003_alter_vehiclecategory_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='hp',
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='kw',
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
    ]