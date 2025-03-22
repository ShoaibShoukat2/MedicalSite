from django.urls import path
from .views import *

app_name = 'frontend'


urlpatterns = [
    
    path('', index, name='index'),
    path('patient/', patient_signup, name='patient_signup'),
    path('practitioner/', practitioner_signup, name='practitioner_signup'),
    path('success/', success, name='success'),

   
    
    path('patient/login/', patient_login, name='patient_login'),
    path('Practitioner/login/', practitioner_login, name='practitioner_login'),
    path('verify_otp/', verify_otp, name='patient_verify_otp'),
    path('practitioner_verify_otp/', practitioner_verify_otp, name='practitioner_verify_otp'),
    
    path('logout/', logout, name='logout'),
     
     
    # Reset Password urls
    
    path("forgot_password/", forgot_password, name="forgot_password"),
    path("reset_password/<str:token>/", reset_password, name="reset_password"),
    
    
    
    # Reset Password Practinoar urls
    
    
    path('practitioner/forgot-password/', practitioner_forgot_password, name='practitioner_forgot_password'),
    path('practitioner/reset-password/', practitioner_reset_password, name='practitioner_reset_password'),
    
    path('temp_index',temp_index, name="temp-page")
   
   
]






