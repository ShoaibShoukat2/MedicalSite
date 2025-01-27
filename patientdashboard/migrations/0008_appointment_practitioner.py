# Generated by Django 5.1.4 on 2025-01-26 16:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patientdashboard', '0007_remove_appointment_practitioner'),
        ('user_account', '0005_practitioner_gender_practitioner_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='practitioner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='user_account.practitioner'),
        ),
    ]
