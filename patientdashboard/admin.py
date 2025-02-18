from django.contrib import admin
from .models import Appointment, Review, Reply
# Register your models here.

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('patient', 'practitioner', 'rating', 'created_at')



@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'practitioner', 'slot', 'status','payment_status','created_at')  # Fields to show in list view
    list_filter = ('status', 'practitioner')  # Add filtering options
    search_fields = ('patient__name', 'practitioner__name')  # Enable search
    ordering = ('-created_at',)  # Order by newest first
    
    

class ReplyAdmin(admin.ModelAdmin):
    # Define the fields to display in the list view
    list_display = ('get_content_object', 'review', 'message', 'created_at')
    
    # Add filtering options (e.g., by review or content type)
    list_filter = ('content_type', 'review', 'created_at')
    
    # Allow searching by review and message
    search_fields = ('message', 'review__feedback',)

    # Custom method to get the content object (Patient or Practitioner)
    def get_content_object(self, obj):
        return obj.content_object.__str__()  # This will return either Patient or Practitioner name
    
    get_content_object.admin_order_field = 'content_object'  # Allow sorting by content object
    get_content_object.short_description = 'Replied by'  # Label in the admin list

    # Optionally, allow only users who are staff or superuser to access
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

admin.site.register(Reply, ReplyAdmin)

