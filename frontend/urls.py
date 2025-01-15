from django.urls import path
from .views import *

app_name = 'frontend'


urlpatterns = [
    
    path('', index, name='index'),
    path('patient/', patient_signup, name='patient_signup'),
    path('practitioner/', practitioner_signup, name='practitioner_signup'),
    path('success/', success, name='success'),
    path('appointment/', appointment, name='appointment'),

   
    
    path('patient/login/', patient_login, name='patient_login'),
    path('Practitioner/login/', practitioner_login, name='practitioner_login'),
    path('verify_otp/', verify_otp, name='patient_verify_otp'),
    path('practinor_verify_otp/', practitioner_verify_otp, name='practinor_verify_otp'),
    
     path('logout/', logout, name='logout'),

]






