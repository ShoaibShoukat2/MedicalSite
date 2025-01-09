from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from user_account.models import Patient, Practitioner
from django.contrib import messages
import random
import string
from django.core.mail import send_mail

# Create your views here.


def index(request):
    return render(request, 'index.html')





def generate_otp():
    """Generate a random OTP of 6 digits."""
    otp = ''.join(random.choices(string.digits, k=6))
    return otp




def patient_signup(request):
    if request.method == 'POST':
        # Retrieve form data from the POST request
        greeting = request.POST.get('greeting')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        mobile_phone = request.POST.get('mobile_phone')
        date_of_birth = request.POST.get('date_of_birth')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Perform form validation
        if not greeting or not first_name or not last_name or not gender or not mobile_phone or not date_of_birth or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect('frontend:patient_signup')

        # Check if the email is already registered
        if Patient.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect('frontend:patient_signup')

        # Generate OTP and send it to the provided email
        otp = generate_otp()
        # You can use Django's send_mail function or any email service
        try:
            send_mail(
                'Your OTP for Email Verification',
                f'Your OTP for email verification is {otp}.',
                'no-reply@yourdomain.com',
                [email],
                fail_silently=False,
            )
            # Save OTP in the session to verify later
            request.session['otp'] = otp
            request.session['patient_data'] = {
                'greeting': greeting,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'mobile_phone': mobile_phone,
                'date_of_birth': date_of_birth,
                'email': email,
                'password': password,
            }
            messages.info(request, "An OTP has been sent to your email. Please verify it to complete the registration.")
            return redirect('frontend:patient_verify_otp')  # Redirect to OTP verification page
        except Exception as e:
            messages.error(request, f"Error sending OTP: {str(e)}")
            return redirect('frontend:patient_signup')

    # Pass the choices to the template context for the form
    context = {
        'greeting_choices': Patient.GREETING_CHOICES,
        'gender_choices': Patient.GENDER_CHOICES,
    }
    return render(request, 'Patient.html', context)





def verify_otp(request):
    """Verify OTP entered by the user."""
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')

        if entered_otp == stored_otp:
            # If OTP is correct, create the patient record
            patient_data = request.session.get('patient_data')
            try:
                patient = Patient.objects.create(
                    greeting=patient_data['greeting'],
                    first_name=patient_data['first_name'],
                    last_name=patient_data['last_name'],
                    gender=patient_data['gender'],
                    mobile_phone=patient_data['mobile_phone'],
                    date_of_birth=patient_data['date_of_birth'],
                    email=patient_data['email'],
                    password=patient_data['password']  # Consider hashing the password before saving
                )
                patient.save()
                messages.success(request, "Patient signed up successfully!")
                return redirect('frontend:success')  # Redirect after successful registration
            except Exception as e:
                messages.error(request, f"An error occurred while saving the data: {str(e)}")
                return redirect('patient_signup')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('patient_verify_otp')

    return render(request, 'verify_otp.html')  # Render OTP verification form





def practitioner_signup(request):
    if request.method == 'POST':
        # Retrieve data from the form
        civility = request.POST.get('civility')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        doctor_type = request.POST.get('doctor_type')
        specialty = request.POST.get('specialty')
        email = request.POST.get('email')
        password = request.POST.get('password')
        terms_accepted = request.POST.get('terms') == 'on'  # Checkbox for terms acceptance
        
        
        
         # Check if the email already exists in the database
        if Practitioner.objects.filter(email=email).exists():
            messages.error(request, "The email address is already in use. Please use a different one.")
            return render(request, 'practitioner.html', {'civilities': Practitioner.CIVILITY_CHOICES, 'doctor_types': Practitioner.DOCTOR_TYPE_CHOICES, 'specialties': Practitioner.SPECIALTY_CHOICES})
        
        # Validate password strength here (using custom validation or built-in Django validators)
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'practitioner.html', {'civilities': Practitioner.CIVILITY_CHOICES, 'doctor_types': Practitioner.DOCTOR_TYPE_CHOICES, 'specialties': Practitioner.SPECIALTY_CHOICES})
        
        if not any(char.isupper() for char in password):
            messages.error(request, "Password must contain at least one uppercase letter.")
            return render(request, 'practitioner.html', {'civilities': Practitioner.CIVILITY_CHOICES, 'doctor_types': Practitioner.DOCTOR_TYPE_CHOICES, 'specialties': Practitioner.SPECIALTY_CHOICES})
        
        if not any(char.isdigit() for char in password):
            messages.error(request, "Password must contain at least one number.")
            return render(request, 'practitioner.html', {'civilities': Practitioner.CIVILITY_CHOICES, 'doctor_types': Practitioner.DOCTOR_TYPE_CHOICES, 'specialties': Practitioner.SPECIALTY_CHOICES})
        
        if not any(char in "!@#$%^&*()-_+={}[]|\:;'<>?,./" for char in password):
            messages.error(request, "Password must contain at least one special character.")
            return render(request, 'practitioner.html', {'civilities': Practitioner.CIVILITY_CHOICES, 'doctor_types': Practitioner.DOCTOR_TYPE_CHOICES, 'specialties': Practitioner.SPECIALTY_CHOICES})

        # Check if terms are accepted
        if not terms_accepted:
            messages.error(request, "You must accept the terms and conditions.")
            return render(request, 'practitioner.html', {'civilities': Practitioner.CIVILITY_CHOICES, 'doctor_types': Practitioner.DOCTOR_TYPE_CHOICES, 'specialties': Practitioner.SPECIALTY_CHOICES})

        # Hash the password before saving
        hashed_password = make_password(password)

        # Save practitioner details to the database
        practitioner = Practitioner(
            civility=civility,
            first_name=first_name,
            last_name=last_name,
            doctor_type=doctor_type,
            specialty=specialty,
            email=email,
            password=hashed_password,
            terms_accepted=terms_accepted
        )
        practitioner.save()

        # Success message and redirect (or render a success page)
        messages.success(request, "Account created successfully!")
        return redirect('frontend:success')  # Redirect to the login page or any other page
    
    # GET request handling (render the form with dropdown choices)
    context = {
        'doctor_types': Practitioner.DOCTOR_TYPE_CHOICES,
        'specialties': Practitioner.SPECIALTY_CHOICES,
        'civilities': Practitioner.CIVILITY_CHOICES,
    }
    return render(request, 'practitioner.html', context)







def patient_login(request):
    if request.method == 'POST':
        # Retrieve email and password from the login form
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validate input fields
        if not email or not password:
            messages.error(request, "Email and Password are required.")
            return redirect('frontend:patient_login')

        # Check if a patient with the given email exists
        try:
            patient = Patient.objects.get(email=email)
        except Patient.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('frontend:patient_login')

        # Verify the password
        if patient.password == password:  # Ensure you hash the password during signup and use proper comparison
            # Mark the user as logged in (you can replace this with Django's authentication system)
            request.session['patient_id'] = patient.id
            messages.success(request, f"Welcome back, {patient.first_name}!")
            return redirect('dashboard')  # Redirect to a dashboard or home page
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('frontend:patient_login')

    return render(request, 'PatientLogin.html')











def practitioner_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Fetch the practitioner record with the given email
            practitioner = Practitioner.objects.get(email=email)
            
            # Compare the password using Django's check_password
            if check_password(password, practitioner.password):
                # Save practitioner info in session or redirect to dashboard
                request.session['practitioner_id'] = practitioner.id
                messages.success(request, 'Login successful.')
                return redirect('dashboard')  # Replace with the practitioner's dashboard URL
            else:
                messages.error(request, 'Invalid password.')
        except Practitioner.DoesNotExist:
            messages.error(request, 'Email not found.')

    return render(request, 'PractiLogin.html')








    
    





def success(request):
    return render(request, 'success.html')



















def login(request):
    return render(request, 'login.html')


