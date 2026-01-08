
import datetime
import json
from django.db.models import Q
from patientdashboard.models import Appointment, Notification
from user_account.models import Practitioner ,Patient # Assuming Practitioner is the model for doctors/practitioners
from user_account.models import Patient  # Adjust the import based on your app structure
from user_account.models import Patient
from django.utils.timezone import now
from .forms import PatientProfileForm, PatientPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password, check_password
import sys
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from patientdashboard.models import Appointment,Symptom
from user_account.models import Patient
from practitionerdashboard.models import AvailableSlot
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render, redirect
from patientdashboard.models import Appointment
from user_account.models import Patient
from practitionerdashboard.models import AvailableSlot
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .models import Patient, AvailableSlot, Appointment
from django.shortcuts import render, redirect
from .models import Patient, Appointment, AvailableSlot, Practitioner,Practitioner, Review, Patient
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .stripe_utils import create_checkout_session, handle_checkout_completed
import stripe
from django.http import HttpResponse
from datetime import datetime, timedelta, date
from django.http import HttpResponse
from django.template.loader import get_template

# practitionerdashboard/views.py
from django.utils import timezone
from calendar import monthrange
from calendar import month_name
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
# views.py

from .models import VideoConsultationSlot
from .models import  VideoConsultationSlot, Appointment

from django.contrib import messages
from django.utils import timezone
import sys
from .models import AvailableSlot, Appointment, Patient
from django.contrib import messages
import uuid
import sys
from .models import AvailableSlot, Appointment, Patient, Billing
import sys
from practitionerdashboard.models import Prescription
from patientdashboard.models import Billing
import sys
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Billing, Patient

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Practitioner, VideoConsultationSlot
stripe.api_key = settings.STRIPE_SECRET_KEY 



@login_required
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
    
    # Get selected date or default to today
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Prepare months data for dropdown
    months = []
    for i in range(1, 13):
        months.append({
            'value': i,
            'name': month_name[i],
            'selected': i == selected_date.month
        })
    
    # Prepare years data for dropdown (current year -5 to +5)
    current_year = datetime.now().year
    years = range(current_year - 5, current_year + 6)
    
    # Calculate calendar days
    first_day_of_month = selected_date.replace(day=1)
    weekday_of_first = first_day_of_month.weekday()
    days_in_month = monthrange(selected_date.year, selected_date.month)[1]
    
    days = []
    # Previous month days
    prev_month_days = weekday_of_first
    prev_month = first_day_of_month - timedelta(days=prev_month_days)
    for i in range(prev_month_days):
        day_date = prev_month + timedelta(days=i)
        days.append({
            'date': day_date,
            'is_current_month': False,
            'slot_count': AvailableSlot.objects.filter(
                practitioner=practitioner,
                status='available',
                date=day_date
            ).count()
        })
    
    # Current month days
    for day in range(1, days_in_month + 1):
        day_date = selected_date.replace(day=day)
        days.append({
            'date': day_date,
            'is_current_month': True,
            'slot_count': AvailableSlot.objects.filter(
                practitioner=practitioner,
                status='available',
                date=day_date
            ).count()
        })
    
    # Next month days
    next_month_days = 42 - len(days)
    next_month = first_day_of_month + timedelta(days=days_in_month)
    for i in range(next_month_days):
        day_date = next_month + timedelta(days=i)
        days.append({
            'date': day_date,
            'is_current_month': False,
            'slot_count': 0
        })
    
    available_slots = AvailableSlot.objects.filter(
        practitioner=practitioner,
        status='available',
        date=selected_date
    ).order_by('start_time')
    
    context = {
        'practitioner': practitioner,
        'selected_date': selected_date,
        'today': timezone.now().date(),
        'days': days,
        'available_slots': available_slots,
        'specialty_name': practitioner.get_specialty_display(),
        'months': months,
        'years': years,
        'current_year': current_year,
    }
    return render(request, 'patientdashboard/available_slots.html', context)













def book_appointment(request):
    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        reason = request.POST.get('reason', '').strip()
        urgency = request.POST.get('urgency', 'normal')
        patient_id = request.session.get('patient_id')  # Ensure the patient is logged in

        if not patient_id:
            return redirect('frontend:patient_login')  # Redirect to login if not logged in

        if not slot_id:
            return render(request, 'patientdashboard/booking_failed.html', 
                          {'error': 'Invalid slot selection.'})  # Show error page

        # Validate reason is provided
        if not reason:
            return render(request, 'patientdashboard/booking_failed.html', 
                          {'error': 'Please provide a reason for your appointment.'})

        # Validate urgency choice
        valid_urgency_choices = ['normal', 'urgent', 'emergency']
        if urgency not in valid_urgency_choices:
            urgency = 'normal'  # Default to normal if invalid choice

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

        # Create the appointment with reason and urgency
        try:
            appointment = Appointment.objects.create(
                patient=patient,
                slot=slot,
                practitioner=practitioner,
                reason=reason,
                urgency=urgency,
                payment_status="Pending"  # New appointments are unpaid by default
            )
            slot.status = 'booked'
            slot.save()
            
            # Send notifications to both patient and practitioner
            from practitionerdashboard.notifications import notify_appointment_booked
            notify_appointment_booked(appointment)
            
        except Exception as e:
            return render(request, 'patientdashboard/booking_failed.html', 
                          {'error': f'Database error: {str(e)}'})

        # Redirect to payment page with the appointment id
        return redirect('patientdashboard:payment', appointment_id=appointment.id)

    return render(request, 'patientdashboard/booking_failed.html', 
                  {'error': 'Invalid request method.'})








def booking(request):
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


def appointments_patients(request):
    patient_id = request.session.get('patient_id')

    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id)

        notifications = Notification.objects.filter(recipient=patient, is_read=False).order_by('-created_at')

        appointments = Appointment.objects.filter(patient=patient).select_related('practitioner', 'slot')

        # Debug: Print appointment details
        for appointment in appointments:
            print(f"🔍 Appointment {appointment.id}: Status={appointment.status}, Video Link={appointment.video_call_link}, Meeting ID={appointment.meeting_id}")

        prescriptions = Prescription.objects.filter(patient=patient)
        
        billing_records = Billing.objects.filter(appointment__patient_id=patient_id)

        return render(request, 'patientdashboard/appointments_patients.html', {
            'patient': patient,
            'notifications': notifications,
            'appointments': appointments,
            'prescriptions': prescriptions,
            'billing_records': billing_records
        })
    else:
        return redirect('frontend:patient_login')
    
    
    
    
def eligible_practitioners_for_review(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('frontend:patient_login')

    patient = get_object_or_404(Patient, id=patient_id)

    # Get practitioners with confirmed appointments
    confirmed_appointments = Appointment.objects.filter(
        patient=patient,
        status='Accepted' 
    ).select_related('practitioner')

    practitioners = [appt.practitioner for appt in confirmed_appointments]

    # Fetch reviews and replies
    practitioner_ids = [p.id for p in practitioners]
    reviews = Review.objects.filter(patient=patient, practitioner_id__in=practitioner_ids)

    # Build patient_reviews with replies
    patient_reviews = {}
    for review in reviews:
        replies = review.replies.all()  # Related name in model
        patient_reviews[review.practitioner_id] = {
            'rating': review.rating,
            'feedback': review.feedback,
            'created_at': review.created_at,
            'replies': replies,
        }
        
        print("Replies:",replies)
    return render(request, 'patientdashboard/eligible_reviews.html', {
        'patient': patient,
        'practitioners': practitioners,
        'patient_reviews': patient_reviews,
    })


   
   
 




def review_practitioner(request, practitioner_id):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('frontend:patient_login')

    practitioner = get_object_or_404(Practitioner, id=practitioner_id)
    patient = get_object_or_404(Patient, id=patient_id)

    # Check if the patient has already submitted a review
    existing_review = Review.objects.filter(patient=patient, practitioner=practitioner).first()
    if existing_review:
        messages.error(request, "You have already submitted a review for this practitioner. You cannot submit it again.")
        return redirect('patientdashboard:eligible_practitioners_for_review')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback')

        Review.objects.create(
            patient=patient,
            practitioner=practitioner,
            rating=rating,
            feedback=feedback
        )
        messages.success(request, "Your review has been submitted successfully.")
        return redirect('patientdashboard:eligible_practitioners_for_review')

    return render(request, 'patientdashboard/review.html', {
        'practitioner': practitioner
    })
    






def telemedicine(request):
    return render(request, 'patientdashboard/telemedicine.html')



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




def booking_success(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient_id=request.session.get('patient_id'))
    return render(request, 'patientdashboard/booking_success.html', {'appointment': appointment})


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
    
    patient_id = request.session.get('patient_id')

    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id)
        
    context = {
        'exercises': [
            {'name': 'Basic Yoga', 'url': 'patientdashboard:yoga_tutorial', 'image': 'basic_yoga.jpg'},
            {'name': 'Leg Exercises', 'url': 'patientdashboard:leg_exercises_tutorial', 'image': 'legs.jpg'},
            {'name': 'Arm Exercises', 'url': 'patientdashboard:arm_exercises_tutorial', 'image': 'arms.jpg'},
        ],
        'patient': patient,
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




def specialty_selection(request):
    specialties = Practitioner.SPECIALTY_CHOICES
    patient_id = request.session.get('patient_id')

    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'patientdashboard/specialty_selection.html', {
        'specialties': specialties,
        'patient': patient,
    })
    
    

def practitioners_list(request, specialty):
    practitioners = Practitioner.objects.filter(specialty=specialty)
    specialty_name = dict(Practitioner.SPECIALTY_CHOICES).get(specialty)
    return render(request, 'patientdashboard/practitioners_list.html', {
        'practitioners': practitioners,
        'specialty_name': specialty_name,
        'specialty': specialty
    })




def book_video_consultation(request, slot_id):
    print(f"Received request to book slot {slot_id}")
    
    if request.method == 'POST':
        patient_id = request.session.get('patient_id')
        print(f"Patient ID from session: {patient_id}")

        if not patient_id:
            print("No patient ID found, redirecting to login")
            return JsonResponse({'error': 'User not logged in', 'redirect_url': '/patient/login/'}, status=401)

        try:
            # Parse JSON data for reason and urgency
            import json
            data = json.loads(request.body) if request.body else {}
            reason = data.get('reason', '').strip()
            urgency = data.get('urgency', 'normal')
            
            # Validate reason
            if not reason:
                return JsonResponse({'error': 'Please provide a reason for your appointment'}, status=400)
            
            # Validate urgency
            valid_urgency_choices = ['normal', 'urgent', 'emergency']
            if urgency not in valid_urgency_choices:
                urgency = 'normal'
            
            patient = Patient.objects.get(id=patient_id)
            print(f"Patient found: {patient}")
            
            slot = get_object_or_404(AvailableSlot, pk=slot_id, status='available')
            print(f"Slot details: {slot}")

            if hasattr(slot, 'appointment'):
                print("Slot is already booked")
                return JsonResponse({'error': 'This time slot is already booked'}, status=400)

            # Store reason and urgency in session for later use
            request.session['booking_reason'] = reason
            request.session['booking_urgency'] = urgency
            request.session['booking_slot_id'] = slot_id

            print("Creating Stripe checkout session...")
            
            # Get practitioner price, default to 50 if not set
            practitioner_price = slot.practitioner.price or 50.00
            print(f"Practitioner: Dr. {slot.practitioner.first_name} {slot.practitioner.last_name}")
            print(f"Original price: {slot.practitioner.price}")
            print(f"Using price: ${practitioner_price}")
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Consultation with Dr. {slot.practitioner.first_name} {slot.practitioner.last_name}',
                            'description': f'Medical consultation session',
                        },
                        'unit_amount': int(practitioner_price * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(f"/patient-dashboard/payment-success/{slot.id}/"),
                cancel_url=request.build_absolute_uri(f"/patient-dashboard/cancel/{slot.id}/"),
            )
            
            print(f"Stripe Checkout URL: {checkout_session.url}")
            return JsonResponse({'redirect_url': checkout_session.url})

        except Patient.DoesNotExist:
            print("Patient profile not found")
            return JsonResponse({'error': 'Patient profile not found'}, status=404)
        
        except json.JSONDecodeError:
            print("Invalid JSON data")
            return JsonResponse({'error': 'Invalid request data'}, status=400)
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return JsonResponse({'error': f"An error occurred: {str(e)}"}, status=500)
        



def payment_success(request, slot_id):
    try:
        slot = get_object_or_404(AvailableSlot, pk=slot_id, status='available')
        patient_id = request.session.get('patient_id')

        if not patient_id:
            return redirect('frontend:patient_login')

        patient = Patient.objects.get(id=patient_id)

        # Get reason and urgency from session
        reason = request.session.get('booking_reason', '')
        urgency = request.session.get('booking_urgency', 'normal')

        # Create appointment with reason and urgency
        appointment = Appointment.objects.create(
            patient=patient,
            slot=slot,
            practitioner=slot.practitioner,
            status='Pending',
            amount=slot.practitioner.price,
            reason=reason,
            urgency=urgency
        )

        # Clear booking data from session
        request.session.pop('booking_reason', None)
        request.session.pop('booking_urgency', None)
        request.session.pop('booking_slot_id', None)

        # Create billing record
        Billing.objects.create(
            appointment=appointment,
            amount=slot.practitioner.price,
            is_paid=True
        )



        messages.success(request, "Payment successful! Appointment booked.")
        return redirect('patientdashboard:booking_success', appointment_id=appointment.id)

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('patientdashboard:available_slots', practitioner_id=slot.practitioner.id)


    



def list_all_bills(request):
    print("📌 list_all_bills view is being executed!")  # Debugging print
    sys.stdout.flush()
    
    patient_id = request.session.get('patient_id')

    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id)
    
    # Check if user is authenticated
    if request.method == 'GET':
        patient_id = request.session.get('patient_id')  # Ensure the patient is logged in

        if not patient_id:
            return redirect('frontend:patient_login')  # Redirect to login if not logged in
        
        
        
        

    
    try:
        # Get all billing records for this patient
        bills = Billing.objects.filter(
            appointment__patient_id=patient_id
        ).order_by('-issued_date')
        
        print(f"💰 Bills found: {bills.count()}")  # Print bills count
        
        context = {
            'bills': bills,
            'patient': patient,
        }
        return render(request, 'patientdashboard/bills_payments.html', context)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('patientdashboard:appointments_patients')
    
from xhtml2pdf import pisa 



def view_bill(request, bill_id):
    print(f"\n\n=== ENTERING view_bill ===")
    print(f"Requested bill_id: {bill_id}")
    
    # Check authentication
    if request.method == 'GET':
        patient_id = request.session.get('patient_id')  # Ensure the patient is logged in

        if not patient_id:
            return redirect('frontend:patient_login')  # Redirect to login if not logged in

    
    # Debug queries
    print(f"Patient {patient_id} has {Billing.objects.filter(appointment__patient_id=patient_id).count()} bills")
    print(f"Bill exists: {Billing.objects.filter(id=bill_id).exists()}")
    print(f"Bill belongs to patient: {Billing.objects.filter(id=bill_id, appointment__patient_id=patient_id).exists()}")
    
    try:
        bill = Billing.objects.get(
            id=bill_id,
            appointment__patient_id=patient_id
        )
        print(f"Rendering bill: {bill.invoice_number}")
        
        context = {
            'bill': bill,
            'appointment': bill.appointment,
            'practitioner': bill.appointment.practitioner,
        }
        return render(request, 'patientdashboard/bill_detail.html', context)
        
    except Billing.DoesNotExist:
        print("Bill not found or doesn't belong to patient")
        messages.error(request, "Bill not found or access denied.")
        return redirect('patientdashboard:all_bills')
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        messages.error(request, "An unexpected error occurred.")
        return redirect('patientdashboard:all_bills')
    





def download_bill_pdf(request, bill_id):
    print(f"\n\n=== ENTERING download_bill_pdf ===")
    
    patient_id = request.session.get('patient_id')

    if not patient_id:
        return redirect('frontend:patient_login')

    
    try:
        bill = Billing.objects.get(id=bill_id, appointment__patient_id=patient_id)
        template_path = 'patientdashboard/bill_pdf_template.html'


        


        context = {
            'bill': bill,
            'appointment': bill.appointment,
            'practitioner': bill.appointment.practitioner,
        }
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="bill_{bill.invoice_number}.pdf"'
        
        template = get_template(template_path)
        html = template.render(context)

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            print("PDF generation error")
            messages.error(request, "Error generating PDF.")
            return redirect('patientdashboard:all_bills')
        return response

    except Billing.DoesNotExist:
        print("Bill not found or doesn't belong to patient")
        messages.error(request, "Bill not found or access denied.")
        return redirect('patientdashboard:all_bills')
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        messages.error(request, "An unexpected error occurred.")
        return redirect('patientdashboard:all_bills')







def cancel_appointment(request, appointment_id):
    """Cancel the appointment by updating its status."""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "Cancelled":  # Prevent duplicate cancellations
        appointment.status = "Cancelled"
        appointment.save()
        
        # Send notifications to practitioner about patient cancellation
        from practitionerdashboard.notifications import notify_appointment_cancelled
        notify_appointment_cancelled(appointment, reason="Cancelled by patient", cancelled_by="patient")
        
        messages.success(request, "Appointment has been cancelled.")
    
    return JsonResponse({"success": True, "message": "Appointment cancelled successfully"})




@csrf_exempt
def submit_symptoms(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        symptoms = request.POST.get('symptoms')

        # Get appointment and patient from IDs
        appointment = get_object_or_404(Appointment, id=appointment_id)
        patient_id = request.session.get('patient_id')



        if not patient_id:
            messages.error(request, 'Patient information not found. Please log in again.')
            return redirect('patient_dashboard:appointments_patients')

        patient = get_object_or_404(Patient, id=patient_id)

        # Create symptom record
        Symptom.objects.create(
            appointment=appointment,
            patient=patient,
            details=symptoms
        )

        messages.success(request, 'Symptoms submitted successfully.')
        return redirect('patient_dashboard:symptoms_list')





def symptoms_list(request):
    patient_id = request.session.get('patient_id')
    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id)
        
    if not patient_id:
        return redirect('patientdashboard:login')  # Or your login page

    symptoms = Symptom.objects.filter(patient_id=patient_id).order_by('-created_at')
    return render(request, 'patientdashboard/symptoms_list.html', 
                  
        {'symptoms': symptoms,'patient': patient,}
        
        )




@csrf_exempt
def add_symptom(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        details = request.POST.get('details')
        patient_id = request.session.get('patient_id')

        if appointment_id and details and patient_id:
            appointment = get_object_or_404(Appointment, id=appointment_id)
            patient = get_object_or_404(Patient, id=patient_id)
            Symptom.objects.create(appointment=appointment, patient=patient, details=details)
        return redirect('patientdashboard:symptoms_list')

    appointments = Appointment.objects.all()  # optionally filter by patient
    return render(request, 'patientdashboard/add_symptom.html', {'appointments': appointments})


def delete_symptom(request, symptom_id):
    symptom = get_object_or_404(Symptom, id=symptom_id)
    if symptom.patient.id == request.session.get('patient_id'):
        symptom.delete()
    return redirect('patientdashboard:symptoms_list')


@csrf_exempt
def mark_notifications_read(request):
    """Mark all notifications as read for the current patient"""
    if request.method == 'POST':
        patient_id = request.session.get('patient_id')
        if not patient_id:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        try:
            patient = Patient.objects.get(id=patient_id)
            # Mark all notifications as read
            Notification.objects.filter(recipient=patient, is_read=False).update(is_read=True)
            return JsonResponse({'success': True})
        except Patient.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Patient not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def mark_notification_read(request):
    """Mark a specific notification as read"""
    if request.method == 'POST':
        patient_id = request.session.get('patient_id')
        if not patient_id:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        try:
            import json
            data = json.loads(request.body)
            notification_id = data.get('notification_id')
            
            patient = Patient.objects.get(id=patient_id)
            
            # Try to find and mark the notification as read
            try:
                notification = Notification.objects.get(id=notification_id, recipient=patient)
                notification.is_read = True
                notification.save()
                return JsonResponse({'success': True})
            except Notification.DoesNotExist:
                # If it's not a database notification, just return success
                # (it might be a generated notification from appointments, etc.)
                return JsonResponse({'success': True})
                
        except Patient.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Patient not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def all_notifications(request):
    """View all notifications for the patient"""
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('frontend:patient_login')
    
    try:
        patient = Patient.objects.get(id=patient_id)
        
        # Get all notifications from database
        db_notifications = Notification.objects.filter(recipient=patient).order_by('-created_at')
        
        # Get recent appointments for notifications
        recent_appointments = Appointment.objects.filter(
            patient=patient,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('practitioner', 'slot').order_by('-created_at')
        
        # Get recent prescriptions
        recent_prescriptions = Prescription.objects.filter(
            patient=patient,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('practitioner').order_by('-created_at')
        
        context = {
            'patient': patient,
            'db_notifications': db_notifications,
            'recent_appointments': recent_appointments,
            'recent_prescriptions': recent_prescriptions,
        }
        
        return render(request, 'patientdashboard/all_notifications.html', context)
        
    except Patient.DoesNotExist:
        return redirect('frontend:patient_login')













def get_chat_room_api(request):
    """API endpoint to get or create chat room for patient-practitioner pair"""
    patient_id = request.session.get('patient_id')
    
    if not patient_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            practitioner_id = data.get('practitioner_id')
            
            if not practitioner_id:
                return JsonResponse({'success': False, 'error': 'Practitioner ID required'}, status=400)
            
            # Check if there's an accepted appointment between them
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
            from user_account.models import Practitioner
            
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