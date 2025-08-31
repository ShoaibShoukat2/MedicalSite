from django.contrib import admin
from .models import Appointment,Review,Billing, Symptom, Reply, Notification
# Register your models here.




@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'practitioner', 'slot', 'status', 'created_at')  # Fields to show in list view
    list_filter = ('status', 'practitioner')  # Add filtering options
    search_fields = ('patient__name', 'practitioner__name')  # Enable search
    ordering = ('-created_at',)  # Order by newest first
    



admin.site.register(Review)
admin.site.register(Billing)



@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'appointment', 'created_at')
    search_fields = ('details', 'patient__user__first_name', 'appointment__id')
    list_filter = ('created_at',)


admin.site.register(Reply)
admin.site.register(Notification)

