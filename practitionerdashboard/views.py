from django.shortcuts import render

# Create your views here.

def dashboard_view(request):
    return render(request, 'practitionerdashboard/dashboard.html')


def telemedicine(request):
    return render(request, 'practitionerdashboard/telemedicine.html')

def appointment(request):
    return render(request, 'practitionerdashboard/appointment.html')



def chat(request):
    return render(request, 'practitionerdashboard/chat.html')

def reviews(request):
    return render(request, 'practitionerdashboard/reviews.html')


def schedule_timming(request):
    return render(request, 'practitionerdashboard/schedule_time.html')


def mypatient(request):
    return render(request, 'practitionerdashboard/mypatient.html')