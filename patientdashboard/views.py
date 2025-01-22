from django.shortcuts import render

def patient_base(request):
    return render(request, 'patientdashboard/patient_base.html')



def search(request):
    return render(request, 'patientdashboard/search.html')

def booking(request):
    return render(request, 'patientdashboard/booking.html')

def chat(request):
    return render(request, 'patientdashboard/chat.html')



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



def view_invoice(request):
    return render(request, 'patientdashboard/view_invoice.html')



