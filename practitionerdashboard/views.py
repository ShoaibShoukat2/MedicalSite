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

    today = date.today()
    now_time = datetime.now()
    today_start = datetime.combine(today, datetime.min.time())  # Start of today
    today_end = datetime.combine(today, datetime.max.time())  # End of today
    
    # 24 hours from now timestamp
    twenty_four_hours_later = now_time + timedelta(hours=24)

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
    
    
    
    # Today's appointments
    today_appointments = Appointment.objects.filter(
        slot__start_time__range=(today_start, today_end),
        status='Pending',
        practitioner_id=practitioner_id,
        
    ).order_by('slot__start_time')

    return render(request, 'practitionerdashboard/dashboard.html', {
        'today_appointments': today_appointments,
        'waiting_list_appointments': waiting_list_appointments,
        'accepted_appointments': accepted_appointments,
        'pending_appointments_list': pending_appointments_list,
        'total_patients': total_patients,
        'completed_appointments': completed_appointments,
        'pending_appointments': pending_appointments,
    })













    
def accept_appointment(request, appointment_id):
    # Get the appointment object
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    

    # Check if the form is submitted (POST request)
        
        
    # Update the appointment status to "Accepted"
    appointment.status = "Accepted"
    
    appointment.save()  

    # Redirect to the appointments list after the action
    return redirect('practitioner_dashboard:dashboard')  # Adjust with your URL name










def cancel_appointment(request, appointment_id):
    # Get the appointment object
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Delete the appointment (Cancel action)
    appointment.delete()

    # Redirect to the appointments list after the action
    return redirect('practitioner_dashboard:dashboard')  # Adjust with your URL name

    
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
    return render(request, 'practitionerdashboard/telemedicine.html')

def appointment(request):
    return render(request, 'practitionerdashboard/appointment.html')





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
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()

            # Create the slot
            slot = AvailableSlot.objects.create(
                practitioner=practitioner,
                date=date,
                start_time=start_time,
                end_time=end_time
            )

            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

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







