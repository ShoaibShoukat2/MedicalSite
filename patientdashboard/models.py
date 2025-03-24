# patientdashboard/models.py

from datetime import timedelta,datetime
from django.utils.timezone import make_aware, now
import uuid
from django.db import models
from practitionerdashboard.models import AvailableSlot
from user_account.models import Patient, Practitioner
from django.utils.timezone import now
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
from django.utils.timezone import now
from django.utils import timezone

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
            existing_unpaid = Appointment.objects.filter(
                patient=self.patient, payment_status="Pending"
            ).exclude(id=self.id).exists()
            
            if existing_unpaid:
                raise ValidationError(
                    "You have an unpaid appointment. Please complete the payment before booking another one."
                )
                

        # Generate a unique video call link if it does not exist.
        if not self.video_call_link:
            meeting_id = f"{uuid.uuid4()}-{self.patient.id}-{self.practitioner.id}"
            self.video_call_link = f"https://meet.jit.si/{meeting_id}"

        super().save(*args, **kwargs)
        
          # Schedule email reminder 1 hour before appointment
        # Combine and make timezone-aware
        start_datetime = datetime.combine(date.today(), self.slot.start_time)
        start_datetime = timezone.make_aware(start_datetime)

        reminder_time = start_datetime - timedelta(hours=1)
        countdown = (reminder_time - timezone.now()).total_seconds()

    
            

    def __str__(self):
        return f"Appointment with {self.practitioner} at {self.slot.start_time} - {self.slot.end_time}"
    





class Notification(models.Model):
    recipient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    url = models.URLField(null=True, blank=True)  
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.first_name} {self.recipient.last_name}"


class Review(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reviews')
    practitioner = models.ForeignKey(Practitioner, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  
    feedback = models.TextField(null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Review by {self.patient.first_name} for {self.practitioner.first_name} - {self.rating} Stars"


class Reply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')  # One review can have many replies
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Points to either Patient or Practitioner model
    object_id = models.PositiveIntegerField()  # Stores the ID of the related object (Patient or Practitioner)
    content_object = GenericForeignKey('content_type', 'object_id')  # This is the GenericForeignKey

    message = models.TextField()  # The reply message
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of reply creation

    def __str__(self):
        return f"Reply by {self.content_object} on {self.review}"
    
    
    
    