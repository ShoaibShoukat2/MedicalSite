from django.contrib import admin
from .models import Appointment,Review,Billing
# Register your models here.




@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'practitioner', 'slot', 'status', 'created_at')  # Fields to show in list view
    list_filter = ('status', 'practitioner')  # Add filtering options
    search_fields = ('patient__name', 'practitioner__name')  # Enable search
    ordering = ('-created_at',)  # Order by newest first
    
    


admin.site.register(Review)
admin.site.register(Billing)





