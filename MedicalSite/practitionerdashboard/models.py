from django.db import models
from django.utils.timezone import now

from user_account.models import Practitioner
class AvailableSlot(models.Model):
    practitioner = models.ForeignKey(Practitioner, on_delete=models.CASCADE, related_name="available_slots")
    day_of_week = models.CharField(max_length=10, choices=[
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)  # Track if the slot is booked

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.start_time} - {self.end_time} ({self.practitioner})"
