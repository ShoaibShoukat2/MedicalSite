# Generated by Django 5.0.1 on 2025-01-22 10:09

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('practitionerdashboard', '0001_initial'),
        ('user_account', '0005_practitioner_gender_practitioner_location_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_date', models.DateField(default=django.utils.timezone.now)),
                ('notes', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='user_account.patient')),
                ('practitioner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='user_account.practitioner')),
                ('slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='practitionerdashboard.availableslot')),
            ],
        ),
    ]
