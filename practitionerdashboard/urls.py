
from django.contrib import admin
from django.urls import path, include
from practitionerdashboard import views
app_name='practitioner_dashboard'
urlpatterns = [  
    path('', views.dashboard_view, name='dashboard'),
    
    # Main pages
    path('appointments/', views.appointment, name='appointments'),  # FIXED: Added missing appointment URL
    path('accepted-appointments/', views.accepted_appointments_view, name='accepted_appointments'),  # NEW: Dedicated accepted appointments view
    path('telemedicine/', views.telemedicine, name='telemedicine'),
    path('mypatient/', views.mypatient, name='mypatient'),
    path('schedule-timming/', views.schedule_timming, name='schedule_timming'),
    
    # Slot management
    path('add-slot/', views.add_slot, name='add_slot'),
    path('remove-slot/<int:slot_id>/', views.remove_slot, name='remove_slot'),
    
    # Prescription management
    path("prescription/add/<int:patient_id>/", views.add_prescription, name="add_prescription"),

    # Other features
    path('reviews/', views.practitioner_reviews, name='reviews'),
    path('chat/', views.chat, name='chat'),
    path('start-video-call/<int:patient_id>/', views.start_video_call, name='start_video_call'),
    
    # Profile management
    path('practitioner-profile/', views.CompleteProfile, name='practitioner_profile'),
    
    # Appointment actions
    path('appointments/<int:appointment_id>/accept/', views.accept_appointment, name='accept_appointment'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    
    # Patient details
    path('patient/<int:appointment_id>/', views.get_patient_details, name='get_patient_details'),
    
    # API endpoints for alert bell
    path('api/pending-appointments/', views.get_pending_appointments_api, name='pending_appointments_api'),
    path('appointments/<int:appointment_id>/<str:status>/', views.update_appointment_status_api, name='update_appointment_status_api'),
    
    # Chat room API
    path('api/get-chat-room/', views.get_chat_room_api, name='get_chat_room_api'),
    
    # Migration endpoint
    path('api/migrate-to-zoom/', views.migrate_jitsi_to_zoom_view, name='migrate_to_zoom'),
    
    # Completion pages
    path('cancellation-completion/', views.Cancel_Complete, name="cancellation_completion"),
    
    # Notification endpoints
    path('api/notifications/', views.get_practitioner_notifications, name='get_notifications'),
    path('api/notifications/mark-read/', views.mark_practitioner_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-all-read/', views.mark_all_practitioner_notifications_read, name='mark_all_notifications_read'),
    
    # Enhanced appointment management with notifications
    path('api/appointments/<int:appointment_id>/<str:action>/', views.handle_appointment_action, name='handle_appointment_action'),
    path('api/appointments/<int:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('api/notify-availability/', views.notify_availability_added, name='notify_availability_added'),        
]






    
