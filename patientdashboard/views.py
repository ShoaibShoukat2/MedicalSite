
import json
from django.db.models import Q
from user_account.models import Practitioner ,Patient # Assuming Practitioner is the model for doctors/practitioners

from django.shortcuts import render, get_object_or_404, redirect

from django.core.paginator import Paginator

def patient_base(request):
    return render(request, 'patientdashboard/patient_base.html')


def booking(request):
    return render(request, 'patientdashboard/booking.html')


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
    return render(request, 'patientdashboard/booking_success.html')



def view_invoice(request):
    return render(request, 'patientdashboard/view_invoice.html')



