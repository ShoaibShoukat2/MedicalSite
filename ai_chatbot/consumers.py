import datetime
import json
import os
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from channels.db import database_sync_to_async
from user_account.models import Patient
from patientdashboard.models import Appointment
from practitionerdashboard.models import Prescription
import logging
from django.core import serializers
from django.db.models.fields.files import ImageFieldFile, FileField
from decimal import Decimal

# Disable TensorFlow warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Load OpenAI API Key
from dotenv import load_dotenv
load_dotenv()

# Try to import OpenAI, use fallback if not available
try:
    import openai
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        OPENAI_AVAILABLE = True
        print("OpenAI API key configured successfully in consumers.")
    else:
        OPENAI_AVAILABLE = False
        print("OpenAI API key not found in consumers. Using fallback responses only.")
except ImportError:
    print("OpenAI not installed. Using fallback responses only.")
    OPENAI_AVAILABLE = False
except Exception as e:
    print(f"OpenAI initialization error in consumers: {e}. Using fallback responses only.")
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles all Django-specific types"""
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (ImageFieldFile, FileField)):
            return obj.url if obj else None
        return super().default(obj)

class AIChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection."""
        await self.accept()
        print("=" * 80)
        print("✅ WebSocket connection established successfully!")
        print("=" * 80)
        logger.info("WebSocket connection established.")

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        print("=" * 80)
        print(f"🔌 WebSocket disconnected with code: {close_code}")
        print("=" * 80)
        logger.info(f"WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data):
        """Handles incoming messages and fetches responses."""
        try:
            print("\n" + "=" * 80)
            print("📨 NEW MESSAGE RECEIVED")
            print("=" * 80)
            
            data = json.loads(text_data)
            patient_id = data.get("patient_id")
            user_message = data.get("message", "").strip()
            
            print(f"👤 Patient ID: {patient_id}")
            print(f"💬 User Message: {user_message}")

            if not patient_id or not user_message:
                print("❌ ERROR: Invalid patient ID or empty message")
                await self.send_error("Invalid patient ID or empty message")
                return

            logger.info(f"Received message: {user_message} from patient {patient_id}")

            # Fetch patient records
            print("\n📋 Fetching patient data...")
            patient_data = await self.get_patient_data(patient_id)
            
            if patient_data:
                print(f"✅ Patient data fetched successfully")
                print(f"   - Appointments: {len(patient_data.get('appointments', []))}")
                print(f"   - Prescriptions: {len(patient_data.get('prescriptions', []))}")
            else:
                print("⚠️ No patient data found")

            # Generate AI response
            print("\n🤖 Generating AI response...")
            ai_response = await self.get_ai_response(user_message, patient_data)
            print(f"✅ AI Response Generated: {ai_response[:100]}...")

            # Send response back to client
            print("\n📤 Sending response to client...")
            await self.send(text_data=json.dumps({
                "message": ai_response,
                "status": "success"
            }, cls=EnhancedJSONEncoder))
            print("✅ Response sent successfully!")
            print("=" * 80 + "\n")

        except Exception as e:
            print("\n" + "=" * 80)
            print(f"❌ ERROR processing message: {str(e)}")
            print("=" * 80 + "\n")
            logger.error(f"Error processing message: {str(e)}")
            await self.send_error(str(e))

    async def send_error(self, error_message):
        """Send error response."""
        await self.send(text_data=json.dumps({
            "error": error_message,
            "status": "error"
        }, cls=EnhancedJSONEncoder))

    @database_sync_to_async
    def get_patient_data(self, patient_id):
        """Fetch patient data with complete type handling"""
        try:
            print(f"\n   🔍 Searching for patient ID: {patient_id}")
            patient = Patient.objects.get(id=patient_id)
            print(f"   ✅ Patient found: {patient.first_name} {patient.last_name}")
            
            # Convert model instances to dictionaries with proper type handling
            def model_to_dict(instance):
                from django.forms.models import model_to_dict
                data = model_to_dict(instance)
                # Handle special field types
                for field in instance._meta.fields:
                    if field.name in data:
                        value = getattr(instance, field.name)
                        if isinstance(value, (datetime.date, datetime.datetime)):
                            data[field.name] = value.isoformat()
                        elif isinstance(value, Decimal):
                            data[field.name] = float(value)
                        elif isinstance(value, (ImageFieldFile, FileField)):
                            data[field.name] = value.url if value else None
                return data
            
            # Get patient data
            patient_data = model_to_dict(patient)
            
            # Get related data
            print(f"   📅 Fetching appointments...")
            appointments = [
                model_to_dict(appt) 
                for appt in Appointment.objects.filter(patient=patient)
            ]
            print(f"   ✅ Found {len(appointments)} appointments")
            
            print(f"   💊 Fetching prescriptions...")
            prescriptions = [
                model_to_dict(pres) 
                for pres in Prescription.objects.filter(patient=patient)
            ]
            print(f"   ✅ Found {len(prescriptions)} prescriptions")
            
            # Structure the response
            structured_data = {
                "patient_info": patient_data,
                "appointments": appointments,
                "prescriptions": prescriptions
            }
            
            logger.info(f"Fetched patient data successfully")
            return structured_data

        except Patient.DoesNotExist:
            print(f"   ❌ ERROR: Patient ID {patient_id} not found in database")
            logger.error(f"Patient ID {patient_id} not found in database.")
            return None
        except Exception as e:
            print(f"   ❌ ERROR fetching patient data: {str(e)}")
            logger.error(f"Error fetching patient data: {str(e)}")
            return None

    async def get_ai_response(self, user_message, patient_data):
        """Generates AI response with proper JSON serialization"""
        try:
            if OPENAI_AVAILABLE:
                print(f"   🤖 Using OpenAI API for response generation")
                
                # Convert patient data to JSON string with our custom encoder
                patient_data_str = json.dumps(patient_data, cls=EnhancedJSONEncoder) if patient_data else "No medical history found."
                
                prompt = f"""You are an AI medical assistant. Here is the patient's medical history:
                {patient_data_str}
                
                User query: {user_message}
                Please provide a helpful response:"""
                
                print(f"   📝 Prompt created (length: {len(prompt)} chars)")
                logger.info(f"Sending request to OpenAI with prompt: {prompt[:500]}...")  # Log first 500 chars

                print(f"   ⏳ Sending request to OpenAI...")
                # Get AI response using old API format
                response = await sync_to_async(openai.ChatCompletion.create)(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )

                ai_reply = response.choices[0].message.content
                print(f"   ✅ OpenAI Response Received!")
                print(f"   💬 Response: {ai_reply[:150]}...")
                logger.info(f"AI Response Received: {ai_reply}")
                
                return ai_reply
            else:
                print(f"   ⚠️ OpenAI not available, using fallback response")
                # Use fallback response
                return self.get_fallback_response(user_message)

        except Exception as e:
            print(f"   ❌ ERROR in AI response generation: {str(e)}")
            print(f"   🔄 Falling back to predefined responses")
            logger.error(f"AI response error: {str(e)}")
            return self.get_fallback_response(user_message)
    
    def get_fallback_response(self, message):
        """Provide fallback responses for common medical questions"""
        print(f"   🔄 Using fallback response for: {message[:50]}...")
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['flu', 'fever', 'cold']):
            response = "For flu-like symptoms, rest, stay hydrated, and consider over-the-counter medications. If symptoms persist or worsen, please consult a healthcare provider."
            print(f"   ✅ Matched: Flu/Fever/Cold category")
        
        elif any(word in message_lower for word in ['headache', 'head', 'pain']):
            response = "Headaches can have various causes. Try rest, hydration, and over-the-counter pain relievers. If headaches are severe or frequent, please see a doctor."
            print(f"   ✅ Matched: Headache/Pain category")
        
        elif any(word in message_lower for word in ['appointment', 'book', 'schedule']):
            response = "To book an appointment, please log in to your patient dashboard or call our clinic directly. Our staff will help you find the right specialist and available time slots."
            print(f"   ✅ Matched: Appointment category")
        
        elif any(word in message_lower for word in ['emergency', 'urgent', 'serious']):
            response = "For medical emergencies, please call 911 immediately or visit your nearest emergency room. For urgent but non-emergency care, contact our clinic's urgent care line."
            print(f"   ✅ Matched: Emergency category")
        
        elif any(word in message_lower for word in ['specialist', 'doctor', 'physician']):
            response = "We have specialists in cardiology, dermatology, orthopedics, neurology, and many other fields. You can browse our doctors on the homepage or through your patient dashboard."
            print(f"   ✅ Matched: Specialist category")
        
        else:
            response = "Thank you for your question! For personalized medical advice, I recommend consulting with one of our healthcare professionals. You can book an appointment through our patient portal."
            print(f"   ✅ Using default response")
        
        return response

    def format_for_speech(self, text):
        """Format text to be more suitable for speech synthesis"""
        # Remove excess whitespace
        text = ' '.join(text.split())
        
        # Replace medical abbreviations that speech synthesis might mispronounce
        replacements = {
            "mg": "milligrams",
            "mcg": "micrograms",
            "ml": "milliliters",
            "BP": "blood pressure",
            "HR": "heart rate",
            "RR": "respiratory rate",
            "temp.": "temperature",
            "Dr.": "Doctor",
            "approx.": "approximately"
        }
        
        for abbr, full in replacements.items():
            text = text.replace(f" {abbr} ", f" {full} ")
            
        return text




