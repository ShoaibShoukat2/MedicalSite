from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from user_account.models import Patient, Practitioner
from django.contrib import messages
from django.db.models import Q
import random
import string
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_protect
from langdetect import detect
from django.views.decorators.csrf import csrf_exempt
import json, time, requests, base64
from django.http import JsonResponse


# Create your views here.



from django.shortcuts import render

def index(request):
    query = request.GET.get('q', '')
    
    if query:
        # Search in multiple fields: first_name, last_name, specialty, doctor_type
        practitioners = Practitioner.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(specialty__icontains=query) |
            Q(doctor_type__icontains=query)
        ).distinct()
    else:
        # Show first 3 practitioners when no search query
        practitioners = Practitioner.objects.all()[:3]
        
    context = {
        'practitioners': practitioners,
        'query': query,
    }
    return render(request, 'temp_index.html', context)








def generate_otp():
    """Generate a random OTP of 6 digits."""
    otp = ''.join(random.choices(string.digits, k=6))
    return otp

    



@csrf_protect
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
        
        # Validate email deliverability
        from .email_utils import validate_email_deliverability, send_otp_email
        
        is_valid, validation_error = validate_email_deliverability(email)
        if not is_valid:
            context['error_message'] = validation_error
            return render(request, 'Patient.html', context)
        
        try:
            # Send OTP email with enhanced deliverability
            success, error_message = send_otp_email(
                recipient_email=email,
                otp=otp,
                user_name=f"{first_name} {last_name}",
                user_type="patient"
            )
            
            if not success:
                context['error_message'] = f"Failed to send OTP: {error_message}"
                return render(request, 'Patient.html', context)
            
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












@csrf_protect
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



@csrf_protect
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
        
        # Validate email deliverability
        from .email_utils import validate_email_deliverability, send_otp_email
        
        is_valid, validation_error = validate_email_deliverability(email)
        if not is_valid:
            messages.error(request, validation_error)
            return redirect('frontend:practitioner_signup')
        
        try:
            # Send OTP email with enhanced deliverability
            success, error_message = send_otp_email(
                recipient_email=email,
                otp=otp,
                user_name=f"{first_name} {last_name}",
                user_type="practitioner"
            )
            
            if not success:
                messages.error(request, f"Failed to send OTP: {error_message}")
                return redirect('frontend:practitioner_signup')

            # Save OTP and practitioner data in session for later verification
            request.session['otp'] = otp
            request.session['practitioner_data'] = {
                'civility': civility,
                'first_name': first_name,
                'last_name': last_name,
                'doctor_type': doctor_type,
                'specialty': specialty,
                'email': email,
                'password': password,  # Hash the password before saving
                'terms_accepted': terms_accepted
            }

            messages.info(request, "An OTP has been sent to your email. Please verify it to complete the registration.")
            return redirect('frontend:practitioner_verify_otp')  # Redirect to OTP verification page
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



@csrf_protect
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
        return redirect('frontend:practitioner_verify_otp')

    return render(request, 'verify_practitioner_otp.html')  # Render OTP verification form




@csrf_protect
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
            return redirect('patient_dashboard:appointments_patients')  # Redirect to a dashboard or home page
        else:
            context['error'] = "Invalid email or password."
            return render(request, 'PatientLogin.html', context)

    return render(request, 'PatientLogin.html', context)







@csrf_protect
def practitioner_login(request):
    error_message = None
    success_message = None

    if request.method == 'POST': 
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(f"Login attempt - Email: {email}")  # Debug print

        try:
            practitioner = Practitioner.objects.get(email=email)
            print(f"Practitioner found: {practitioner.first_name} {practitioner.last_name}")  # Debug print
            
            # Print the first few characters of the stored hash
            print(f"Stored password hash preview: {practitioner.password[:20]}...")  
            
            password_valid = check_password(password, practitioner.password)
            print(f"Password check result: {password_valid}")  # Debug print
            
            if password_valid:
                request.session['practitioner_id'] = practitioner.id
                request.session['practitioner_name'] = practitioner.first_name
                print("Login successful, redirecting...")  # Debug print
                return redirect('practitioner_dashboard:dashboard')


            else:
                error_message = 'Invalid password.'
                print("Invalid password")  # Debug print
        except Practitioner.DoesNotExist:
            error_message = 'Email not found.'
            print(f"No practitioner found with email: {email}")  # Debug print
        except Exception as e:
            error_message = 'An error occurred.'
            print(f"Unexpected error: {str(e)}")  # Debug print

    return render(request, 'PractiLogin.html', {
        'error_message': error_message,
        'success_message': success_message
    })





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

            patient.password = make_password(new_password)
            patient.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect("frontend:patient_login")
        except Patient.DoesNotExist:
            messages.error(request, "Invalid or expired reset token.")
    return render(request, "reset_password.html", {"token": token})







def temp_index(request):
    

    
    return render(request,'temp_index.html')


import json
# import openai
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from openai import OpenAI
import base64
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# interview

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DID_API_KEY = os.getenv("DID_API_KEY")



# Create OpenAI client
# client = OpenAI(api_key=OPENAI_API_KEY)

# Clean OpenAI output
def clean_text(text):
    return re.sub(r'[^\x00-\x7F]+', '', text).strip()


import time 




@csrf_exempt
def ask_avatar(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"error": "Only POST method allowed"}, status=405)
            
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return JsonResponse({"error": "Please enter a message"}, status=400)
            
        if len(user_message) > 500:
            return JsonResponse({"error": "Message too long. Please keep it under 500 characters."}, status=400)

        # 🌐 Detect the language
        try:
            detected_lang = detect(user_message)
        except:
            detected_lang = "en"  # Default to English if detection fails

        # 🧠 Enhanced system prompt for medical assistant
        system_prompts = {
            "en": "You are a friendly AI medical assistant. Provide helpful, accurate health information while being warm and conversational. Keep responses under 150 words. Always remind users to consult healthcare professionals for serious concerns.",
            "ur": "آپ ایک دوستانہ AI طبی معاون ہیں۔ مفید اور درست صحت کی معلومات فراہم کریں۔ جوابات 150 الفاظ سے کم رکھیں۔ سنگین مسائل کے لیے ہمیشہ ڈاکٹر سے رجوع کرنے کی یاد دہانی کرائیں۔",
            "hi": "आप एक मित्रवत AI चिकित्सा सहायक हैं। सहायक और सटीक स्वास्थ्य जानकारी प्रदान करें। उत्तर 150 शब्दों से कम रखें। गंभीर समस्याओं के लिए हमेशा डॉक्टर से सलाह लेने की याद दिलाएं।"
        }
        
        system_prompt = system_prompts.get(detected_lang, system_prompts["en"])

        # 🌍 Enhanced voice mapping with better quality voices
        voice_map = {
            "en": "en-US-JennyNeural",  # More natural female voice
            "fr": "fr-FR-DeniseNeural",
            "de": "de-DE-KatjaNeural", 
            "es": "es-ES-ElviraNeural",
            "it": "it-IT-ElsaNeural",
            "ur": "ur-PK-AsadNeural",
            "hi": "hi-IN-SwaraNeural",
            "ar": "ar-SA-ZariyahNeural"
        }
        voice_id = voice_map.get(detected_lang, "en-US-JennyNeural")

        # 🔮 OpenAI GPT response with better error handling
        try:
            # openai_response = client.chat.completions.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "system", "content": system_prompt},
            #         {"role": "user", "content": user_message}
            #     ],
            #     max_tokens=200,
            #     temperature=0.7
            # )
            # raw_answer = openai_response.choices[0].message.content.strip()
            # answer = raw_answer[:400] if raw_answer else "I'm here to help with your health questions!"
            
            # Fallback response for now
            answer = "I'm your AI medical assistant. How can I help you with your health questions today?"
            
        except Exception as openai_error:
            print(f"OpenAI Error: {openai_error}")
            # Fallback response
            answer = "I'm your AI medical assistant. How can I help you with your health questions today?"

        # 🎙️ Enhanced D-ID API call with better error handling
        try:
            encoded_auth = base64.b64encode(DID_API_KEY.encode()).decode()
            headers = {
                "Authorization": f"Basic {encoded_auth}",
                "Content-Type": "application/json"
            }

            payload = {
                "script": {
                    "type": "text",
                    "provider": {
                        "type": "microsoft",
                        "voice_id": voice_id
                    },
                    "ssml": False,
                    "input": answer
                },
                "source_url": "https://res.cloudinary.com/dovwzsl4v/image/upload/v1752823658/avatar_zfdfcr.jpg",
                "config": {
                    "fluent": True,
                    "pad_audio": 0.0
                }
            }

            response = requests.post("https://api.d-id.com/talks", json=payload, headers=headers, timeout=30)
            
            if response.status_code != 201:
                print(f"D-ID API Error: {response.status_code} - {response.text}")
                return JsonResponse({"error": "Avatar service temporarily unavailable", "answer": answer}, status=200)
                
            parsed_json = response.json()
            talk_id = parsed_json.get("id")
            
            if not talk_id:
                return JsonResponse({"error": "Failed to create avatar video", "answer": answer}, status=200)
                
            poll_url = f"https://api.d-id.com/talks/{talk_id}"

            # Poll for completion with timeout
            max_attempts = 15
            for attempt in range(max_attempts):
                try:
                    poll_response = requests.get(poll_url, headers=headers, timeout=10)
                    poll_data = poll_response.json()
                    
                    status = poll_data.get("status")
                    if status == "done":
                        video_url = poll_data.get("result_url")
                        if video_url:
                            return JsonResponse({"video_url": video_url, "answer": answer})
                    elif status == "error":
                        print(f"D-ID processing error: {poll_data}")
                        break
                        
                    time.sleep(2)  # Wait 2 seconds between polls
                    
                except requests.RequestException as poll_error:
                    print(f"Polling error: {poll_error}")
                    break

            # If video generation fails, return text response
            return JsonResponse({"answer": answer, "error": "Video generation took too long, but here's the text response"}, status=200)
            
        except requests.RequestException as did_error:
            print(f"D-ID Request Error: {did_error}")
            return JsonResponse({"answer": answer, "error": "Avatar service unavailable, showing text response"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        print(f"Unexpected error in ask_avatar: {str(e)}")
        return JsonResponse({"error": "Something went wrong. Please try again.", "exception": str(e)}, status=500)


    



def login(request):
    return render(request, 'login.html')

