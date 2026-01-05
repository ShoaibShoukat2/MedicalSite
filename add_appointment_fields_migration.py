# Run this command to create and apply the migration:
# python manage.py makemigrations patientdashboard
# python manage.py migrate

"""
This migration adds reason and urgency fields to the Appointment model.

The fields added are:
- reason: TextField for appointment reason (optional, can be blank)
- urgency: CharField with choices (normal, urgent, emergency) defaulting to 'normal'
"""

# After running the migration, you can update existing appointments if needed:
"""
from patientdashboard.models import Appointment

# Update existing appointments to have default values
Appointment.objects.filter(reason__isnull=True).update(reason='')
Appointment.objects.filter(urgency__isnull=True).update(urgency='normal')
"""