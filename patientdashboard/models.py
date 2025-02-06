# patientdashboard/models.py

import uuid
from django.db import models
from practitionerdashboard.models import AvailableSlot
from user_account.models import Patient, Practitioner
from django.utils.timezone import now
import uuid
from django.db import models
from django.core.exceptions import ValidationError

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    slot = models.OneToOneField(AvailableSlot, on_delete=models.CASCADE)
    practitioner = models.ForeignKey(Practitioner, on_delete=models.CASCADE, related_name="appointments", default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Pending')  # New field

    video_call_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Prevent patients from booking another appointment if payment is not cleared."""
        if self.payment_status == "Pending":
            existing_unpaid = Appointment.objects.filter(patient=self.patient, payment_status="Pending").exclude(id=self.id).exists()
            if existing_unpaid:
                raise ValidationError("You have an unpaid appointment. Please complete the payment before booking another one.")

        # Generate a unique video call link if it does not exist.
        if not self.video_call_link:
            meeting_id = f"{uuid.uuid4()}-{self.patient.id}-{self.practitioner.id}"
            self.video_call_link = f"https://meet.jit.si/{meeting_id}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment with {self.practitioner} at {self.slot.start_time} - {self.slot.end_time}"





class Notification(models.Model):
    recipient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    url = models.URLField(null=True, blank=True)  # Link to the video call
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.first_name} {self.recipient.last_name}"




