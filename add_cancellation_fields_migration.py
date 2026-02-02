#!/usr/bin/env python
"""
Migration to add cancellation_reason and cancelled_at fields to Appointment model
Run with: python manage.py shell < add_cancellation_fields_migration.py
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.db import migrations, models

def add_cancellation_fields():
    """Add cancellation_reason and cancelled_at fields to Appointment model"""
    
    # Create the migration manually
    migration_content = '''# Generated migration for cancellation fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('patientdashboard', '0001_initial'),  # Adjust this to your latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='cancellation_reason',
            field=models.TextField(blank=True, null=True, help_text='Reason for appointment cancellation'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True, help_text='When the appointment was cancelled'),
        ),
    ]
'''
    
    # Write migration file
    import os
    from datetime import datetime
    
    # Create migrations directory if it doesn't exist
    migrations_dir = 'patientdashboard/migrations'
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)
    
    # Generate migration filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    migration_filename = f'{migrations_dir}/{timestamp}_add_cancellation_fields.py'
    
    with open(migration_filename, 'w') as f:
        f.write(migration_content)
    
    print(f"✅ Migration file created: {migration_filename}")
    print("📝 Please run: python manage.py makemigrations")
    print("📝 Then run: python manage.py migrate")

if __name__ == "__main__":
    add_cancellation_fields()