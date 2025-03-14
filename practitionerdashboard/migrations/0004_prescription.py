# Generated by Django 5.0.1 on 2025-03-09 00:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('practitionerdashboard', '0003_remove_availableslot_is_booked_availableslot_status'),
        ('user_account', '0005_practitioner_gender_practitioner_location_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, null=True)),
                ('prescription_file', models.FileField(blank=True, null=True, upload_to='prescriptions/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_account.patient')),
                ('practitioner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_account.practitioner')),
            ],
        ),
    ]
