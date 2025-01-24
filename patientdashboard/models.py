# patientdashboard/models.py

from django.db import models
from practitionerdashboard.models import AvailableSlot
from user_account.models import Patient  # Correct import of AvailableSlot
from django.utils.timezone import now

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    slot = models.OneToOneField(AvailableSlot, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment with {self.slot.practitioner} at {self.slot.start_time} - {self.slot.end_time}"
