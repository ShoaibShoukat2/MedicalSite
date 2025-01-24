
import datetime
import json
from django.db.models import Q
from patientdashboard.models import Appointment
from user_account.models import Practitioner ,Patient # Assuming Practitioner is the model for doctors/practitioners

from django.shortcuts import render, get_object_or_404, redirect

from django.core.paginator import Paginator

def patient_base(request):
    return render(request, 'patientdashboard/patient_base.html')

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

def book_appointment(request):
    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        patient_id = request.session.get('patient_id')  # Assuming the patient is logged in
        if not patient_id:
            return JsonResponse({'success': False, 'error': 'You must be logged in to book an appointment.'}, status=403)

        slot = get_object_or_404(AvailableSlot, id=slot_id, status='available')
        patient = get_object_or_404(Patient, id=patient_id)

        # Create an appointment and update slot status
        appointment = Appointment.objects.create(patient=patient, slot=slot)
        slot.status = 'booked'
        slot.save()

        return redirect('patientdashboard:booking_success')
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
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

def appointments_patients(request):
    # Check if the session contains patient_id
    patient_id = request.session.get('patient_id')
    if patient_id:
        # Retrieve the Patient object using the session ID
        patient = get_object_or_404(Patient, id=patient_id)
        return render(request, 'patientdashboard/appointments_patients.html', {'patient': patient})
    else:
        # Redirect to login page if the session is not valid
        return redirect('frontend:patient_login')


def payment(request):
    return render(request, 'patientdashboard/payment.html')




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



