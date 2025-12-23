"""
Unified Video Consultation System
Supports both Jitsi Meet and Zoom integration
"""

import uuid
import requests
import json
from django.conf import settings
from datetime import datetime, timedelta

def generate_jitsi_room(appointment):
    """Generate Jitsi Meet room for appointment"""
    # Create unique room name
    room_name = f"medical-{appointment.id}-{uuid.uuid4().hex[:8]}"
    
    # Jitsi Meet URL
    jitsi_url = f"https://meet.jit.si/{room_name}"
    
    # Room configuration
    room_config = {
        'roomName': room_name,
        'displayName': f"Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name}",
        'subject': f"Medical Consultation - {appointment.patient.first_name} {appointment.patient.last_name}",
        'password': None,  # Can add password if needed
        'startWithAudioMuted': False,
        'startWithVideoMuted': False,
    }
    
    return {
        'platform': 'jitsi',
        'room_url': jitsi_url,
        'room_name': room_name,
        'config': room_config,
        'practitioner_url': jitsi_url,
        'patient_url': jitsi_url,
    }

def generate_zoom_meeting(appointment):
    """Generate Zoom meeting for appointment (requires Zoom API)"""
    try:
        # This requires Zoom API credentials
        # For now, return a placeholder structure
        meeting_id = f"medical-{appointment.id}-{uuid.uuid4().hex[:8]}"
        
        # In production, you would call Zoom API here
        # zoom_response = create_zoom_meeting(appointment)
        
        return {
            'platform': 'zoom',
            'meeting_id': meeting_id,
            'join_url': f"https://zoom.us/j/{meeting_id}",
            'password': None,
            'practitioner_url': f"https://zoom.us/j/{meeting_id}?role=1",  # Host
            'patient_url': f"https://zoom.us/j/{meeting_id}?role=0",       # Participant
        }
    except Exception as e:
        print(f"Error creating Zoom meeting: {str(e)}")
        # Fallback to Jitsi
        return generate_jitsi_room(appointment)

def create_video_consultation(appointment, platform='jitsi'):
    """Create video consultation room for appointment"""
    
    if platform.lower() == 'zoom':
        return generate_zoom_meeting(appointment)
    else:
        # Default to Jitsi (more reliable, no API key needed)
        return generate_jitsi_room(appointment)

def get_video_consultation_info(appointment):
    """Get existing video consultation info or create new one"""
    
    # Check if appointment already has video info
    if hasattr(appointment, 'video_call_link') and appointment.video_call_link:
        # Parse existing video info
        if 'jitsi' in appointment.video_call_link or 'meet.jit.si' in appointment.video_call_link:
            return {
                'platform': 'jitsi',
                'room_url': appointment.video_call_link,
                'practitioner_url': appointment.video_call_link,
                'patient_url': appointment.video_call_link,
            }
        elif 'zoom' in appointment.video_call_link:
            return {
                'platform': 'zoom',
                'join_url': appointment.video_call_link,
                'practitioner_url': appointment.video_call_link,
                'patient_url': appointment.video_call_link,
            }
    
    # Create new video consultation
    video_info = create_video_consultation(appointment, platform='jitsi')
    
    # Save video link to appointment
    appointment.video_call_link = video_info.get('room_url') or video_info.get('join_url')
    appointment.save()
    
    return video_info

def start_video_consultation(appointment_id, user_type='practitioner'):
    """Start video consultation and return appropriate URL"""
    from patientdashboard.models import Appointment
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Get or create video consultation
        video_info = get_video_consultation_info(appointment)
        
        # Return appropriate URL based on user type
        if user_type == 'practitioner':
            return video_info.get('practitioner_url') or video_info.get('room_url') or video_info.get('join_url')
        else:
            return video_info.get('patient_url') or video_info.get('room_url') or video_info.get('join_url')
            
    except Exception as e:
        print(f"Error starting video consultation: {str(e)}")
        return None

def end_video_consultation(appointment_id):
    """End video consultation and cleanup"""
    try:
        from patientdashboard.models import Appointment
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Mark consultation as completed
        appointment.consultation_completed = True
        appointment.consultation_end_time = datetime.now()
        appointment.save()
        
        return True
    except Exception as e:
        print(f"Error ending video consultation: {str(e)}")
        return False