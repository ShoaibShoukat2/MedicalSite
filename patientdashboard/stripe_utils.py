import stripe
from django.conf import settings
from django.urls import reverse
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, appointment):
    """
    Create a Stripe checkout session for an appointment
    
    Args:
        request: The HTTP request object
        appointment: The Appointment object to be paid for
        
    Returns:
        The Stripe checkout session ID
    """
    # Get the practitioner's price from the appointment
    # Get practitioner price, default to 50 if not set
    practitioner_price = appointment.practitioner.price or 50.00
    amount = int(practitioner_price * 100)  # Convert to cents
    
    success_url = request.build_absolute_uri(
        reverse('patientdashboard:payment_success')
    ) + f'?appointment_id={appointment.id}'
    
    cancel_url = request.build_absolute_uri(
        reverse('patientdashboard:payment_cancel')
    ) + f'?appointment_id={appointment.id}'
    
    # Create the Stripe checkout session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Appointment with {appointment.practitioner.first_name} {appointment.practitioner.last_name}',
                        'description': f'Appointment on {appointment.slot.start_time.strftime("%Y-%m-%d at %H:%M")}',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            },
        ],
        metadata={
            'appointment_id': appointment.id,
            'patient_id': appointment.patient.id,
            'practitioner_id': appointment.practitioner.id,
        },
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    
    return checkout_session.id

def handle_checkout_completed(event):
    """
    Handle the checkout.session.completed event from Stripe
    
    Args:
        event: The Stripe event object
    """
    from patientdashboard.models import Appointment
    
    session = event['data']['object']
    appointment_id = session.get('metadata', {}).get('appointment_id')
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.payment_status = 'Completed'
        appointment.save()
        
        # You could also send confirmation emails here
        
        return True
    except Appointment.DoesNotExist:
        return False