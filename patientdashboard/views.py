
import datetime
import json
from django.db.models import Q
from patientdashboard.models import Appointment, Notification
from user_account.models import Practitioner ,Patient # Assuming Practitioner is the model for doctors/practitioners
from django.shortcuts import render, get_object_or_404, redirect
from user_account.models import Patient  # Adjust the import based on your app structure
from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment, Patient, Notification
from django.http import JsonResponse
from user_account.models import Patient
from practitionerdashboard.models import AvailableSlot
from django.shortcuts import render, get_object_or_404
from user_account.models import Practitioner
from practitionerdashboard.models import AvailableSlot
from django.utils.timezone import now
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PatientProfileForm, PatientPasswordForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render
import sys

from django.core.paginator import Paginator
def patient_dashboard(request):
    print("📌 patient_dashboard view is being executed!")  # Debugging print
    sys.stdout.flush()  # Force output to be written


    patient_id = request.session.get('patient_id')
    print(f"Session Data: {request.session.items()}")  # Print session details
    sys.stdout.flush()  # Force output to be written


    if not patient_id:
        print("❌ No patient_id found in session. Redirecting to login.")
        return redirect('/patient/login/')

    notifications = Notification.objects.filter(recipient_id=patient_id, is_read=False).order_by('-created_at')

    print(f"🔔 Notifications found: {notifications.count()}")  # Print notifications count

    return render(request, "patientdashboard/dashboard.html", {"notifications": notifications})

    

# patientdashboard/views.py


def get_practitioners_by_specialization(request):
    specialization = request.GET.get('specialization')
    if not specialization:
        return JsonResponse({'error': 'Specialization is required'}, status=400)

    practitioners = Practitioner.objects.filter(specialty=specialization)
    data = [
        {
            'id': p.id,
            'first_name': p.first_name,
            'last_name': p.last_name,
            'email': p.email,
            'photo': p.photo.url if p.photo else None,
            'specialty': p.get_specialty_display(),
        }
        for p in practitioners
    ]
    return JsonResponse(data, safe=False)

def available_slots(request, practitioner_id):
    practitioner = get_object_or_404(Practitioner, id=practitioner_id)
    slots = AvailableSlot.objects.filter(practitioner=practitioner, status='available').order_by('day_of_week', 'start_time')
    return render(request, 'patientdashboard/available_slots.html', {'practitioner': practitioner, 'slots': slots})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from patientdashboard.models import Appointment
from user_account.models import Patient
from practitionerdashboard.models import AvailableSlot
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from patientdashboard.models import Appointment
from user_account.models import Patient
from practitionerdashboard.models import AvailableSlot
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .models import Patient, AvailableSlot, Appointment
from django.shortcuts import render, redirect
from .models import Patient, Appointment, AvailableSlot
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
from datetime import datetime, timedelta

from .models import Patient, Practitioner, Appointment, AvailableSlot
from .stripe_utils import create_checkout_session, handle_checkout_completed

# Your existing views...
import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from datetime import datetime, date, timedelta
from django.utils import timezone
from .models import Appointment, AvailableSlot, Patient
from .stripe_utils import create_checkout_session, handle_checkout_completed

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY



def book_appointment(request):
    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        patient_id = request.session.get('patient_id')  # Ensure the patient is logged in

        if not patient_id:
            return redirect('frontend:patient_login')  # Redirect to login if not logged in

        if not slot_id:
            return render(request, 'patientdashboard/booking_failed.html', 
                          {'error': 'Invalid slot selection.'})  # Show error page

        # Ensure patient exists
    
        
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return redirect('frontend:patient_login')  # Redirect if patient doesn't exist

        # Check if patient has an unpaid appointment
        unpaid_appointment = Appointment.objects.filter(
            patient=patient, payment_status="Pending"
        ).exists()

        if unpaid_appointment:
            return render(request, 'patientdashboard/booking_failed.html', 
                          {'error': 'You already have an unpaid appointment. Please complete the payment before booking another one.'})

        # Ensure slot exists and get related practitioner
        try:
            slot = AvailableSlot.objects.get(id=slot_id, status='available')
        except AvailableSlot.DoesNotExist:
            return render(request, 'patientdashboard/booking_failed.html', 
                          {'error': 'Selected slot is unavailable or does not exist.'})

        # Ensure practitioner exists
        practitioner = slot.practitioner if hasattr(slot, 'practitioner') else None
        if not practitioner:
            return render(request, 'patientdashboard/booking_failed.html', 
                          {'error': 'No practitioner linked to this slot.'})

        # Prevent duplicate bookings for the same slot
        if Appointment.objects.filter(patient=patient, slot=slot).exists():
            return render(request, 'patientdashboard/booking_failed.html', 
                          {'error': 'You have already booked this appointment.'})

        # Create the appointment
        try:
            appointment = Appointment.objects.create(
                patient=patient,
                slot=slot,
                practitioner=practitioner,
                payment_status="Pending"  # New appointments are unpaid by default
            )
            slot.status = 'booked'
            slot.save()
        except Exception as e:
            return render(request, 'patientdashboard/booking_failed.html', 
                          {'error': f'Database error: {str(e)}'})

        # Redirect to payment page with the appointment id
        return redirect('patientdashboard:payment', appointment_id=appointment.id)

    return render(request, 'patientdashboard/booking_failed.html', 
                  {'error': 'Invalid request method.'})





def payment_view(request, appointment_id):
    """View to show payment details and initiate Stripe checkout"""
    patient_id = request.session.get('patient_id')
    
    if not patient_id:
        return redirect('frontend:patient_login')
    
    # Get the appointment
    try:
        appointment = Appointment.objects.get(id=appointment_id, patient__id=patient_id)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found or doesn't belong to you.")
        return redirect('patientdashboard:dashboard')
    
    # If payment already completed
    if appointment.payment_status == 'Completed':
        messages.info(request, "This appointment has already been paid for.")
        return redirect('patientdashboard:dashboard')
    
    # Calculate appointment duration in minutes
    start_datetime = datetime.combine(date.today(), appointment.slot.start_time)
    end_datetime = datetime.combine(date.today(), appointment.slot.end_time)
    duration = int((end_datetime - start_datetime).total_seconds() / 60)
    
    # Create Stripe checkout session
    try:
        checkout_session_id = create_checkout_session(request, appointment)
        print(f"Created checkout session: {checkout_session_id}")  # Debug log
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")  # Debug log
        messages.error(request, f"Error creating payment: {str(e)}")
        return redirect('patientdashboard:dashboard')
    
    context = {
        'appointment': appointment,
        'duration': duration,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'checkout_session_id': checkout_session_id,
    }
    
    print(f"Context for payment template: {context}")  # Debug log
    
    return render(request, 'patientdashboard/payment2.html', context)


def payment_success(request):
    """View for successful payment"""
    patient_id = request.session.get('patient_id')
    
    if not patient_id:
        return redirect('frontend:patient_login')
    
    appointment_id = request.GET.get('appointment_id')
    
    try:
        appointment = Appointment.objects.get(id=appointment_id, patient__id=patient_id)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found or doesn't belong to you.")
        return redirect('patientdashboard:dashboard')
    
    # Update appointment payment status if not already completed
    # Note: The webhook should already have handled this, but this is a fallback
    if appointment.payment_status != 'Completed':
        appointment.payment_status = 'Completed'
        appointment.save()
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'patientdashboard/payment_success.html', context)


def payment_cancel(request):
    """View for cancelled payment"""
    patient_id = request.session.get('patient_id')
    
    if not patient_id:
        return redirect('frontend:patient_login')
    
    appointment_id = request.GET.get('appointment_id')
    
    try:
        appointment = Appointment.objects.get(id=appointment_id, patient__id=patient_id)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found or doesn't belong to you.")
        return redirect('patientdashboard:dashboard')
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'patientdashboard/payment_cancel.html', context)


@csrf_exempt
def stripe_webhook(request):
    """Webhook to receive Stripe events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        if handle_checkout_completed(event):
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
    
    # Handle other events here if needed
    
    return HttpResponse(status=200)


def booking(request):
    from user_account.models import Practitioner
    context = {
        'SPECIALTY_CHOICES': Practitioner.SPECIALTY_CHOICES,
    }
    return render(request, 'patientdashboard/booking.html', context)
def search_practitioners(request):
    query = request.GET.get('query', '')  # Search query
    gender = request.GET.get('gender', '')  # Gender filter
    location = request.GET.get('location', '')  # Location filter
    specialty = request.GET.get('specialty', '')  # Specialty filter

    # Fetch all practitioners initially
    practitioners = Practitioner.objects.all()

    # Apply search query filter (search in first_name, last_name, or specialty)
    if query:
        practitioners = practitioners.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(specialty__icontains=query)
        )

    # Apply gender filter (case-sensitive check)
    if gender:
        practitioners = practitioners.filter(gender__iexact=gender)

    # Apply location filter (case-insensitive substring match)
    if location:
        practitioners = practitioners.filter(location__icontains=location)

    # Apply specialty filter (match exact choice value)
    if specialty:
        practitioners = practitioners.filter(specialty=specialty)

    # Paginate results (10 results per page)
    paginator = Paginator(practitioners, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'patientdashboard/search.html', {
        'query': query,
        'page_obj': page_obj,
        'gender': gender,
        'location': location,
        'specialty': specialty,
    })

def chat(request):
    return render(request, 'patientdashboard/chat.html')



from practitionerdashboard.models import Prescription
def appointments_patients(request):
    patient_id = request.session.get('patient_id')

    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id)

        notifications = Notification.objects.filter(recipient=patient, is_read=False).order_by('-created_at')

        appointments = Appointment.objects.filter(patient=patient).select_related('practitioner', 'slot')

        prescriptions = Prescription.objects.filter(patient=patient)


        return render(request, 'patientdashboard/appointments_patients.html', {
            'patient': patient,
            'notifications': notifications,
            'appointments': appointments,
            'prescriptions': prescriptions,
        })
    else:
        return redirect('frontend:patient_login')

    
   


from django.shortcuts import render, redirect

def payment(request):
    if request.method == 'POST':
        # Here you can add logic to update the payment status
        # For example, updating the user's payment status or invoice status.
        # user.payment_status = 'Paid'
        # user.save()

        # Redirect to booking success page after payment is marked as successful
        return redirect('patientdashboard:booking_success')
    return render(request, 'patientdashboard/pay.html')


def telemedicine(request):
    return render(request, 'patientdashboard/telemedicine.html')
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Practitioner, Review
from .forms import ReviewForm
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Practitioner, Review, Patient
def practitioner_profile(request, pk):
    practitioner = get_object_or_404(Practitioner, pk=pk)
    reviews = Review.objects.filter(practitioner=practitioner).order_by('-created_at')
    
    # Calculate average rating if reviews exist
    average_rating = 0
    if reviews.exists():
        total = sum(review.rating for review in reviews)
        average_rating = total / reviews.count()
    
    # Handle review submission
    if request.method == 'POST':
        # Get the logged-in patient using session data
        patient_id = request.session.get('patient_id')
        
        if patient_id:
            try:
                patient = Patient.objects.get(id=patient_id)
                
                rating = request.POST.get('rating')
                feedback = request.POST.get('feedback')
                
                if rating:
                    # Check if patient has already reviewed this practitioner
                    existing_review = Review.objects.filter(patient=patient, practitioner=practitioner).first()
                    
                    if existing_review:
                        # Update existing review
                        existing_review.rating = int(rating)
                        existing_review.feedback = feedback
                        existing_review.save()
                        messages.success(request, "Your review has been updated.")
                    else:
                        # Create a new review
                        review = Review(
                            patient=patient,
                            practitioner=practitioner,
                            rating=int(rating),
                            feedback=feedback
                        )
                        review.save()
                        messages.success(request, "Your review has been submitted.")
                    
                    return redirect('patientdashboard:practitioner_profile', pk=pk)
                else:
                    messages.error(request, "Rating is required.")
            except Patient.DoesNotExist:
                messages.error(request, "Unable to find your patient profile.")
        else:
            messages.warning(request, "You need to be logged in to leave a review.")
            # Optional: Store the intended action in session for redirect after login
            request.session['redirect_after_login'] = request.path
            return redirect('/patient/login/')
    
    # Check if patient is logged in using the session data
    is_patient_logged_in = 'patient_id' in request.session
    
    context = {
        'practitioner': practitioner,
        'reviews': reviews,
        'average_rating': average_rating,
        'total_reviews': reviews.count(),
        'is_patient_logged_in': is_patient_logged_in
    }
    
    return render(request, 'patientdashboard/doctor_profile.html', context)
def booking_success(request):
    # Fetch the appointment details
    return render(request, 'patientdashboard/booking_success.html')

def view_invoice(request):
    return render(request, 'patientdashboard/view_invoice.html')




def patient_profile(request):
    # Get patient_id from session
    patient_id = request.session.get('patient_id')
    if not patient_id:
        messages.error(request, 'Please log in first')
        return redirect('login')

    # Get the patient or return 404
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST' and 'update_profile' in request.POST:
        form = PatientProfileForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('patientdashboard:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientProfileForm(instance=patient)

    context = {
        'patient': patient,
        'form': form,
    }
    
    return render(request, 'patientdashboard/profile.html', context)





def exercises_view(request):
    context = {
        'exercises': [
            {'name': 'Basic Yoga', 'url': 'patientdashboard:yoga_tutorial', 'image': 'basic_yoga.jpg'},
            {'name': 'Leg Exercises', 'url': 'patientdashboard:leg_exercises_tutorial', 'image': 'legs.jpg'},
            {'name': 'Arm Exercises', 'url': 'patientdashboard:arm_exercises_tutorial', 'image': 'arms.jpg'},
        ]
    }
    return render(request, 'patientdashboard/exercises.html', context)
def yoga_tutorial(request):
    context = {
        'exercise_name': 'Basic Yoga',
        'steps': [
           {
    'step': 1,
    'instruction': 'Raised Hands Pose: Stand tall with feet together. Inhale and raise your arms overhead, keeping them parallel and palms facing each other.',
    'video': 'https://www.verywellfit.com/thmb/kIygQFVp3hjSBFyphdmgyrlvD98=/750x0/filters:gifv(webm)/raisedarm-pose-2f444fca6bae4742bde9c0dfa6a9a45a.gif'  # Add a YouTube embed link
},
            {
                'step': 2,
                'instruction': 'Downward-Facing Dog: Start on your hands and knees. Lift your hips up and back, forming an inverted V shape.',
                'video': 'https://www.verywellfit.com/thmb/ivbgBdIazIWeUMnvjkgzWcj5k6Q=/750x0/filters:gifv(webm)/Verywell-18-3567197-DownDogSplit01-887-5afc773e3037130037a6a82d.gif'  # No video for this step
            },
            {
                'step': 3,
                'instruction': 'Warrior II: Step one foot back, bend your front knee, and raise your arms overhead. Keep your back leg straight.',
                'video': 'https://www.verywellfit.com/thmb/gjxJxNveYVmRoORSPkM3u8pErR0=/750x0/filters:gifv(webm)/Verywell-03-3567198-Warrior2copy-598b7c57396e5a0010148cc5.gif'  # YouTube embed link
            },
            {
                'step': 4,
                'instruction': 'Bridge Pose: Lie on your back with knees bent and feet flat on the floor. Lift your hips towards the ceiling while keeping your shoulders grounded.',
                'video': 'https://www.verywellfit.com/thmb/-2ytXkijWJ48nkhKjl7w0rsAYSs=/750x0/filters:gifv(webm)/essential-yoga-poses-for-beginners-3566747-bridge-f91496dbe9a34e168ea9858b543ae46f.gif'  # Add a video link if available
            },
        {
                'step': 5,
                'instruction': 'Easy Pose: Sit on the floor with your legs crossed and your hands resting on your knees. Keep your back straight and breathe deeply.',
                'image': 'easy_pose.jpg',  # Add the image for Easy Pose
                'video': None  # Add a video link if available
            }
        ]
    }
    return render(request, 'patientdashboard/exercise_tutorial.html', context)
def leg_exercises_tutorial(request):
    context = {
        'exercise_name': 'Leg Exercises',
        'steps': [
            {'step': 1, 'instruction': 'Stand straight and place your hands on your hips.', 'image': 'leg_step1.jpg'},
            {'step': 2, 'instruction': 'Lunge forward with your right leg.', 'image': 'leg_step2.jpg'},
            {'step': 3, 'instruction': 'Return to the starting position and repeat with the left leg.', 'image': 'leg_step3.jpg'},
        ]
    }
    return render(request, 'patientdashboard/exercise_tutorial.html', context)

def arm_exercises_tutorial(request):
    context = {
        'exercise_name': 'Arm Exercises',
        'steps': [
            {'step': 1, 'instruction': 'Stand straight with your arms at your sides.', 'image': 'arm_step1.jpg'},
            {'step': 2, 'instruction': 'Raise your arms to shoulder height and hold for 5 seconds.', 'image': 'arm_step2.jpg'},
            {'step': 3, 'instruction': 'Lower your arms slowly and repeat.', 'image': 'arm_step3.jpg'},
        ]
    }
    return render(request, 'patientdashboard/exercise_tutorial.html', context)
def update_progress(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Here you can save the progress to the database
        # For now, we'll just return a success message
        return JsonResponse({'status': 'success', 'message': 'Progress updated successfully.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
