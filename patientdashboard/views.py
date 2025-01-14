from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'patientdashboard/dashboard.html')

def appointment(request):
    return render(request, 'patientdashboard/book_appointment.html')

def patient_base(request):
    return render(request, 'patientdashboard/patient_base.html')
def search(request):
    return render(request, 'patientdashboard/search.html')

def booking(request):
    return render(request, 'patientdashboard/booking.html')



def appointments_patients(request):
    return render(request, 'patientdashboard/appointments_patients.html')
def payment(request):
    return render(request, 'patientdashboard/payment.html')




def telemedicine(request):
    return render(request, 'patientdashboard/telemedicine.html')



def doctor_profile(request):
    return render(request, 'patientdashboard/doctor_profile.html')



def booking_success(request):
    return render(request, 'patientdashboard/booking_success.html')



def chat(request):
    return render(request, 'patientdashboard/chat.html')

def reviews(request):
    return render(request, 'patientdashboard/reviews.html')


def schedule_timming(request):
    return render(request, 'patientdashboard/schedule_time.html')

def mypatient(request):
    return render(request, 'patientdashboard/mypatient.html')

def view_invoice(request):
    return render(request, 'patientdashboard/view_invoice.html')