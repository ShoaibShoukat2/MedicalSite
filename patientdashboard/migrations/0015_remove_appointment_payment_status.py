# Generated by Django 5.1.4 on 2025-03-28 02:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patientdashboard', '0014_videoconsultationslot'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='payment_status',
        ),
    ]
