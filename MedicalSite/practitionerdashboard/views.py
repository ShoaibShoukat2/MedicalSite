from django.shortcuts import render, redirect,get_object_or_404
from user_account.models import Practitioner

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



def CompleteProfile(request):
    
    context = {}
    
    practitioner_id = request.session.get('practitioner_id')
    
    
    # Check if practitioner ID exists in the session
    if not practitioner_id:
        context['error_message'] = "No practitioner ID found in the session. Please log in."
        return render(request, 'practitionerdashboard/profile.html', context)
    
    
     # Fetch the practitioner instance or return a 404
    practitioner = get_object_or_404(Practitioner, id=practitioner_id)
    
    
    
    if request.method == 'POST':
        # Retrieve form data
        photo = request.FILES.get('photo')
        price = request.POST.get('price')
        description = request.POST.get('description')

        # Validate input and update practitioner fields
        if photo:
            practitioner.photo = photo
        if price:
            try:
                practitioner.price = float(price)
            except ValueError:
                context['error_message'] = "Invalid price. Please enter a valid number."
                return render(request, 'practitionerdashboard/profile.html', context)
            
        if description:
            practitioner.description = description
            
           # Save the changes
        practitioner.save()
        
        context['success_message'] = "Practitioner details updated successfully!"
        
        
        
        
    
    return render(request,'practitionerdashboard/profile.html',context)









