# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import localtime
from .models import Appointment

@shared_task
def send_reminder_email(appointment_id):
    """Send reminder email 1 hour before the appointment."""
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment_time = localtime(appointment.slot.start_time)

        subject = "Appointment Reminder"
        message = f"""
        Dear {appointment.patient.first_name},

        This is a reminder for your appointment with {appointment.practitioner.first_name} 
        at {appointment_time.strftime('%Y-%m-%d %H:%M:%S')}.

        Please be on time.

        Thank you!
        """
        
        send_mail(subject, message, 'michdmg@outlook.fr', [appointment.patient.email])
        return f"Reminder sent to {appointment.patient.email}"
    except Appointment.DoesNotExist:
        return f"Appointment ID {appointment_id} not found"





