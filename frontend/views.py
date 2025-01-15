from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from user_account.models import Patient, Practitioner
from django.contrib import messages
import random
import string
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings

# Create your views here.


def index(request):
    return render(request, 'index.html')






def generate_otp():
    """Generate a random OTP of 6 digits."""
    otp = ''.join(random.choices(string.digits, k=6))
    return otp



def appointment(request):
    return render(request, 'appointment.html')




def patient_signup(request):
    context = {
        'greeting_choices': Patient.GREETING_CHOICES,
        'gender_choices': Patient.GENDER_CHOICES,
        'error_message': None,
        'success_message': None,
    }

    if request.method == 'POST':
        greeting = request.POST.get('greeting')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        mobile_phone = request.POST.get('mobile_phone')
        date_of_birth = request.POST.get('date_of_birth')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Form validation
        if not all([greeting, first_name, last_name, gender, mobile_phone, date_of_birth, email, password]):
            context['error_message'] = "All fields are required."
            return render(request, 'Patient.html', context)

        if Patient.objects.filter(email=email).exists():
            context['error_message'] = "This email is already registered."
            return render(request, 'Patient.html', context)

        # Generate OTP
        otp = generate_otp()
        try:
            send_mail(
                'Your OTP for Email Verification',
                f'Your OTP for email verification is {otp}.',
                'no-reply@yourdomain.com',
                [email],
                fail_silently=False,
            )
            # Hash password and save session data
            hashed_password = make_password(password)
            request.session['otp'] = otp
            request.session['patient_data'] = {
                'greeting': greeting,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'mobile_phone': mobile_phone,
                'date_of_birth': date_of_birth,
                'email': email,
                'password': hashed_password,
            }
            context['success_message'] = "An OTP has been sent to your email. Please verify it to complete the registration."
            return redirect('frontend:patient_verify_otp')  
        except Exception as e:
            context['error_message'] = f"Error sending OTP: {str(e)}"
            return render(request, 'Patient.html', context)

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
                    password=patient_data['password']  
                )
                patient.save()
                
                request.session.flush()
                messages.success(request, "Patient signed up successfully!")
                return redirect('frontend:success')  
            except Exception as e:
                messages.error(request, f"An error occurred while saving the data: {str(e)}")
                return redirect('frontend:patient_signup')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('frontend:patient_verify_otp')


    return render(request, 'verify_otp.html')  


# eeryone for thiscode cna make






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
        terms_accepted = request.POST.get('terms') == 'on'  

        # Check if the email already exists in the database
        if Practitioner.objects.filter(email=email).exists():
            messages.error(request, "The email address is already in use. Please use a different one.")
            return redirect('frontend:practitioner_signup')

        # Validate password strength
        if len(password) < 8 or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password) or not any(char in "!@#$%^&*()-_+={}[]|\\:;'<>?,./" for char in password):
            messages.error(request, "Password must meet the required strength criteria.")
            return redirect('frontend:practitioner_signup')

        # Check if terms are accepted
        if not terms_accepted:
            messages.error(request, "You must accept the terms and conditions.")
            return redirect('frontend:practitioner_signup')

        # Generate OTP and send it to the provided email
        otp = generate_otp()
        try:
            
            
            send_mail(
                'Your OTP for Email Verification',
                f'Your OTP for email verification is {otp}.',
                'no-reply@yourdomain.com',
                [email],
                fail_silently=False,
            )

            # Save OTP and practitioner data in session for later verification
            request.session['otp'] = otp
            request.session['practitioner_data'] = {
                'civility': civility,
                'first_name': first_name,
                'last_name': last_name,
                'doctor_type': doctor_type,
                'specialty': specialty,
                'email': email,
                'password': make_password(password),  # Hash the password before saving
                'terms_accepted': terms_accepted
            }

            messages.info(request, "An OTP has been sent to your email. Please verify it to complete the registration.")
            return redirect('frontend:practinor_verify_otp')  # Redirect to OTP verification page
        except Exception as e:
            messages.error(request, f"Error sending OTP: {str(e)}")
            return redirect('frontend:practitioner_signup')

    # GET request handling (render the form with dropdown choices)
    context = {
        'doctor_types': Practitioner.DOCTOR_TYPE_CHOICES,
        'specialties': Practitioner.SPECIALTY_CHOICES,
        'civilities': Practitioner.CIVILITY_CHOICES,
    }
    return render(request, 'practitioner.html', context)


def practitioner_verify_otp(request):
    """Verify OTP for practitioner signup."""
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        # If OTP matches, create the practitioner record
        practitioner_data = request.session.get('practitioner_data')
        try:
            # Hash the password before saving
            hashed_password = make_password(practitioner_data['password'])
            practitioner = Practitioner.objects.create(
                civility=practitioner_data['civility'],
                first_name=practitioner_data['first_name'],
                last_name=practitioner_data['last_name'],
                doctor_type=practitioner_data['doctor_type'],
                specialty=practitioner_data['specialty'],
                email=practitioner_data['email'],
                password=hashed_password,
            )
            practitioner.save()

            # Clear session data after successful registration
            request.session.flush()
            messages.success(request, "Practitioner signed up successfully!")
            return redirect('frontend:success')  # Redirect to success page
        except Exception as e:
            messages.error(request, f"An error occurred while saving the data: {str(e)}")
            return redirect('frontend:practitioner_signup')

        messages.error(request, "Invalid OTP. Please try again.")
        return redirect('frontend:practinor_verify_otp')

    return render(request, 'verify_practitioner_otp.html')  # Render OTP verification form




def patient_login(request):
    context = {}
    if request.method == 'POST':
        # Retrieve email and password from the login form
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Validate input fields
        if not email or not password:
            context['error'] = "Email and Password are required."
            return render(request, 'PatientLogin.html', context)

        # Check if a patient with the given email exists
        try:
            patient = Patient.objects.get(email=email)
        except Patient.DoesNotExist:
            context['error'] = "Invalid email or password."
            return render(request, 'PatientLogin.html', context)

        # Verify the password
        if check_password(password, patient.password):  # Use Django's `check_password` to validate
            # Mark the user as logged in (consider using Django's authentication system for better security)
            request.session['patient_id'] = patient.id
            request.session['patient_name'] = patient.first_name
            context['success'] = f"Welcome back, {patient.first_name}!"
            return redirect('frontend:index')  # Redirect to a dashboard or home page
        else:
            context['error'] = "Invalid email or password."
            return render(request, 'PatientLogin.html', context)

    return render(request, 'PatientLogin.html', context)













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
                request.session['practitioner_name'] = practitioner.first_name
                
                
                
                messages.success(request, 'Login successful.')
                return redirect('frontend:index')  # Redirect to a dashboard or home page
            else:
                messages.error(request, 'Invalid password.')
        except Practitioner.DoesNotExist:
            messages.error(request, 'Email not found.')

    return render(request, 'PractiLogin.html')




def practitioner_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            # Verify email exists in the database
            Practitioner.objects.get(email=email)

            # Generate a reset link with the email as a query parameter
            reset_link = request.build_absolute_uri(
                reverse('frontend:practitioner_reset_password') + f"?email={email}"
            )

            # Send the reset link via email
            send_mail(
                'Password Reset Request',
                f'Click the link below to reset your password:\n\n{reset_link}',
                'your_email@example.com',
                [email],
                fail_silently=False,
            )

            messages.success(request, 'A password reset link has been sent to your email.')
        except Practitioner.DoesNotExist:
            messages.error(request, 'Email not found.')

    return render(request, 'Pract_ForgotPassword.html')






def practitioner_reset_password(request):
    email = request.GET.get('email')

    if not email:
        messages.error(request, 'Invalid or missing email.')
        return redirect('frontend:practitioner_forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')

        try:
            practitioner = Practitioner.objects.get(email=email)
            practitioner.password = make_password(new_password)
            practitioner.save()

            messages.success(request, 'Your password has been reset successfully.')
            return redirect('frontend:practitioner_login')
        except Practitioner.DoesNotExist:
            messages.error(request, 'Email not found.')

    return render(request, 'Pract_ResetPassword.html', {'email': email})







def logout(request):
    request.session.flush()


    return redirect('frontend:index')  









def success(request):
    return render(request, 'success.html')






# Step 1: Forgot Password View
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            patient = Patient.objects.get(email=email)
            # Generate a reset token (e.g., temporary random password or a secure token)
            reset_token = get_random_string(20)
            patient.password = reset_token  # Save the token temporarily as the password
            patient.save()

            # Send the token to the user's email
            reset_link = request.build_absolute_uri(
                reverse("frontend:reset_password", kwargs={"token": reset_token})
            )
            send_mail(
                subject="Password Reset",
                message=f"Click the link to reset your password: {reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            messages.success(
                request, "A password reset link has been sent to your email."
            )
            return redirect("frontend:forgot_password")
        except Patient.DoesNotExist:
            messages.error(request, "No account found with that email address.")
    return render(request, "forgot_password.html")


# Step 2: Reset Password View
def reset_password(request, token):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        try:
            # Find the user with the given token
            patient = get_object_or_404(Patient, password=token)
            # Update the password securely (hash it)
            from django.contrib.auth.hashers import make_password

            patient.password = make_password(new_password)
            patient.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect("frontend:patient_login")
        except Patient.DoesNotExist:
            messages.error(request, "Invalid or expired reset token.")
    return render(request, "reset_password.html", {"token": token})








def temp_index(request):
    
    
    
    return render(request,'temp_index.html')

















def login(request):
    return render(request, 'login.html')


