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
from django.core.serializers.json import DjangoJSONEncoder

# Disable TensorFlow warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Load OpenAI API Key
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Use the API key
print(f"Your API Key: {OPENAI_API_KEY}")  # For testing purposes only (remove in production)
client = OpenAI(api_key=OPENAI_API_KEY)

logger = logging.getLogger(__name__)

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

            # Log user message
            logger.info(f"Received message: {user_message} from patient {patient_id}")

            # Fetch patient records
            patient_data = await self.get_patient_data(patient_id)

            # Generate AI response
            ai_response = await self.get_ai_response(user_message, patient_data)

            # Send response back to client
            await self.send(text_data=json.dumps({
                "message": ai_response,
                "status": "success"
            }))

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send_error(str(e))

    async def send_error(self, error_message):
        """Send error response."""
        await self.send(text_data=json.dumps({
            "error": error_message,
            "status": "error"
        }))


    @database_sync_to_async
    def get_patient_data(self, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
            appointments = list(Appointment.objects.filter(patient=patient).values())
            prescriptions = list(Prescription.objects.filter(patient=patient).values())

        # Convert datetime fields to string
            def format_datetime(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, (datetime.date, datetime.datetime)):
                            obj[key] = value.isoformat()
                return obj

            appointments = [format_datetime(a) for a in appointments]
            prescriptions = [format_datetime(p) for p in prescriptions]

            patient_data = {
            "patient_info": {
                "name": patient.first_name,
                "gender": patient.gender,
            },
            "appointments": appointments,
            "prescriptions": prescriptions,
        }

            logger.info(f"Fetched patient data: {patient_data}")
            return patient_data

        except Patient.DoesNotExist:
            logger.error(f"Patient ID {patient_id} not found in database.")
            return None


    async def get_ai_response(self, user_message, patient_data):
        """Generates AI response using OpenAI while incorporating patient history."""
        try:
            # Construct prompt using patient history
            prompt = "You are an AI medical assistant. Here is the patient's medical history and past appointments:\n\n"
            prompt += json.dumps(patient_data, indent=2) if patient_data else "No medical history found."

            prompt += f"\n\nUser query: {user_message}\nAI Response:"

            # Log AI request
            logger.info(f"Sending request to OpenAI with prompt: {prompt}")

            # Get AI response
            response = await sync_to_async(client.chat.completions.create)(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150
            )

            ai_reply = response.choices[0].message.content
            logger.info(f"AI Response Received: {ai_reply}")
            
            return ai_reply

        except Exception as e:
            logger.error(f"OpenAI error: {str(e)}")
            return "I am currently unable to process your request."
