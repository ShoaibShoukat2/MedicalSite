
from django.db.models import Q
from user_account.models import Practitioner ,Patient # Assuming Practitioner is the model for doctors/practitioners

from django.shortcuts import render, get_object_or_404, redirect

from django.core.paginator import Paginator

def patient_base(request):
    return render(request, 'patientdashboard/patient_base.html')


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

def booking(request):
    return render(request, 'patientdashboard/booking.html')

def chat(request):
    return render(request, 'patientdashboard/chat.html')

def appointments_patients(request):
    if request.user.is_authenticated:  # Check if user is logged in
        try:
            # Fetch the patient data using the email of the logged-in user
            patient = get_object_or_404(Patient, email=request.user.email)
            return render(request, 'patientdashboard/appointments_patients.html', {'patient': patient})
        except Patient.DoesNotExist:
            # Redirect or show an error if no matching patient record is found
            return render(request, 'patientdashboard/appointments_patients.html', {'patient': None})
    else:
        # Redirect to login page if user is not authenticated
        return redirect('frontend:patient_login')  # Update with your login URL name


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



