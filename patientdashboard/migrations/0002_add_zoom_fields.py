# Generated manually for Zoom integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patientdashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='meeting_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='meeting_password',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='host_start_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]