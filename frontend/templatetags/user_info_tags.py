from django import template
from user_account.models import Practitioner
from patientdashboard.models import Review

register = template.Library()

@register.simple_tag
def get_practitioner_name(request):
    """
    Returns the name of the logged-in practitioner.
    If no practitioner is logged in, it returns an empty string.
    """
    practitioner_name = request.session.get('practitioner_name', None)
    
    if practitioner_name:
        return practitioner_name
    return ''  # Return empty string if no practitioner is logged in





@register.simple_tag
def get_practitioner_image(request):
    """
    Returns the image URL of the logged-in practitioner based on their practitioner ID.
    If no practitioner ID is found, it returns a person icon SVG.
    """
    practitioner_id = request.session.get('practitioner_id', None)
    
    if practitioner_id:
        try:
            practitioner = Practitioner.objects.get(id=practitioner_id)
            if practitioner.photo:
                return practitioner.photo.url
            else:
                # Return an inline SVG person icon
                return '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                            <circle cx="12" cy="8" r="4" fill="#b0bec5"/>
                            <path d="M12 14c-4 0-6 2-6 4v2h12v-2c0-2-2-4-6-4z" fill="#b0bec5"/>
                          </svg>'''
        except Practitioner.DoesNotExist:
            return '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                        <circle cx="12" cy="8" r="4" fill="#b0bec5"/>
                        <path d="M12 14c-4 0-6 2-6 4v2h12v-2c0-2-2-4-6-4z" fill="#b0bec5"/>
                      </svg>'''
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <circle cx="12" cy="8" r="4" fill="#b0bec5"/>
                <path d="M12 14c-4 0-6 2-6 4v2h12v-2c0-2-2-4-6-4z" fill="#b0bec5"/>
              </svg>'''
              
              
              



@register.simple_tag
def get_patient_name(request):
    """
    Returns the name of the logged-in patient.
    If no patient is logged in, it returns an empty string.
    """
    patient_name = request.session.get('patient_name', None)
    
    if patient_name:
        return patient_name
    return ''  # Return empty string if no patient is logged in



@register.filter
def to(value):
    return range(value)





@register.simple_tag
def review_count_from_session(request):
    # Get practitioner_id from session
    practitioner_id = request.session.get('practitioner_id')

    if not practitioner_id:
        return 0  # Or handle as needed if the practitioner_id is not found in the session

    # Query the reviews for the practitioner and get the count
    total_reviews = Review.objects.filter(practitioner_id=practitioner_id).count()
    
    return total_reviews