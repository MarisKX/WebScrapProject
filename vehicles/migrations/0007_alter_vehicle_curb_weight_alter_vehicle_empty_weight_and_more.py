# Generated by Django 5.1.4 on 2024-12-22 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0006_rename_type_code_bodytype_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='curb_weight',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='empty_weight',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='gross_combination_weight',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='max_weight_legal',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='max_weight_tech',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='trailer_with_brakes',
            field=models.CharField(blank=True, db_index=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='trailer_without_brakes',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
