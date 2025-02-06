
import datetime
import json
from django.db.models import Q
from patientdashboard.models import Appointment, Notification
from user_account.models import Practitioner ,Patient # Assuming Practitioner is the model for doctors/practitioners

from django.shortcuts import render, get_object_or_404, redirect
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

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from user_account.models import Patient
from practitionerdashboard.models import AvailableSlot
# patientdashboard/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from user_account.models import Practitioner
from practitionerdashboard.models import AvailableSlot
from django.utils.timezone import now
import json

from django.http import JsonResponse
from user_account.models import Practitioner
from django.http import JsonResponse
from user_account.models import Practitioner

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

        # ✅ Check if patient has an unpaid appointment
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

        # ✅ Ensure correct ForeignKey reference
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

        # ✅ Redirect to success page after successful booking
        return redirect('patientdashboard:payment')

    return render(request, 'patientdashboard/booking_failed.html', 
                  {'error': 'Invalid request method.'})


from user_account.models import Practitioner

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

from django.shortcuts import render, get_object_or_404, redirect
from user_account.models import Patient  # Adjust the import based on your app structure
from django.shortcuts import render, redirect, get_object_or_404
from user_account.models import Patient
from django.shortcuts import render, get_object_or_404, redirect
from .models import Appointment, Patient, Notification

def appointments_patients(request):
    # Check if the session contains patient_id
    patient_id = request.session.get('patient_id')

    if patient_id:
        # Retrieve the Patient object using the session ID
        patient = get_object_or_404(Patient, id=patient_id)

        # Fetch unread notifications for this patient
        notifications = Notification.objects.filter(recipient=patient, is_read=False).order_by('-created_at')

        # Fetch all booked appointments for this patient
        appointments = Appointment.objects.filter(patient=patient).select_related('practitioner', 'slot')

        return render(request, 'patientdashboard/appointments_patients.html', {
            'patient': patient,
            'notifications': notifications,  # Pass notifications to the template
            'appointments': appointments  # Pass appointments to the template
        })
    else:
        # Redirect to login page if the session is not valid
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


def practitioner_profile(request, pk):
    practitioner = get_object_or_404(Practitioner, pk=pk)  # Fetch practitioner by primary key (ID)
    return render(request, 'patientdashboard/doctor_profile.html', {'practitioner': practitioner})


def booking_success(request):
    # Fetch the appointment details
    return render(request, 'patientdashboard/booking_success.html')

def view_invoice(request):
    return render(request, 'patientdashboard/view_invoice.html')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PatientProfileForm, PatientPasswordForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password, check_password
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