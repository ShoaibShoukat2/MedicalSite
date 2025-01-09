from django.contrib import admin

from .models import *
# Register your models here.


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('greeting', 'first_name', 'last_name', 'gender', 'mobile_phone', 'date_of_birth', 'email')
    search_fields = ('first_name', 'last_name', 'email', 'mobile_phone')
    list_filter = ('gender', 'date_of_birth')  # You can filter by gender or date of birth
    ordering = ('last_name', 'first_name')

@admin.register(Practitioner)
class PractitionerAdmin(admin.ModelAdmin):
    list_display = ('civility', 'first_name', 'last_name', 'specialty', 'doctor_type', 'email')
    search_fields = ('first_name', 'last_name', 'email', 'specialty')
    list_filter = ('specialty', 'doctor_type')  # You can filter by specialty or doctor type
    ordering = ('last_name', 'first_name')
    
    


