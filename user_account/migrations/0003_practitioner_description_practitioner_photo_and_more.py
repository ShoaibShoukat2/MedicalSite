# Generated by Django 5.1.4 on 2025-01-20 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0002_patient_practitioner'),
    ]

    operations = [
        migrations.AddField(
            model_name='practitioner',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='practitioner',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='practitioner_photos/'),
        ),
        migrations.AddField(
            model_name='practitioner',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
