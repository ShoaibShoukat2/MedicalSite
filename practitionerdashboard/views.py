import uuid
import requests
import json
import base64
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import render, redirect,get_object_or_404
from user_account.models import Patient, Practitioner
from datetime import date, datetime, timedelta

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from user_account.models import Practitioner
from .models import AvailableSlot
import json
from django.shortcuts import render, get_object_or_404, redirect
from user_account.models import Practitioner

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from patientdashboard.models import Appointment, Notification
from django.http import JsonResponse
from datetime import date
from practitionerdashboard.models import Prescription
from django.contrib import messages
from patientdashboard.models import Review, Reply
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt

# Zoom API Configuration
ZOOM_API_KEY = getattr(settings, 'ZOOM_API_KEY', None)
ZOOM_API_SECRET = getattr(settings, 'ZOOM_API_SECRET', None)
ZOOM_JWT_TOKEN = getattr(settings, 'ZOOM_JWT_TOKEN', None)

# Check if Zoom is properly configured
ZOOM_CONFIGURED = all([ZOOM_API_KEY, ZOOM_API_SECRET, ZOOM_JWT_TOKEN]) and \
                  ZOOM_API_KEY != 'your_zoom_api_key' and \
                  ZOOM_API_SECRET != 'your_zoom_api_secret' and \
                  ZOOM_JWT_TOKEN != 'your_zoom_jwt_token'

def create_zoom_meeting(topic, start_time, duration=60):
    """Create a Zoom meeting and return meeting details"""
    if not ZOOM_CONFIGURED:
        return {
            'success': False,
            'error': 'Zoom API not configured. Please set up Zoom credentials in settings.'
        }
    
    try:
        # Zoom API endpoint
        url = "https://api.zoom.us/v2/users/me/meetings"
        
        # Headers
        headers = {
            'Authorization': f'Bearer {ZOOM_JWT_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Meeting data
        meeting_data = {
            "topic": topic,
            "type": 2,  # Scheduled meeting
            "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "duration": duration,
            "timezone": "UTC",
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "watermark": False,
                "use_pmi": False,
                "approval_type": 0,
                "audio": "both",
                "auto_recording": "none"
            }
        }
        
        # Make API request
        response = requests.post(url, headers=headers, json=meeting_data, timeout=10)
        
        if response.status_code == 201:
            meeting_info = response.json()
            return {
                'success': True,
                'meeting_id': meeting_info['id'],
                'join_url': meeting_info['join_url'],
                'start_url': meeting_info['start_url'],
                'password': meeting_info.get('password', ''),
                'meeting_data': meeting_info
            }
        else:
            print(f"Zoom API Error: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': f"Zoom API Error: {response.status_code} - {response.text}"
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': "Zoom API request timed out"
        }
    except requests.exceptions.RequestException as e:
        print(f"Zoom API Request Error: {str(e)}")
        return {
            'success': False,
            'error': f"Zoom API Request Error: {str(e)}"
        }
    except Exception as e:
        print(f"Error creating Zoom meeting: {str(e)}")
        return {
            'success': False,
            'error': f"Error creating Zoom meeting: {str(e)}"
        }

def create_fallback_meeting(appointment):
    """Create a fallback meeting link using Jitsi Meet"""
    try:
        # Create a unique meeting room name
        meeting_id = f"medical-{appointment.id}-{appointment.patient.id}-{appointment.practitioner.id}"
        
        # Create Jitsi Meet URL
        join_url = f"https://meet.jit.si/{meeting_id}"
        
        return {
            'success': True,
            'meeting_id': meeting_id,
            'join_url': join_url,
            'start_url': join_url,  # Same URL for host and participant in Jitsi
            'password': '',
            'provider': 'jitsi'
        }
    except Exception as e:
        print(f"Error creating fallback meeting: {str(e)}")
        return {
            'success': False,
            'error': f"Error creating fallback meeting: {str(e)}"
        }

def generate_zoom_meeting_for_appointment(appointment):
    """Generate meeting for an appointment (Zoom or fallback)"""
    try:
        # Create meeting topic
        topic = f"Medical Consultation - Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} & {appointment.patient.first_name} {appointment.patient.last_name}"
        
        # Use appointment slot time
        start_time = appointment.slot.start_time
        
        # Try Zoom first if configured
        if ZOOM_CONFIGURED:
            print(f"🔄 Attempting to create Zoom meeting for appointment {appointment.id}")
            zoom_result = create_zoom_meeting(topic, start_time, duration=60)
            
            if zoom_result['success']:
                print(f"✅ Zoom meeting created successfully for appointment {appointment.id}")
                # Save meeting details to appointment
                appointment.video_call_link = zoom_result['join_url']
                appointment.meeting_id = zoom_result['meeting_id']
                appointment.meeting_password = zoom_result['password']
                appointment.host_start_url = zoom_result['start_url']
                appointment.save()
                
                return {
                    'success': True,
                    'join_url': zoom_result['join_url'],
                    'meeting_id': zoom_result['meeting_id'],
                    'password': zoom_result['password'],
                    'start_url': zoom_result['start_url'],
                    'provider': 'zoom'
                }
            else:
                print(f"⚠️ Zoom meeting creation failed: {zoom_result['error']}")
        else:
            print(f"⚠️ Zoom not configured, using fallback for appointment {appointment.id}")
        
        # Use fallback meeting system
        print(f"🔄 Creating fallback meeting for appointment {appointment.id}")
        fallback_result = create_fallback_meeting(appointment)
        
        if fallback_result['success']:
            print(f"✅ Fallback meeting created successfully for appointment {appointment.id}")
            # Save meeting details to appointment
            appointment.video_call_link = fallback_result['join_url']
            appointment.meeting_id = fallback_result['meeting_id']
            appointment.meeting_password = fallback_result['password']
            appointment.host_start_url = fallback_result['start_url']
            appointment.save()
            
            return {
                'success': True,
                'join_url': fallback_result['join_url'],
                'meeting_id': fallback_result['meeting_id'],
                'password': fallback_result['password'],
                'start_url': fallback_result['start_url'],
                'provider': 'jitsi'
            }
        else:
            return fallback_result
            
    except Exception as e:
        print(f"❌ Error in generate_zoom_meeting_for_appointment: {str(e)}")
        return {
            'success': False,
            'error': f"Error generating meeting: {str(e)}"
        }

# Create your views here.




def dashboard_view(request):
    # Get the practitioner ID from the session
    practitioner_id = request.session.get('practitioner_id')
    
    # Ensure practitioner_id exists in the session
    if not practitioner_id:
        # Handle the case where no practitioner is logged in
        return render(request, 'practitionerdashboard/dashboard.html', {
            'error': 'No practitioner found in session.'
        })
    
    # Check if the practitioner has photo, price, and description in their profile
    practitioner = Practitioner.objects.filter(id=practitioner_id).first()
    
    if not practitioner or not practitioner.photo or not practitioner.price or not practitioner.description:
        # Send error message and redirect to complete profile page
        return render(request, 'practitionerdashboard/dashboard.html', {
            'error': 'Please complete your profile by adding a photo, price, and description.',
            'redirect_url': '/practitioner-profile/'  # URL for completing the profile
        })

    # Count total patients
    total_patients = Appointment.objects.filter(
        practitioner_id=practitioner_id
    ).exclude(status="Cancelled").count()

    # Get unread message count
    from chat.models import ChatRoom, Message
    try:
        unread_messages_count = Message.objects.filter(
            chat_room__practitioner_id=practitioner_id,
            sender_type='patient',
            is_read=False
        ).count()
    except:
        unread_messages_count = 0


    
    
    
    print("Total Patient:",total_patients)

    # Count completed appointments
    completed_appointments = Appointment.objects.filter(practitioner_id=practitioner_id, status="Accepted").count()

    # Count pending appointments
    pending_appointments = Appointment.objects.filter(practitioner_id=practitioner_id, status="Pending").count()

    # Get current date and time in local timezone
    from django.utils import timezone as django_timezone
    
    # Get current time aware of timezone
    now_time = django_timezone.now()
    today = django_timezone.localdate()  # Get local date
    
    # Create today's start and end datetime
    today_start = django_timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_end = django_timezone.make_aware(datetime.combine(today, datetime.max.time()))
    
    # 24 hours from now
    twenty_four_hours_later = now_time + timedelta(hours=24)

    # Today's appointments (appointments for today excluding cancelled)
    today_appointments = Appointment.objects.filter(
        slot__start_time__range=(today_start, today_end),
        practitioner_id=practitioner_id,
    ).exclude(status='Cancelled').order_by('slot__start_time')
    
    # Today's accepted appointments only (for Today's Appointments tab)
    today_accepted_appointments = today_appointments.filter(status='Accepted')
    
    # Accepted appointments (status = Accepted)
    accepted_appointments = Appointment.objects.filter(
        practitioner_id=practitioner_id,
        status='Accepted',
        amount=practitioner.price
    ).order_by('slot__start_time')
    
    # Waiting list (all appointments with status = Pending)
    waiting_list_appointments = Appointment.objects.filter(
        status='Pending',
        practitioner_id=practitioner_id,
    ).order_by('slot__start_time')

    return render(request, 'practitionerdashboard/dashboard.html', {
        'practitioner': practitioner,
        'today_appointments': today_appointments,
        'today_accepted_appointments': today_accepted_appointments,
        'waiting_list_appointments': waiting_list_appointments,
        'accepted_appointments': accepted_appointments,
        'total_patients': total_patients,
        'completed_appointments': completed_appointments,
        'pending_appointments': pending_appointments,
        'unread_messages_count': unread_messages_count,
    })






from django.core.mail import send_mail
from django.contrib import messages





def accept_appointment(request, appointment_id):
    """Accept appointment with enhanced notifications, meeting setup, and chat room creation"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = "Accepted"
    
    # Always save the appointment status first
    appointment.save()
    print(f"✅ Appointment {appointment_id} status set to Accepted")
    
    # Generate meeting if not exists
    if not appointment.video_call_link:
        meeting_result = generate_zoom_meeting_for_appointment(appointment)
        if meeting_result['success']:
            provider = meeting_result.get('provider', 'unknown')
            print(f"✅ {provider.title()} meeting created for appointment {appointment_id}")
            if provider == 'zoom':
                messages.success(request, "Appointment accepted successfully! Zoom meeting created.")
            else:
                messages.success(request, "Appointment accepted successfully! Video meeting created.")
        else:
            print(f"⚠️ Failed to create meeting for appointment {appointment_id}: {meeting_result['error']}")
            messages.warning(request, "Appointment accepted successfully! Video call will be available shortly.")

    # Create chat room when appointment is accepted
    from chat.models import ChatRoom
    try:
        chat_room, created = ChatRoom.objects.get_or_create(
            patient=appointment.patient,
            practitioner=appointment.practitioner
        )
        
        if created:
            print(f"✅ Chat room created for {appointment.patient.first_name} and Dr. {appointment.practitioner.first_name}")
        else:
            print(f"✅ Chat room already exists for {appointment.patient.first_name} and Dr. {appointment.practitioner.first_name}")
    except Exception as e:
        print(f"⚠️ Failed to create chat room: {str(e)}")

    # Import notification functions
    try:
        from .notifications import notify_appointment_accepted
        # Send comprehensive notifications
        notify_appointment_accepted(appointment)
        print(f"✅ Notifications sent for appointment {appointment_id}")
    except Exception as e:
        print(f"⚠️ Failed to send notifications: {str(e)}")

    # Add frontend notification
    if appointment.video_call_link:
        messages.success(request, "Appointment accepted successfully! Video call and chat are now available.")
    else:
        messages.success(request, "Appointment accepted successfully! Chat is now available. Video call will be ready shortly.")

    return redirect('practitioner_dashboard:dashboard')



def cancel_appointment(request, appointment_id):
    """Cancel appointment with enhanced notifications and reason"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Get cancellation reason from request
    reason = request.POST.get('reason', 'No reason provided')
    
    # Import notification functions
    from .notifications import notify_appointment_cancelled
    
    # Send notifications before deleting
    notify_appointment_cancelled(appointment, reason)
    
    # Update status instead of deleting (for record keeping)
    appointment.status = "Cancelled"
    appointment.cancellation_reason = reason
    appointment.save()
    
    # Add frontend notification
    messages.success(request, f"Appointment cancelled successfully! Patient has been notified.")
    
    return redirect('practitioner_dashboard:dashboard')

    subject = 'Your Appointment Has Been Cancelled'
    message = f"""
    Dear {patient_name},

    Your appointment has been cancelled.

    - Date: {date}
    - Time: {time}
    - Practitioner: {practitioner_name}
    """
    send_mail(subject, message, 'shoaibahmadbhatti6252@gmail.com', [recipient_email])

    messages.info(request, "Appointment cancelled and email sent successfully.")

    return redirect('practitioner_dashboard:dashboard')



    
def get_patient_details(request, appointment_id):
    # Get the appointment object
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Fetch the associated patient
    patient = appointment.patient
    
    # Return the patient details as a JSON response
    patient_data = {
        'greeting': patient.greeting,
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'gender': patient.get_gender_display(),  # To display the human-readable gender
        'mobile_phone': patient.mobile_phone,
        'date_of_birth': patient.date_of_birth,
        'email': patient.email,
        'profile_photo': patient.profile_photo.url if patient.profile_photo else None,  # Return photo URL
    }

    return JsonResponse({'patient': patient_data})




def telemedicine(request):
    """Enhanced telemedicine view with unified video system"""
    practitioner_id = request.session.get('practitioner_id')
    
    if not practitioner_id:
        return redirect('frontend:practitioner_login')
    
    practitioner = get_object_or_404(Practitioner, id=practitioner_id)
    
    # Get today's accepted appointments for video calls
    from django.utils import timezone as django_timezone
    today = django_timezone.localdate()
    today_start = django_timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_end = django_timezone.make_aware(datetime.combine(today, datetime.max.time()))
    
    video_appointments = Appointment.objects.filter(
        practitioner_id=practitioner_id,
        status='Accepted',
        slot__start_time__range=(today_start, today_end)
    ).select_related('patient', 'slot').order_by('slot__start_time')
    
    context = {
        'practitioner': practitioner,
        'video_appointments': video_appointments,
        'total_video_calls': video_appointments.count(),
    }
    
    return render(request, 'practitionerdashboard/telemedicine.html', context)

def appointment(request):
    """Enhanced appointment view with proper data"""
    practitioner_id = request.session.get('practitioner_id')
    
    if not practitioner_id:
        return redirect('frontend:practitioner_login')
    
    practitioner = get_object_or_404(Practitioner, id=practitioner_id)
    
    # Get current time
    from django.utils import timezone as django_timezone
    now_time = django_timezone.now()
    today = django_timezone.localdate()
    
    # Create today's start and end datetime
    today_start = django_timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_end = django_timezone.make_aware(datetime.combine(today, datetime.max.time()))
    
    # Get all appointments for this practitioner
    all_appointments = Appointment.objects.filter(
        practitioner_id=practitioner_id
    ).select_related('patient', 'slot').order_by('-created_at')
    
    # Today's appointments
    today_appointments = all_appointments.filter(
        slot__start_time__range=(today_start, today_end)
    )
    
    # Pending appointments (need action)
    pending_appointments = all_appointments.filter(status='Pending')
    
    # Accepted appointments
    accepted_appointments = all_appointments.filter(status='Accepted')
    
    # Cancelled appointments
    cancelled_appointments = all_appointments.filter(status='Cancelled')
    
    # Upcoming appointments (next 7 days)
    next_week = today + timedelta(days=7)
    upcoming_appointments = all_appointments.filter(
        slot__date__range=(today, next_week),
        status__in=['Pending', 'Accepted']
    )
    
    context = {
        'practitioner': practitioner,
        'all_appointments': all_appointments,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'accepted_appointments': accepted_appointments,
        'cancelled_appointments': cancelled_appointments,
        'upcoming_appointments': upcoming_appointments,
        'total_appointments': all_appointments.count(),
        'pending_count': pending_appointments.count(),
        'accepted_count': accepted_appointments.count(),
        'today_count': today_appointments.count(),
    }
    
    return render(request, 'practitionerdashboard/appointment.html', context)


def accepted_appointments_view(request):
    """Dedicated view for accepted appointments - accessible from sidebar"""
    practitioner_id = request.session.get('practitioner_id')
    
    if not practitioner_id:
        return redirect('frontend:practitioner_login')
    
    practitioner = get_object_or_404(Practitioner, id=practitioner_id)
    
    # Get all accepted appointments for this practitioner
    accepted_appointments = Appointment.objects.filter(
        practitioner_id=practitioner_id,
        status='Accepted'
    ).select_related('patient', 'slot').order_by('-slot__date', '-slot__start_time')
    
    # Get current time for categorization
    from django.utils import timezone as django_timezone
    now_time = django_timezone.now()
    today = django_timezone.localdate()
    
    # Categorize accepted appointments
    upcoming_accepted = accepted_appointments.filter(slot__date__gte=today)
    past_accepted = accepted_appointments.filter(slot__date__lt=today)
    today_accepted = accepted_appointments.filter(slot__date=today)
    
    context = {
        'practitioner': practitioner,
        'accepted_appointments': accepted_appointments,
        'upcoming_accepted': upcoming_accepted,
        'past_accepted': past_accepted,
        'today_accepted': today_accepted,
        'total_accepted': accepted_appointments.count(),
        'upcoming_count': upcoming_accepted.count(),
        'past_count': past_accepted.count(),
        'today_count': today_accepted.count(),
    }
    
    return render(request, 'practitionerdashboard/accepted_appointments.html', context)


def chat(request):
    return render(request, 'practitionerdashboard/chat.html')



from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from datetime import datetime
from .models import AvailableSlot, Practitioner

def schedule_timming(request):
    practitioner_id = request.session.get('practitioner_id')
    if not practitioner_id:
        return redirect('frontend:practitioner_login')

    practitioner = get_object_or_404(Practitioner, id=practitioner_id)
    slots = practitioner.available_slots.all().order_by('date', 'start_time')
    return render(request, 'practitionerdashboard/schedule_time.html', {'slots': slots})

def add_slot(request):
    if request.method == 'POST':
        try:
            practitioner_id = request.session.get('practitioner_id')
            if not practitioner_id:
                return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)

            practitioner = get_object_or_404(Practitioner, id=practitioner_id)
            
            # Parse JSON data
            data = json.loads(request.body)
            
            # Parse date - ensure it's treated as local date
            slot_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            
            # Parse times
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()
            
            # Validate that end time is after start time
            if end_time <= start_time:
                return JsonResponse({
                    'success': False, 
                    'error': 'End time must be after start time'
                }, status=400)
            
            # Check if slot already exists
            existing_slot = AvailableSlot.objects.filter(
                practitioner=practitioner,
                date=slot_date,
                start_time=start_time,
                end_time=end_time
            ).exists()
            
            if existing_slot:
                return JsonResponse({
                    'success': False, 
                    'error': 'This slot already exists'
                }, status=400)

            # Create the slot
            slot = AvailableSlot.objects.create(
                practitioner=practitioner,
                date=slot_date,
                start_time=start_time,
                end_time=end_time
            )
            
            # Send notifications to interested patients about new availability
            try:
                from .notifications import send_bulk_availability_notifications
                # Get recently added slots for this practitioner
                recent_slots = AvailableSlot.objects.filter(
                    practitioner=practitioner,
                    status='available',
                    date__gte=datetime.now().date()
                ).order_by('date', 'start_time')[:5]  # Get up to 5 recent slots
                
                send_bulk_availability_notifications(practitioner, recent_slots)
                print(f"✅ Availability notifications sent for new slot: {slot_date} {start_time}-{end_time}")
            except Exception as e:
                print(f"⚠️ Failed to send availability notifications: {str(e)}")

            return JsonResponse({
                'success': True,
                'slot': {
                    'id': slot.id,
                    'date': slot.date.strftime('%Y-%m-%d'),
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M')
                }
            })
        
        except KeyError as e:
            return JsonResponse({
                'success': False, 
                'error': f'Missing required field: {str(e)}'
            }, status=400)
        except ValueError as e:
            return JsonResponse({
                'success': False, 
                'error': f'Invalid date/time format: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'An error occurred: {str(e)}'
            }, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    
def remove_slot(request, slot_id):
    if request.method == "POST":
        slot = get_object_or_404(AvailableSlot, id=slot_id)
        slot.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)





def mypatient(request):
    practitioner_id = request.session.get('practitioner_id')

    if practitioner_id:
        appointments = Appointment.objects.filter(
            practitioner_id=practitioner_id, status='Accepted'
        ).select_related('patient')
       
       
        patients = list(set(appointment.patient for appointment in appointments))

        # Fetch prescriptions for each patient
        for patient in patients:
            patient.prescriptions = Prescription.objects.filter(patient=patient)

    else:
        patients = []

    return render(request, 'practitionerdashboard/mypatient.html', {'patients': patients})






def CompleteProfile(request):
    context = {}

    # Retrieve practitioner ID from session
    practitioner_id = request.session.get('practitioner_id')
    
    print("Practitonar ID:",practitioner_id)
    
    if not practitioner_id:
        context['error_message'] = "No practitioner ID found in the session. Please log in."
        return redirect('login')  # Redirect to login if ID is missing

    # Fetch practitioner instance or return a 404 error
    practitioner = get_object_or_404(Practitioner, id=practitioner_id)
    context['practitioner'] = practitioner  # Pass the practitioner object to the template

    if request.method == 'POST':
        # Retrieve form data
        photo = request.FILES.get('photo')
        price = request.POST.get('price')
        description = request.POST.get('description')

        # Validate inputs
        if photo:
            practitioner.photo = photo
        if price:
            try:
                practitioner.price = float(price)
            except ValueError:
                context['error_message'] = "Invalid price. Please enter a valid number."
                return render(request, 'practitionerdashboard/profile.html', context)

        if description:
            practitioner.description = description

        # Save the changes
        practitioner.save()
        context['success_message'] = "Profile updated successfully!"
        return redirect('practitioner_dashboard:practitioner_profile')  # Redirect to prevent form resubmission

    return render(request, 'practitionerdashboard/profile.html', context)









@csrf_exempt
def start_video_call(request, patient_id):
    practitioner_id = request.session.get('practitioner_id')

    if not practitioner_id:
        return JsonResponse({"error": "Practitioner is not logged in. Please log in again."}, status=401)

    if request.method == "POST":
        try:
            # Get practitioner and patient
            practitioner = get_object_or_404(Practitioner, id=practitioner_id)
            patient = get_object_or_404(Patient, id=patient_id)

            # Get the latest accepted appointment
            appointment = Appointment.objects.filter(
                patient=patient, 
                practitioner=practitioner,
                status='Accepted'
            ).order_by('-created_at').first()

            if not appointment:
                return JsonResponse({"error": "No accepted appointment found for this patient."}, status=404)

            # Generate meeting if not exists
            if not appointment.video_call_link:
                meeting_result = generate_zoom_meeting_for_appointment(appointment)
                if not meeting_result['success']:
                    return JsonResponse({"error": f"Failed to create video meeting: {meeting_result['error']}"}, status=500)

            # Send a notification to the patient
            try:
                Notification.objects.create(
                    recipient=patient,
                    message=f"Your doctor has started a video call. Click here to join: {appointment.video_call_link}",
                    url=appointment.video_call_link
                )
            except Exception as e:
                print(f"⚠️ Failed to create notification: {str(e)}")

            # Determine meeting provider
            provider = "Video meeting"
            if "zoom.us" in appointment.video_call_link:
                provider = "Zoom meeting"
            elif "meet.jit.si" in appointment.video_call_link:
                provider = "Jitsi meeting"

            return JsonResponse({
                "success": True, 
                "message": f"{provider} ready!", 
                "join_url": appointment.video_call_link,
                "start_url": appointment.host_start_url or appointment.video_call_link,
                "meeting_id": appointment.meeting_id,
                "password": appointment.meeting_password or "",
                "provider": provider
            }, status=200)

        except Exception as e:
            print(f"❌ Error in start_video_call: {str(e)}")
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)






    

def add_prescription(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    # Get the practitioner ID from the session
    practitioner_id = request.session.get("practitioner_id")

    if not practitioner_id:
        messages.error(request, "Unauthorized access! Practitioner ID is missing.")
        return redirect("practitioner_dashboard:mypatient")  

    # Get the practitioner instance
    practitioner = get_object_or_404(Practitioner, id=practitioner_id)

    
    # Check if a prescription already exists for this patient and practitioner
    prescription = Prescription.objects.filter(practitioner=practitioner, patient=patient).first()

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        prescription_file = request.FILES.get("prescription_file")
        if not text and not prescription_file:
            messages.error(request, "Please enter a prescription or upload a file.")
            return redirect("practitioner_dashboard:practitioner_profile")  
        # If prescription exists, update it
        if prescription:
            prescription.text = text or prescription.text
            if prescription_file:
                prescription.prescription_file = prescription_file
            prescription.save()
            messages.success(request, "Prescription updated successfully!")
        else:
            # Create a new prescription
            Prescription.objects.create(
                practitioner=practitioner,
                patient=patient,
                text=text,
                prescription_file=prescription_file
            )
            messages.success(request, "Prescription added successfully!")

        return redirect("practitioner_dashboard:mypatient")  

    messages.info(request, "Invalid request method.")
    return redirect("practitioner_dashboard:mypatient")





def Cancel_Complete(request):
    practitioner_id = request.session.get("practitioner_id")  # Get practitioner_id from session
    
    if not practitioner_id:
        return render(request, "practitionerdashboard/Cancel_Completeion.html", {
            "message": "Practitioner ID not found in session."
        })

    # Filter appointments for the logged-in practitioner where status is "Cancelled"
    cancelled_appointments = Appointment.objects.filter(practitioner_id=practitioner_id, status="Cancelled")

    return render(request, 'practitionerdashboard/Cancel_Completeion.html', {
        "cancelled_appointments": cancelled_appointments
    })







def get_pending_appointments_api(request):
    """API endpoint to get pending appointments for alert bell"""
    practitioner_id = request.session.get('practitioner_id')
    
    if not practitioner_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    
    try:
        # Get pending appointments for this practitioner
        pending_appointments = Appointment.objects.filter(
            practitioner_id=practitioner_id,
            status='Pending'
        ).select_related('patient', 'slot').order_by('slot__start_time')[:10]  # Limit to 10 most recent
        
        appointments_data = []
        for appointment in pending_appointments:
            # Determine urgency display
            urgency_display = {
                'emergency': {'text': 'Emergency', 'class': 'bg-red-100 text-red-800', 'icon': 'fas fa-exclamation-circle'},
                'urgent': {'text': 'Urgent', 'class': 'bg-yellow-100 text-yellow-800', 'icon': 'fas fa-exclamation-triangle'},
                'normal': {'text': 'Normal', 'class': 'bg-green-100 text-green-800', 'icon': 'fas fa-clock'}
            }.get(appointment.urgency, {'text': 'Normal', 'class': 'bg-green-100 text-green-800', 'icon': 'fas fa-clock'})
            
            appointments_data.append({
                'id': appointment.id,
                'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
                'patient_email': appointment.patient.email,
                'patient_initial': appointment.patient.first_name[0].upper() if appointment.patient.first_name else 'P',
                'date': appointment.slot.date.strftime('%b %d, %Y'),
                'time': appointment.slot.start_time.strftime('%I:%M %p'),
                'amount': str(appointment.amount),
                'reason': appointment.reason or 'No reason provided',
                'urgency': appointment.urgency,
                'urgency_display': urgency_display,
                'created_at': appointment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'success': True,
            'appointments': appointments_data,
            'count': len(appointments_data)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def update_appointment_status_api(request, appointment_id, status):
    """API endpoint to update appointment status (Accept/Cancel)"""
    practitioner_id = request.session.get('practitioner_id')
    
    if not practitioner_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    
    if status not in ['Accepted', 'Cancelled']:
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id, practitioner_id=practitioner_id)
        appointment.status = status
        appointment.save()
        
        # Send notifications
        if status == 'Accepted':
            # Generate Zoom meeting if not exists
            if not appointment.video_call_link:
                zoom_result = generate_zoom_meeting_for_appointment(appointment)
                if not zoom_result['success']:
                    return JsonResponse({
                        'success': False, 
                        'error': f"Appointment accepted but failed to create Zoom meeting: {zoom_result['error']}"
                    }, status=500)
            
            # Create chat room when appointment is accepted
            from chat.models import ChatRoom
            chat_room, created = ChatRoom.objects.get_or_create(
                patient=appointment.patient,
                practitioner=appointment.practitioner
            )
            
            from .notifications import notify_appointment_accepted
            notify_appointment_accepted(appointment)
            message = 'Appointment accepted successfully! Zoom meeting and chat enabled.'
        else:
            from .notifications import notify_appointment_cancelled
            notify_appointment_cancelled(appointment, 'Cancelled by practitioner')
            message = 'Appointment cancelled successfully!'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'appointment_id': appointment_id,
            'new_status': status
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def practitioner_reviews(request):
    # Get practitioner_id from session
    practitioner_id = request.session.get('practitioner_id')

    if not practitioner_id:
        return JsonResponse({"error": "Practitioner not found in session"}, status=400)

    # Fetch reviews related to the current practitioner
    reviews = Review.objects.filter(practitioner=practitioner_id)

    # Handle reply functionality
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        message = request.POST.get('message')

        print("Received POST data:", request.POST)  # Debugging

        if not review_id or not message:
            return JsonResponse({"error": "Missing review_id or message"}, status=400)

        try:
            # Get the review by its ID
            review = Review.objects.get(id=review_id)
            

            # If Reply model uses GenericForeignKey, you need ContentType
            content_type = ContentType.objects.get_for_model(Review)

            # Create a new reply object and save it
            reply = Reply.objects.create(
                review=review,
                content_type=content_type,
                object_id=practitioner_id,  # Assuming practitioner is the object for reply
                message=message
            )

            # Return success response
            return JsonResponse({"message": "Reply saved successfully"}, status=200)

        except Review.DoesNotExist:
            return JsonResponse({"error": "Review not found"}, status=404)

        except Exception as e:
            # Log the error if necessary
            print("Error:", e)
            return JsonResponse({"error": str(e)}, status=500)

    # Return rendered template with reviews
    return render(request, 'practitionerdashboard/reviews.html', {'reviews': reviews})


def update_existing_appointments_to_zoom():
    """Update existing appointments from Jitsi to Zoom meetings"""
    try:
        # Get all accepted appointments that have Jitsi links
        appointments_to_update = Appointment.objects.filter(
            status='Accepted',
            video_call_link__icontains='meet.jit.si'
        )
        
        updated_count = 0
        failed_count = 0
        
        for appointment in appointments_to_update:
            # Generate Zoom meeting for this appointment
            zoom_result = generate_zoom_meeting_for_appointment(appointment)
            
            if zoom_result['success']:
                updated_count += 1
                print(f"✅ Updated appointment {appointment.id} - {appointment.patient.first_name} {appointment.patient.last_name}")
            else:
                failed_count += 1
                print(f"❌ Failed to update appointment {appointment.id}: {zoom_result['error']}")
        
        return {
            'success': True,
            'updated': updated_count,
            'failed': failed_count,
            'total': appointments_to_update.count()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_chat_room_api(request):
    """API endpoint to get or create chat room for practitioner-patient pair"""
    practitioner_id = request.session.get('practitioner_id')
    
    if not practitioner_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient_id = data.get('patient_id')
            
            if not patient_id:
                return JsonResponse({'success': False, 'error': 'Patient ID required'}, status=400)
            
            # Check if there's an accepted appointment between them
            from patientdashboard.models import Appointment
            accepted_appointment = Appointment.objects.filter(
                patient_id=patient_id,
                practitioner_id=practitioner_id,
                status='Accepted'
            ).exists()
            
            if not accepted_appointment:
                return JsonResponse({
                    'success': False, 
                    'error': 'No accepted appointment found. Chat is only available for accepted appointments.'
                }, status=403)
            
            # Get or create chat room
            from chat.models import ChatRoom
            from user_account.models import Patient, Practitioner
            
            patient = get_object_or_404(Patient, id=patient_id)
            practitioner = get_object_or_404(Practitioner, id=practitioner_id)
            
            chat_room, created = ChatRoom.objects.get_or_create(
                patient=patient,
                practitioner=practitioner
            )
            
            return JsonResponse({
                'success': True,
                'chat_room_id': chat_room.id,
                'created': created,
                'patient_name': f"{patient.first_name} {patient.last_name}",
                'practitioner_name': f"Dr. {practitioner.first_name} {practitioner.last_name}"
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def migrate_jitsi_to_zoom_view(request):
    """Admin view to migrate existing Jitsi appointments to Zoom"""
    practitioner_id = request.session.get('practitioner_id')
    
    if not practitioner_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    
    if request.method == 'POST':
        # Run the migration
        result = update_existing_appointments_to_zoom()
        return JsonResponse(result)
    
    # Get count of appointments that need migration
    jitsi_appointments = Appointment.objects.filter(
        practitioner_id=practitioner_id,
        status='Accepted',
        video_call_link__icontains='meet.jit.si'
    ).count()
    
    return JsonResponse({
        'success': True,
        'jitsi_appointments_count': jitsi_appointments
    })










# Notification Views
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from practitionerdashboard.models import PractitionerNotification
from practitionerdashboard.notifications import (
    notify_appointment_accepted, 
    notify_appointment_cancelled, 
    notify_appointment_modified,
    send_bulk_availability_notifications
)
import json

@require_http_methods(["GET"])
def get_practitioner_notifications(request):
    """Get notifications for the current practitioner"""
    try:
        practitioner_id = request.session.get('practitioner_id')
        if not practitioner_id:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        practitioner = get_object_or_404(Practitioner, id=practitioner_id)
        
        # Get recent notifications
        notifications = PractitionerNotification.objects.filter(
            recipient=practitioner
        ).order_by('-created_at')[:20]
        
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'url': notification.url,
                'is_read': notification.is_read,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'time_ago': get_time_ago(notification.created_at)
            })
        
        # Count unread notifications
        unread_count = PractitionerNotification.objects.filter(
            recipient=practitioner,
            is_read=False
        ).count()
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
@csrf_exempt
def mark_practitioner_notification_read(request):
    """Mark a practitioner notification as read"""
    try:
        practitioner_id = request.session.get('practitioner_id')
        if not practitioner_id:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        notification = get_object_or_404(
            PractitionerNotification, 
            id=notification_id, 
            recipient_id=practitioner_id
        )
        
        notification.is_read = True
        notification.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
@csrf_exempt
def mark_all_practitioner_notifications_read(request):
    """Mark all practitioner notifications as read"""
    try:
        practitioner_id = request.session.get('practitioner_id')
        if not practitioner_id:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        PractitionerNotification.objects.filter(
            recipient_id=practitioner_id,
            is_read=False
        ).update(is_read=True)
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
@csrf_exempt
def handle_appointment_action(request, appointment_id, action):
    """Handle appointment accept/decline actions with notifications"""
    try:
        practitioner_id = request.session.get('practitioner_id')
        if not practitioner_id:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        appointment = get_object_or_404(
            Appointment, 
            id=appointment_id, 
            practitioner_id=practitioner_id
        )
        
        if action == 'accept':
            appointment.status = 'Accepted'
            appointment.save()
            
            # Create Zoom meeting if configured
            if ZOOM_CONFIGURED:
                zoom_result = create_zoom_meeting(
                    topic=f"Medical Consultation - {appointment.patient.first_name} {appointment.patient.last_name}",
                    start_time=appointment.slot.start_time,
                    duration=60
                )
                
                if zoom_result.get('success'):
                    appointment.video_call_link = zoom_result['join_url']
                    appointment.meeting_id = zoom_result['meeting_id']
                    appointment.meeting_password = zoom_result.get('password', '')
                    appointment.save()
            
            # Send notifications
            notify_appointment_accepted(appointment)
            
            return JsonResponse({
                'success': True, 
                'message': 'Appointment accepted successfully',
                'status': 'Accepted'
            })
            
        elif action == 'decline':
            appointment.status = 'Cancelled'
            appointment.save()
            
            # Send notifications
            notify_appointment_cancelled(appointment, reason="Declined by practitioner", cancelled_by="practitioner")
            
            return JsonResponse({
                'success': True, 
                'message': 'Appointment declined successfully',
                'status': 'Cancelled'
            })
        
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
@csrf_exempt
def notify_availability_added(request):
    """Notify patients when practitioner adds new availability"""
    try:
        practitioner_id = request.session.get('practitioner_id')
        if not practitioner_id:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        practitioner = get_object_or_404(Practitioner, id=practitioner_id)
        
        # Get recently added slots (you can customize this logic)
        from datetime import datetime, timedelta
        recent_slots = AvailableSlot.objects.filter(
            practitioner=practitioner,
            status='available',
            date__gte=datetime.now().date()
        ).order_by('date', 'start_time')[:10]  # Get up to 10 recent slots
        
        if recent_slots.exists():
            # Send bulk notifications
            send_bulk_availability_notifications(practitioner, recent_slots)
            
            return JsonResponse({
                'success': True,
                'message': f'Notifications sent to interested patients about {recent_slots.count()} new slots'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No available slots found to notify about'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def get_time_ago(created_at):
    """Helper function to get human-readable time difference"""
    from django.utils import timezone
    
    now = timezone.now()
    diff = now - created_at
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

# Enhanced appointment management with notifications
@require_http_methods(["POST"])
@csrf_exempt
def reschedule_appointment(request, appointment_id):
    """Reschedule an appointment with notifications"""
    try:
        practitioner_id = request.session.get('practitioner_id')
        if not practitioner_id:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        appointment = get_object_or_404(
            Appointment, 
            id=appointment_id, 
            practitioner_id=practitioner_id
        )
        
        data = json.loads(request.body)
        new_slot_id = data.get('new_slot_id')
        reason = data.get('reason', '')
        
        # Get the new slot
        new_slot = get_object_or_404(AvailableSlot, id=new_slot_id, practitioner_id=practitioner_id)
        
        # Store old time for notification
        old_time = appointment.slot.start_time
        
        # Update appointment
        old_slot = appointment.slot
        old_slot.status = 'available'  # Make old slot available again
        old_slot.save()
        
        appointment.slot = new_slot
        appointment.save()
        
        new_slot.status = 'booked'
        new_slot.save()
        
        # Send modification notification
        notify_appointment_modified(appointment, old_time=old_time, reason=reason)
        
        return JsonResponse({
            'success': True,
            'message': 'Appointment rescheduled successfully',
            'new_time': new_slot.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})