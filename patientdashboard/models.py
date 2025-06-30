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

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    slot = models.OneToOneField(AvailableSlot, on_delete=models.CASCADE)
    practitioner = models.ForeignKey(Practitioner, on_delete=models.CASCADE, related_name="appointments", default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    video_call_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    PAYMENT_STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]
    
    

    # ... existing fields ...
    payment_status = models.CharField(
        max_length=10, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='Unpaid'
    )
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    

    def save(self, *args, **kwargs):
        """Generate video call link if it doesn't exist"""
        if not self.video_call_link:
            meeting_id = f"{uuid.uuid4()}-{self.patient.id}-{self.practitioner.id}"
            self.video_call_link = f"https://meet.google.com/lookup/{meeting_id}"
        
        # Mark the slot as booked when appointment is created
        if not self.pk:  # Only for new appointments
            self.slot.status = 'booked'
            self.amount = self.practitioner.price  # Set from practitioner's price
            self.payment_status = 'Unpaid'
            self.slot.save()
            
        super().save(*args, **kwargs)
    def get_formatted_date(self):
        return self.slot.date.strftime("%B %d, %Y")
    
    def get_formatted_time(self):
        return f"{self.slot.start_time.strftime('%I:%M %p')} - {self.slot.end_time.strftime('%I:%M %p')}"

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



class VideoConsultationSlot(models.Model):
    practitioner = models.ForeignKey(Practitioner, on_delete=models.CASCADE, related_name='video_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['practitioner', 'date', 'start_time']
        
    def __str__(self):
        return f"{self.practitioner} - {self.date} {self.start_time}-{self.end_time}"

class Billing(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True)
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
            self.due_date = timezone.now() + timezone.timedelta(days=3)
        super().save(*args, **kwargs)