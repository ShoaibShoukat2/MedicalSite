"""
Enhanced Notification System for Medical Platform
Handles email notifications and in-app notifications for appointments
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from patientdashboard.models import Notification
from practitionerdashboard.models import PractitionerNotification
import requests
import json
from django.utils import timezone
from datetime import timedelta

def create_patient_notification(patient, title, message, notification_type='info', url=None):
    """Create a notification for a patient"""
    try:
        notification = Notification.objects.create(
            recipient=patient,
            title=title,
            message=message,
            notification_type=notification_type,
            url=url
        )
        return notification
    except Exception as e:
        print(f"Error creating patient notification: {str(e)}")
        return None

def create_practitioner_notification(practitioner, title, message, notification_type='info', url=None):
    """Create a notification for a practitioner"""
    try:
        notification = PractitionerNotification.objects.create(
            recipient=practitioner,
            title=title,
            message=message,
            notification_type=notification_type,
            url=url
        )
        return notification
    except Exception as e:
        print(f"Error creating practitioner notification: {str(e)}")
        return None

def send_email_notification(to_email, subject, template_name, context, language='fr'):
    """Send email notification with language support (default: French)"""
    try:
        # Add request context for URLs
        context.update({
            'settings': settings,
        })
        
        # Try to use language-specific template first (French by default)
        if language and language != 'en':
            localized_template = f'emails/{language}/{template_name.replace("emails/", "")}'
            try:
                # Check if localized template exists
                from django.template.loader import get_template
                get_template(localized_template)
                template_name = localized_template
                print(f"📧 Using {language.upper()} template: {localized_template}")
            except:
                print(f"⚠️ {language.upper()} template not found, using default: {template_name}")
        
        html_message = render_to_string(template_name, context)
        
        # Translate subject to French if using French template
        if language == 'fr':
            subject = translate_subject_to_french(subject)
        
        send_mail(
            subject=subject,
            message='',  # Plain text version
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"✅ Email sent successfully to {to_email} in {language.upper()}")
        return True
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {str(e)}")
        return False

def translate_subject_to_french(subject):
    """Translate common email subjects to French"""
    translations = {
        'Appointment Booked': 'Rendez-vous Réservé',
        'Appointment Confirmed': 'Rendez-vous Confirmé',
        'Appointment Cancelled': 'Rendez-vous Annulé',
        'Patient Cancelled Appointment': 'Patient a Annulé le Rendez-vous',
        'Appointment Cancellation Confirmed': 'Annulation de Rendez-vous Confirmée',
        'Appointment Reminder': 'Rappel de Rendez-vous',
        'Appointment Modified': 'Rendez-vous Modifié',
        'New Availability': 'Nouvelle Disponibilité',
        'Appointment Request': 'Demande de Rendez-vous',
    }
    return translations.get(subject, subject)

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
    
    create_patient_notification(
        patient=appointment.patient,
        title=patient_title,
        message=patient_message,
        notification_type='success',
        url=f'/patient-dashboard/appointments/'
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
    
    create_practitioner_notification(
        practitioner=appointment.practitioner,
        title=practitioner_title,
        message=practitioner_message,
        notification_type='info',
        url=f'/practitioner-dashboard/dashboard/'
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
        message += f" Video consultation link has been provided."
    
    create_patient_notification(
        patient=appointment.patient,
        title=title,
        message=message,
        notification_type='success',
        url=f'/patient-dashboard/appointments/'
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
            sms_message += f" Video link provided in email."
        send_sms_notification(appointment.patient.phone, sms_message)

def notify_appointment_cancelled(appointment, reason="", cancelled_by="system"):
    """Notify patient and practitioner when appointment is cancelled with separate, appropriate messages"""
    
    # Prevent duplicate notifications - check if already cancelled
    if appointment.status != "Cancelled":
        print(f"⚠️ Warning: Trying to send cancellation notification for appointment {appointment.id} that is not cancelled (status: {appointment.status})")
        return
    
    print(f"📧 Sending cancellation notifications for appointment {appointment.id} (cancelled by: {cancelled_by})")
    
    # Always notify the patient about cancellation
    patient_title = "Appointment Cancelled"
    patient_message = f"Your appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} scheduled for {appointment.slot.start_time.strftime('%B %d, %Y at %I:%M %p')} has been cancelled."
    
    if reason:
        patient_message += f" Reason: {reason}"
    
    # Create in-app notification for patient
    create_patient_notification(
        patient=appointment.patient,
        title=patient_title,
        message=patient_message,
        notification_type='warning',
        url=f'/patient-dashboard/appointments/'
    )
    
    # Send email to patient using patient-specific template
    if appointment.patient.email:
        print(f"📤 Sending patient email to: {appointment.patient.email}")
        send_email_notification(
            to_email=appointment.patient.email,
            subject=patient_title,
            template_name='emails/appointment_cancelled_patient.html',
            context={
                'patient': appointment.patient,
                'practitioner': appointment.practitioner,
                'appointment': appointment,
                'appointment_time': appointment.slot.start_time,
                'reason': reason,
                'cancelled_by': cancelled_by
            }
        )
    
    # Always notify practitioner about cancellation (different message based on who cancelled)
    if cancelled_by == "patient":
        practitioner_title = "Patient Cancelled Appointment"
        practitioner_message = f"Patient {appointment.patient.first_name} {appointment.patient.last_name} has cancelled their appointment scheduled for {appointment.slot.start_time.strftime('%B %d, %Y at %I:%M %p')}."
    else:
        practitioner_title = "Appointment Cancellation Confirmed"
        practitioner_message = f"You have successfully cancelled the appointment with {appointment.patient.first_name} {appointment.patient.last_name} scheduled for {appointment.slot.start_time.strftime('%B %d, %Y at %I:%M %p')}."
    
    if reason:
        practitioner_message += f" Reason: {reason}"
    
    # Create in-app notification for practitioner
    create_practitioner_notification(
        practitioner=appointment.practitioner,
        title=practitioner_title,
        message=practitioner_message,
        notification_type='info' if cancelled_by == "patient" else 'success',
        url=f'/practitioner-dashboard/dashboard/'
    )
    
    # Send email to practitioner using practitioner-specific template
    if appointment.practitioner.email:
        print(f"📤 Sending practitioner email to: {appointment.practitioner.email}")
        send_email_notification(
            to_email=appointment.practitioner.email,
            subject=practitioner_title,
            template_name='emails/appointment_cancelled_practitioner.html',
            context={
                'patient': appointment.patient,
                'practitioner': appointment.practitioner,
                'appointment': appointment,
                'appointment_time': appointment.slot.start_time,
                'reason': reason,
                'cancelled_by': cancelled_by
            }
        )
    
    # Send SMS to patient (only if patient has phone number)
    if hasattr(appointment.patient, 'mobile_phone') and appointment.patient.mobile_phone:
        if cancelled_by == "practitioner":
            sms_message = f"Your appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} on {appointment.slot.start_time.strftime('%m/%d/%Y at %I:%M %p')} has been cancelled by the doctor."
        else:
            sms_message = f"Your appointment cancellation with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} on {appointment.slot.start_time.strftime('%m/%d/%Y at %I:%M %p')} has been confirmed."
        
        if reason:
            sms_message += f" Reason: {reason}"
            
        send_sms_notification(appointment.patient.mobile_phone, sms_message)
    
    print(f"✅ Cancellation notifications sent successfully for appointment {appointment.id}")

def notify_appointment_modified(appointment, old_time=None, reason=""):
    """Notify patient when appointment is modified"""
    
    title = "Appointment Modified"
    message = f"Your appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} has been rescheduled to {appointment.slot.start_time.strftime('%B %d, %Y at %I:%M %p')}."
    
    if reason:
        message += f" Reason: {reason}"
    
    create_patient_notification(
        patient=appointment.patient,
        title=title,
        message=message,
        notification_type='info',
        url=f'/patient-dashboard/appointments/'
    )
    
    # Send email
    if appointment.patient.email:
        send_email_notification(
            to_email=appointment.patient.email,
            subject=title,
            template_name='emails/appointment_modified.html',
            context={
                'patient': appointment.patient,
                'practitioner': appointment.practitioner,
                'appointment': appointment,
                'appointment_time': appointment.slot.start_time,
                'old_time': old_time,
                'reason': reason
            }
        )
    
    # Send SMS
    if hasattr(appointment.patient, 'phone') and appointment.patient.phone:
        sms_message = f"Appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} rescheduled to {appointment.slot.start_time.strftime('%m/%d/%Y at %I:%M %p')}."
        send_sms_notification(appointment.patient.phone, sms_message)

def notify_new_availability(practitioner, new_slots):
    """Notify waiting list patients about new availability"""
    
    # Import here to avoid circular imports
    from patientdashboard.models import Appointment
    
    # Get patients on waiting list for this practitioner
    waiting_appointments = Appointment.objects.filter(
        practitioner=practitioner,
        status='Pending'
    ).select_related('patient')
    
    # Also notify patients who have shown interest (you can customize this logic)
    interested_patients = []
    
    all_patients = list(waiting_appointments.values_list('patient', flat=True)) + interested_patients
    
    for appointment in waiting_appointments:
        title = "New Appointment Slots Available"
        message = f"Dr. {practitioner.first_name} {practitioner.last_name} has new available slots. You may be able to reschedule your appointment earlier."
        
        create_patient_notification(
            patient=appointment.patient,
            title=title,
            message=message,
            notification_type='info',
            url=f'/patient-dashboard/practitioner/{practitioner.id}/slots/'
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
    if hours_before == 24:
        time_text = "tomorrow"
    elif hours_before == 2:
        time_text = "in 2 hours"
    elif hours_before == 1:
        time_text = "in 1 hour"
    else:
        time_text = f"in {hours_before} hours"
    
    message = f"Reminder: You have an appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} {time_text} at {appointment.slot.start_time.strftime('%I:%M %p')}."
    
    create_patient_notification(
        patient=appointment.patient,
        title=title,
        message=message,
        notification_type='info',
        url=f'/patient-dashboard/appointments/'
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
    
    # Send SMS
    if hasattr(appointment.patient, 'phone') and appointment.patient.phone:
        sms_message = f"Reminder: Appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} {time_text} at {appointment.slot.start_time.strftime('%I:%M %p')}."
        if appointment.video_call_link:
            sms_message += f" Video link in email."
        send_sms_notification(appointment.patient.phone, sms_message)

def send_bulk_availability_notifications(practitioner, new_slots):
    """Send notifications to multiple patients about new availability"""
    
    # Import here to avoid circular imports
    from patientdashboard.models import Appointment
    
    # Get all patients who might be interested
    # This could include patients with pending appointments, past patients, etc.
    
    # Patients with pending appointments for this practitioner
    pending_patients = Appointment.objects.filter(
        practitioner=practitioner,
        status='Pending'
    ).select_related('patient').values_list('patient', flat=True)
    
    # You could also add logic for:
    # - Patients who have had appointments with this practitioner before
    # - Patients who have shown interest in this specialty
    # - Patients on a waiting list
    
    for patient_id in pending_patients:
        try:
            from user_account.models import Patient
            patient = Patient.objects.get(id=patient_id)
            
            title = "New Appointment Slots Available"
            message = f"Dr. {practitioner.first_name} {practitioner.last_name} has added new appointment slots. Book now to get an earlier appointment!"
            
            create_patient_notification(
                patient=patient,
                title=title,
                message=message,
                notification_type='info',
                url=f'/patient-dashboard/practitioner/{practitioner.id}/slots/'
            )
            
            # Send email
            if patient.email:
                send_email_notification(
                    to_email=patient.email,
                    subject=title,
                    template_name='emails/new_availability.html',
                    context={
                        'patient': patient,
                        'practitioner': practitioner,
                        'new_slots': new_slots
                    }
                )
        except Exception as e:
            print(f"Error sending availability notification to patient {patient_id}: {str(e)}")

# Utility functions for scheduled reminders
def send_daily_reminders():
    """Send reminders for appointments happening in 24 hours"""
    # Import here to avoid circular imports
    from patientdashboard.models import Appointment
    
    tomorrow = timezone.now() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        slot__start_time__date=tomorrow.date(),
        status='Accepted'
    ).select_related('patient', 'practitioner')
    
    for appointment in appointments:
        notify_appointment_reminder(appointment, hours_before=24)

def send_hourly_reminders():
    """Send reminders for appointments happening in 2 hours"""
    # Import here to avoid circular imports
    from patientdashboard.models import Appointment
    
    in_two_hours = timezone.now() + timedelta(hours=2)
    appointments = Appointment.objects.filter(
        slot__start_time__range=[
            in_two_hours - timedelta(minutes=30),
            in_two_hours + timedelta(minutes=30)
        ],
        status='Accepted'
    ).select_related('patient', 'practitioner')
    
    for appointment in appointments:
        notify_appointment_reminder(appointment, hours_before=2)