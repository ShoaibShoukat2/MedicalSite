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
from openai import OpenAI
import logging
from django.core import serializers
from django.db.models.fields.files import ImageFieldFile, FileField
from decimal import Decimal

# Disable TensorFlow warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Load OpenAI API Key
from dotenv import load_dotenv
load_dotenv()

# Get API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

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
        logger.info("WebSocket connection established.")

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        logger.info(f"WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data):
        """Handles incoming messages and fetches responses."""
        try:
            data = json.loads(text_data)
            patient_id = data.get("patient_id")
            user_message = data.get("message", "").strip()

            if not patient_id or not user_message:
                await self.send_error("Invalid patient ID or empty message")
                return

            logger.info(f"Received message: {user_message} from patient {patient_id}")

            # Fetch patient records
            patient_data = await self.get_patient_data(patient_id)

            # Generate AI response
            ai_response = await self.get_ai_response(user_message, patient_data)

            # Send response back to client
            await self.send(text_data=json.dumps({
                "message": ai_response,
                "status": "success"
            }, cls=EnhancedJSONEncoder))

        except Exception as e:
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
            patient = Patient.objects.get(id=patient_id)
            
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
            appointments = [
                model_to_dict(appt) 
                for appt in Appointment.objects.filter(patient=patient)
            ]
            
            prescriptions = [
                model_to_dict(pres) 
                for pres in Prescription.objects.filter(patient=patient)
            ]
            
            # Structure the response
            structured_data = {
                "patient_info": patient_data,
                "appointments": appointments,
                "prescriptions": prescriptions
            }
            
            logger.info(f"Fetched patient data successfully")
            return structured_data

        except Patient.DoesNotExist:
            logger.error(f"Patient ID {patient_id} not found in database.")
            return None
        except Exception as e:
            logger.error(f"Error fetching patient data: {str(e)}")
            return None

    async def get_ai_response(self, user_message, patient_data):
        """Generates AI response with proper JSON serialization"""
        try:
            # Convert patient data to JSON string with our custom encoder
            patient_data_str = json.dumps(patient_data, cls=EnhancedJSONEncoder) if patient_data else "No medical history found."
            
            prompt = f"""You are an AI medical assistant. Here is the patient's medical history:
            {patient_data_str}
            
            User query: {user_message}
            Please provide a helpful response:"""
            
            logger.info(f"Sending request to OpenAI with prompt: {prompt[:500]}...")  # Log first 500 chars

            # Get AI response
            response = await sync_to_async(client.chat.completions.create)(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150,
                temperature=0.7
            )

            ai_reply = response.choices[0].message.content
            logger.info(f"AI Response Received: {ai_reply}")
            
            return ai_reply

        except Exception as e:
            logger.error(f"OpenAI error: {str(e)}")
            return "I'm currently unable to process your request. Please try again later."
    
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




