
from django.contrib import admin
from django.urls import path, include

from patientdashboard import views
app_name='patient_dashboard'
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),

]

