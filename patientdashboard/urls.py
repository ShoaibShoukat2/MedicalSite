
from django.contrib import admin
from django.urls import path, include

from patientdashboard import views
app_name='patient_dashboard'
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('book_appointment/', views.appointment, name='appointment'),
    path('search/', views.search, name='search'),
    path('booking/', views.booking, name='booking'),
    path('payment/', views.payment, name='payment'),
    path('booking_success/', views.booking_success, name='booking_success'),
    path('view_invoice/', views.view_invoice, name='view_invoice'),
    path('doctor_profile/', views.doctor_profile, name='doctor_profile'),
    path('telemedicine/', views.telemedicine, name='telemedicine'),
    path('chat/', views.chat, name='chat'),







]

