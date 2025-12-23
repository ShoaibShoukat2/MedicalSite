import uuid
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

    # Today's appointments (appointments for today with any status)
    today_appointments = Appointment.objects.filter(
        slot__start_time__range=(today_start, today_end),
        practitioner_id=practitioner_id,
    ).order_by('slot__start_time')
    
    # Accepted appointments (status = Accepted)
    accepted_appointments = Appointment.objects.filter(
        practitioner_id=practitioner_id,
        status='Accepted',
        amount=practitioner.price
    ).order_by('slot__start_time')
    
    # Waiting list (appointments >= 24 hours away with status = Pending)
    waiting_list_appointments = Appointment.objects.filter(
        slot__start_time__gte=twenty_four_hours_later,
        status='Pending',
        practitioner_id=practitioner_id,
    ).order_by('slot__start_time')
    
    # Pending appointments (< 24 hours away with status = Pending)
    pending_appointments_list = Appointment.objects.filter(
        slot__start_time__lt=twenty_four_hours_later,
        status='Pending',
        practitioner_id=practitioner_id,
    ).order_by('slot__start_time')

    return render(request, 'practitionerdashboard/dashboard.html', {
        'practitioner': practitioner,
        'today_appointments': today_appointments,
        'waiting_list_appointments': waiting_list_appointments,
        'accepted_appointments': accepted_appointments,
        'pending_appointments_list': pending_appointments_list,
        'total_patients': total_patients,
        'completed_appointments': completed_appointments,
        'pending_appointments': pending_appointments,
    })






from django.core.mail import send_mail
from django.contrib import messages





def accept_appointment(request, appointment_id):
    """Accept appointment with enhanced notifications"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = "Accepted"
    appointment.save()

    # Import notification functions
    from .notifications import notify_appointment_accepted
    
    # Send comprehensive notifications
    notify_appointment_accepted(appointment)

    # Add frontend notification
    messages.success(request, "Appointment accepted successfully! Patient has been notified via email and SMS.")

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
        slot__start_time__date__range=(today, next_week),
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

            # Get the latest appointment (or the first if multiple exist)
            appointment = Appointment.objects.filter(patient=patient, practitioner=practitioner).order_by('-created_at').first()


            if not appointment:
                return JsonResponse({"error": "No appointment found for this patient."}, status=404)

            # Generate a unique Jitsi Meet link
            meeting_id = f"{uuid.uuid4()}-{patient.id}-{practitioner.id}"
            jitsi_link = f"https://meet.jit.si/{meeting_id}"
            


            # Save the video call link in the most recent appointment
            appointment.video_call_link = jitsi_link


            appointment.save()

            # Send a notification to the patient
            Notification.objects.create(
                recipient=patient,
                message=f"Your doctor has started a video call. Click here to join: {jitsi_link}",
                url=jitsi_link
            )

            return JsonResponse({"success": True, "message": "Video call started!", "jitsi_link": jitsi_link}, status=200)

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)






    

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









