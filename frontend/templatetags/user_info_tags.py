from django import template

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
def get_patient_name(request):
    """
    Returns the name of the logged-in patient.
    If no patient is logged in, it returns an empty string.
    """
    patient_name = request.session.get('patient_name', None)
    
    if patient_name:
        return patient_name
    return ''  # Return empty string if no patient is logged in



