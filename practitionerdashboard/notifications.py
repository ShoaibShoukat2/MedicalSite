"""
Notification System for Medical Platform
Handles email and SMS notifications for appointments
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from patientdashboard.models import Notification
import requests
import json

def create_notification(user_type, user_id, title, message, notification_type='info'):
    """Create a notification in the database"""
    try:
        notification = Notification.objects.create(
            user_type=user_type,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )
        return notification
    except Exception as e:
        print(f"Error creating notification: {str(e)}")
        return None

def send_email_notification(to_email, subject, template_name, context):
    """Send email notification"""
    try:
        html_message = render_to_string(template_name, context)
        
        send_mail(
            subject=subject,
            message='',  # Plain text version
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_sms_notification(phone_number, message):
    """Send SMS notification (placeholder for SMS service integration)"""
    try:
        # This is a placeholder - integrate with your SMS service
        # Example: Twilio, AWS SNS, etc.
        print(f"SMS to {phone_number}: {message}")
        return True
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False

def notify_appointment_booked(appointment):
    """Notify both patient and practitioner about new appointment"""
    
    # Notify Patient
    patient_title = "Appointment Booked Successfully"
    patient_message = f"Your appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} has been booked for {appointment.slot.start_time.strftime('%B %d, %Y at %I:%M %p')}."
    
    create_notification(
        user_type='patient',
        user_id=appointment.patient.id,
        title=patient_title,
        message=patient_message,
        notification_type='success'
    )
    
    # Send email to patient
    if appointment.patient.email:
        send_email_notification(
            to_email=appointment.patient.email,
            subject=patient_title,
            template_name='emails/appointment_booked_patient.html',
            context={
                'patient': appointment.patient,
                'practitioner': appointment.practitioner,
                'appointment': appointment,
                'appointment_time': appointment.slot.start_time
            }
        )
    
    # Notify Practitioner
    practitioner_title = "New Appointment Request"
    practitioner_message = f"New appointment request from {appointment.patient.first_name} {appointment.patient.last_name} for {appointment.slot.start_time.strftime('%B %d, %Y at %I:%M %p')}."
    
    create_notification(
        user_type='practitioner',
        user_id=appointment.practitioner.id,
        title=practitioner_title,
        message=practitioner_message,
        notification_type='info'
    )
    
    # Send email to practitioner
    if appointment.practitioner.email:
        send_email_notification(
            to_email=appointment.practitioner.email,
            subject=practitioner_title,
            template_name='emails/appointment_request_practitioner.html',
            context={
                'patient': appointment.patient,
                'practitioner': appointment.practitioner,
                'appointment': appointment,
                'appointment_time': appointment.slot.start_time
            }
        )

def notify_appointment_accepted(appointment):
    """Notify patient when appointment is accepted"""
    
    title = "Appointment Confirmed"
    message = f"Your appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} has been confirmed for {appointment.slot.start_time.strftime('%B %d, %Y at %I:%M %p')}."
    
    # Add Zoom meeting info if available
    if appointment.video_call_link:
        message += f" Zoom meeting link: {appointment.video_call_link}"
        if appointment.meeting_id:
            message += f" Meeting ID: {appointment.meeting_id}"
        if appointment.meeting_password:
            message += f" Password: {appointment.meeting_password}"
    
    create_notification(
        user_type='patient',
        user_id=appointment.patient.id,
        title=title,
        message=message,
        notification_type='success'
    )
    
    # Send email
    if appointment.patient.email:
        send_email_notification(
            to_email=appointment.patient.email,
            subject=title,
            template_name='emails/appointment_confirmed.html',
            context={
                'patient': appointment.patient,
                'practitioner': appointment.practitioner,
                'appointment': appointment,
                'appointment_time': appointment.slot.start_time,
                'zoom_join_url': appointment.video_call_link,
                'zoom_meeting_id': appointment.meeting_id,
                'zoom_password': appointment.meeting_password
            }
        )
    
    # Send SMS if phone number available
    if hasattr(appointment.patient, 'phone') and appointment.patient.phone:
        sms_message = f"Appointment confirmed with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} on {appointment.slot.start_time.strftime('%m/%d/%Y at %I:%M %p')}."
        if appointment.video_call_link:
            sms_message += f" Zoom: {appointment.video_call_link}"
            if appointment.meeting_id:
                sms_message += f" ID: {appointment.meeting_id}"
        send_sms_notification(appointment.patient.phone, sms_message)

def notify_appointment_cancelled(appointment, reason=""):
    """Notify patient when appointment is cancelled"""
    
    title = "Appointment Cancelled"
    message = f"Your appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} scheduled for {appointment.slot.start_time.strftime('%B %d, %Y at %I:%M %p')} has been cancelled."
    
    if reason:
        message += f" Reason: {reason}"
    
    create_notification(
        user_type='patient',
        user_id=appointment.patient.id,
        title=title,
        message=message,
        notification_type='warning'
    )
    
    # Send email
    if appointment.patient.email:
        send_email_notification(
            to_email=appointment.patient.email,
            subject=title,
            template_name='emails/appointment_cancelled.html',
            context={
                'patient': appointment.patient,
                'practitioner': appointment.practitioner,
                'appointment': appointment,
                'appointment_time': appointment.slot.start_time,
                'reason': reason
            }
        )
    
    # Send SMS
    if hasattr(appointment.patient, 'phone') and appointment.patient.phone:
        sms_message = f"Appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} on {appointment.slot.start_time.strftime('%m/%d/%Y at %I:%M %p')} has been cancelled."
        send_sms_notification(appointment.patient.phone, sms_message)

def notify_new_availability(practitioner, new_slots):
    """Notify waiting list patients about new availability"""
    
    # Get patients on waiting list for this practitioner
    waiting_appointments = Appointment.objects.filter(
        practitioner=practitioner,
        status='Pending'
    ).select_related('patient')
    
    for appointment in waiting_appointments:
        title = "New Appointment Slots Available"
        message = f"Dr. {practitioner.first_name} {practitioner.last_name} has new available slots. You may be able to reschedule your appointment earlier."
        
        create_notification(
            user_type='patient',
            user_id=appointment.patient.id,
            title=title,
            message=message,
            notification_type='info'
        )
        
        # Send email
        if appointment.patient.email:
            send_email_notification(
                to_email=appointment.patient.email,
                subject=title,
                template_name='emails/new_availability.html',
                context={
                    'patient': appointment.patient,
                    'practitioner': practitioner,
                    'new_slots': new_slots
                }
            )

def notify_appointment_reminder(appointment, hours_before=24):
    """Send appointment reminder"""
    
    title = f"Appointment Reminder - {hours_before} hours"
    message = f"Reminder: You have an appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} tomorrow at {appointment.slot.start_time.strftime('%I:%M %p')}."
    
    create_notification(
        user_type='patient',
        user_id=appointment.patient.id,
        title=title,
        message=message,
        notification_type='info'
    )
    
    # Send email
    if appointment.patient.email:
        send_email_notification(
            to_email=appointment.patient.email,
            subject=title,
            template_name='emails/appointment_reminder.html',
            context={
                'patient': appointment.patient,
                'practitioner': appointment.practitioner,
                'appointment': appointment,
                'appointment_time': appointment.slot.start_time,
                'hours_before': hours_before
            }
        )