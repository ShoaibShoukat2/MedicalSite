from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'patientdashboard/dashboard.html')

def appointment(request):
    return render(request, 'patientdashboard/book_appointment.html')

def search(request):
    return render(request, 'patientdashboard/search.html')

def booking(request):
    return render(request, 'patientdashboard/booking.html')

def payment(request):
    return render(request, 'patientdashboard/payment.html')





def booking_success(request):
    return render(request, 'patientdashboard/booking_success.html')



def view_invoice(request):
    return render(request, 'patientdashboard/view_invoice.html')