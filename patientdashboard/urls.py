
from django.contrib import admin
from django.urls import path, include

from patientdashboard import views
app_name='patient_dashboard'
urlpatterns = [
    path('', views.appointments_patients, name='appointments_patients'),

    

    path('search/', views.search_practitioners, name='search'),
    

     
    path('api/practitioners/', views.get_practitioners_by_specialization, name='get_practitioners_by_specialization'),
    path('available-slots/<int:practitioner_id>/', views.available_slots, name='available_slots'),
    path('book-consultation/<int:slot_id>/', views.book_video_consultation, name='book_video_consultation'),
    path('payment-success/<int:slot_id>/', views.payment_success, name='payment_success'),
    
    
   
    
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    
    path('booking-success/<int:appointment_id>/', views.booking_success, name='booking_success'),
    path('booking/', views.booking, name='booking'),  # Your existing booking page
    path('specialties/', views.specialty_selection, name='specialty_selection'),
    path('specialties/<str:specialty>/', views.practitioners_list, name='practitioners_list'),
    path('booking_success/', views.booking_success, name='booking_success'),
    path('view_invoice/', views.view_invoice, name='view_invoice'),
    path('practitioner/<int:pk>/', views.practitioner_profile, name='practitioner_profile'),
    path('telemedicine/', views.telemedicine, name='telemedicine'),
    path('profile/', views.patient_profile, name='profile'),
    
    

    
    
    
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments_patients/', views.appointments_patients, name='appointments_patients'),


    path('chat/', views.chat, name='chat'),


    # New payment-related URLs
  
    path('exercises/', views.exercises_view, name='exercises'),
    path('exercises/yoga/', views.yoga_tutorial, name='yoga_tutorial'),
    path('exercises/leg-exercises/', views.leg_exercises_tutorial, name='leg_exercises_tutorial'),
    path('exercises/arm-exercises/', views.arm_exercises_tutorial, name='arm_exercises_tutorial'),
    path('exercises/update_progress/', views.update_progress, name='update_progress'),
    path('bills/', views.list_all_bills, name='all_bills'),
    path('bills/<int:bill_id>/', views.view_bill, name='view_bill'),
]




