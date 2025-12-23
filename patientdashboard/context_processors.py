# patientdashboard/context_processors.py

from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment, Notification
from practitionerdashboard.models import Prescription
from user_account.models import Patient

def patient_notifications(request):
    """
    Context processor to provide notification data to all templates
    """
    context = {
        'notifications_count': 0,
        'recent_notifications': [],
    }
    
    # Only process if patient is logged in
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return context
    
    try:
        patient = Patient.objects.get(id=patient_id)
        
        # Get all notifications for this patient
        notifications = []
        
        # 1. Pending Appointments (next 7 days)
        upcoming_appointments = Appointment.objects.filter(
            patient=patient,
            status='Pending',
            slot__date__gte=timezone.now().date(),
            slot__date__lte=timezone.now().date() + timedelta(days=7)
        ).select_related('practitioner', 'slot').order_by('slot__date', 'slot__start_time')
        
        for appointment in upcoming_appointments:
            time_diff = appointment.slot.date - timezone.now().date()
            if time_diff.days == 0:
                time_ago = "Today"
            elif time_diff.days == 1:
                time_ago = "Tomorrow"
            else:
                time_ago = f"{time_diff.days}d"
                
            notifications.append({
                'id': appointment.id,
                'type': 'appointment',
                'title': 'Upcoming Appointment',
                'message': f"Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} - {appointment.slot.date.strftime('%b %d')} at {appointment.slot.start_time.strftime('%I:%M %p')}",
                'subtitle': appointment.practitioner.get_specialty_display(),
                'icon': 'calendar-check',
                'color': 'patient-blue',
                'time_ago': time_ago,
                'is_read': False,
                'url': '/patient-dashboard/appointments_patients/',
                'created_at': appointment.created_at
            })
        
        # 2. Accepted Appointments
        accepted_appointments = Appointment.objects.filter(
            patient=patient,
            status='Accepted',
            slot__date__gte=timezone.now().date()
        ).select_related('practitioner', 'slot').order_by('-created_at')[:3]
        
        for appointment in accepted_appointments:
            time_diff = timezone.now() - appointment.created_at
            if time_diff.days == 0:
                time_ago = f"{time_diff.seconds // 3600}h"
            else:
                time_ago = f"{time_diff.days}d"
                
            notifications.append({
                'id': appointment.id,
                'type': 'appointment',
                'title': 'Appointment Confirmed',
                'message': f"Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} - {appointment.slot.date.strftime('%b %d')}, {appointment.slot.start_time.strftime('%I:%M %p')}",
                'subtitle': appointment.practitioner.get_specialty_display(),
                'icon': 'calendar-plus',
                'color': 'patient-green',
                'time_ago': time_ago,
                'is_read': False,
                'url': '/patient-dashboard/appointments_patients/',
                'created_at': appointment.created_at
            })
        
        # 3. Recent Prescriptions
        recent_prescriptions = Prescription.objects.filter(
            patient=patient,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).select_related('practitioner').order_by('-created_at')[:2]
        
        for prescription in recent_prescriptions:
            time_diff = timezone.now() - prescription.created_at
            if time_diff.days == 0:
                time_ago = f"{time_diff.seconds // 3600}h"
            else:
                time_ago = f"{time_diff.days}d"
                
            notifications.append({
                'id': prescription.id,
                'type': 'prescription',
                'title': 'New Prescription',
                'message': f"Dr. {prescription.practitioner.first_name} {prescription.practitioner.last_name} prescribed new medication",
                'subtitle': 'Ready for pickup at pharmacy',
                'icon': 'prescription-bottle',
                'color': 'patient-orange',
                'time_ago': time_ago,
                'is_read': False,
                'url': '/patient-dashboard/appointments_patients/',
                'created_at': prescription.created_at
            })
        
        # 4. Database Notifications
        db_notifications = Notification.objects.filter(
            recipient=patient,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-created_at')[:3]
        
        for notification in db_notifications:
            time_diff = timezone.now() - notification.created_at
            if time_diff.days == 0:
                if time_diff.seconds < 3600:
                    time_ago = f"{time_diff.seconds // 60}m"
                else:
                    time_ago = f"{time_diff.seconds // 3600}h"
            else:
                time_ago = f"{time_diff.days}d"
                
            notifications.append({
                'id': notification.id,
                'type': 'message',
                'title': 'New Message',
                'message': notification.message[:50] + "..." if len(notification.message) > 50 else notification.message,
                'subtitle': 'Click to view details',
                'icon': 'comment-medical',
                'color': 'patient-teal',
                'time_ago': time_ago,
                'is_read': notification.is_read,
                'url': notification.url or '/patient-dashboard/chat/',
                'created_at': notification.created_at
            })
        
        # Sort all notifications by creation time (most recent first)
        notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Take only the most recent 5 notifications
        recent_notifications = notifications[:5]
        
        # Count unread notifications
        unread_count = len([n for n in notifications if not n['is_read']])
        
        context = {
            'notifications_count': unread_count,
            'recent_notifications': recent_notifications,
        }
        
    except Patient.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error in patient_notifications context processor: {e}")
    
    return context