
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

    path('reviews/', views.reviews, name='reviews'),
    path('chat/', views.chat, name='chat'),
    
    
    
    # Profile url
    path('practitioner-profile/', views.CompleteProfile, name='practitioner_profile'),
    
    
]



