# Generated by Django 5.0.1 on 2025-02-05 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_chatroom_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='ai_config',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='ai_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
