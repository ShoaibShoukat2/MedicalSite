from django.db import models
from django.utils.timezone import now
from django.utils import timezone

from user_account.models import Practitioner,Patient
from django.db import models
from django.utils import timezone
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class PractitionerNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    recipient = models.ForeignKey(Practitioner, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200, default='Notification')
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    url = models.URLField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for Dr. {self.recipient.first_name} {self.recipient.last_name}: {self.title}"


class AvailableSlot(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
    ]
    date = models.DateField()

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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.start_time} - {self.end_time} ({self.practitioner})"





class Prescription(models.Model):
    practitioner = models.ForeignKey(Practitioner, on_delete=models.CASCADE)  # Assuming User is a practitioner
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    prescription_file = models.FileField(upload_to="prescriptions/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Prescription for {self.patient.first_name} by {self.practitioner.first_name}"
    


