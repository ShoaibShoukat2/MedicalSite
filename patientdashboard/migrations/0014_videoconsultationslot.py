# Generated by Django 5.1.4 on 2025-03-28 01:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patientdashboard', '0013_review_reply'),
        ('user_account', '0005_practitioner_gender_practitioner_location_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoConsultationSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_available', models.BooleanField(default=True)),
                ('fee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('practitioner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_slots', to='user_account.practitioner')),
            ],
            options={
                'ordering': ['date', 'start_time'],
                'unique_together': {('practitioner', 'date', 'start_time')},
            },
        ),
    ]
