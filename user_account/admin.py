from django.contrib import admin

from .models import *
# Register your models here.


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('greeting', 'first_name', 'last_name', 'gender', 'mobile_phone', 'date_of_birth', 'email',)
    search_fields = ('first_name', 'last_name', 'email', 'mobile_phone')
    list_filter = ('gender', 'date_of_birth')  # You can filter by gender or date of birth
    ordering = ('last_name', 'first_name')

@admin.register(Practitioner)
class PractitionerAdmin(admin.ModelAdmin):
    list_display = (
        'id',  # Display the primary key for easy reference
        'first_name',
        'last_name',
        'get_civility_display',  # Custom display for civility
        'get_specialty_display',  # Custom display for specialty
        'email',
        'doctor_type',
        'price',
        'terms_accepted',  # Boolean field to show whether terms were accepted
    )
    list_filter = ('doctor_type', 'specialty', 'terms_accepted')  # Filters in the sidebar
    search_fields = ('first_name', 'last_name', 'email')  # Search bar fields
    ordering = ('last_name', 'first_name')  # Default ordering

    def get_specialty_display(self, obj):
        return obj.get_specialty_display()
    get_specialty_display.short_description = "Specialty"

    def get_civility_display(self, obj):
        return obj.get_civility_display()
    get_civility_display.short_description = "Civility"

