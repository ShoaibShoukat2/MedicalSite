from django.shortcuts import render, redirect,get_object_or_404
from user_account.models import Practitioner

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from user_account.models import Practitioner
from .models import AvailableSlot
import json
from django.shortcuts import render, get_object_or_404, redirect
from user_account.models import Practitioner

from django.http import JsonResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

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
    # Check if practitioner is logged in
    practitioner_id = request.session.get('practitioner_id')
    if not practitioner_id:
        return redirect('frontend:practitioner_login')  # Redirect to login if not authenticated

    # Get the logged-in practitioner
    practitioner = get_object_or_404(Practitioner, id=practitioner_id)
    slots = practitioner.available_slots.all()
    return render(request, 'practitionerdashboard/schedule_time.html', {'slots': slots})

import json

def add_slot(request):
    # Check if the practitioner is logged in
    practitioner_id = request.session.get('practitioner_id')
    if not practitioner_id:
        return JsonResponse({'success': False, 'error': 'You must be logged in to add a slot.'}, status=403)

    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data from the request
            practitioner = get_object_or_404(Practitioner, id=practitioner_id)  # Get practitioner by session ID
            day_of_week = data.get('day_of_week')
            start_time = data.get('start_time')
            end_time = data.get('end_time')

            # Validate required fields
            if not day_of_week or not start_time or not end_time:
                return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)

            # Create the slot
            slot = AvailableSlot.objects.create(
                practitioner=practitioner,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
            )
            return JsonResponse({'success': True, 'slot_id': slot.id})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data.'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

def remove_slot(request, slot_id):
    if request.method == "POST":
        slot = get_object_or_404(AvailableSlot, id=slot_id)
        slot.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


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









