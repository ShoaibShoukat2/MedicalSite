# patientdashboard/models.py

from django.db import models
from practitionerdashboard.models import AvailableSlot
from user_account.models import Patient, Practitioner
from django.utils.timezone import now

class Appointment(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    slot = models.OneToOneField(
        AvailableSlot,
        on_delete=models.CASCADE
    )
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.CASCADE,
        related_name="appointments",
        default=1  # Ensure there is a Practitioner with ID=1 in the database
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment with {self.practitioner} at {self.slot.start_time} - {self.slot.end_time}"




