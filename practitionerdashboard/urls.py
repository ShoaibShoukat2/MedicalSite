
from django.contrib import admin
from django.urls import path, include
from practitionerdashboard import views
app_name='practitioner_dashboard'
urlpatterns = [  
    path('', views.dashboard_view, name='dashboard'),


    path('telemedicine/', views.telemedicine, name='telemedicine'),
    path('mypatient/', views.mypatient, name='mypatient'),
    path('schedule-timming/', views.schedule_timming, name='schedule_timming'),
    path('add-slot/', views.add_slot, name='add_slot'),
    path('remove-slot/<int:slot_id>/', views.remove_slot, name='remove_slot'),  # Add this line
    path("prescription/add/<int:patient_id>/", views.add_prescription, name="add_prescription"),

    path('reviews/', views.practitioner_reviews, name='reviews'),
    path('chat/', views.chat, name='chat'),
    path('start-video-call/<int:patient_id>/', views.start_video_call, name='start_video_call'),

    
    
    
    # Profile url
    path('practitioner-profile/', views.CompleteProfile, name='practitioner_profile'),
    
    
    path('appointments/<int:appointment_id>/Accepted/', views.accept_appointment, name='accept_appointment'),
    path('appointments/<int:appointment_id>/Cancelled/', views.cancel_appointment, name='cancel_appointment'),
    
    path('patient/<int:appointment_id>/', views.get_patient_details, name='get_patient_details'),
    
    path('cancellation-completion/', views.Cancel_Complete, name="cancellation_completion"),

        
    
    
]





