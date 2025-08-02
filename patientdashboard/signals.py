from django.dispatch import receiver
from social_django.signals import social_auth_authenticated
from .models import Patient


@receiver(social_auth_authenticated)
def google_patient_login_handler(sender, request, user, **kwargs):
    email = user.email

    try:
        patient = Patient.objects.get(email=email)
        # Store login in session (same as patient_login())
        request.session['patient_id'] = patient.id
        request.session['patient_name'] = patient.first_name
        print(f"✅ Patient login via Google: {patient.first_name}")
    except Patient.DoesNotExist:
        print(f"❌ Patient with email {email} not found.")


