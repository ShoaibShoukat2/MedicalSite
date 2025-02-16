import json
import os
import cv2
import numpy as np
import subprocess
import mediapipe as mp
from pydub import AudioSegment
from gtts import gTTS
from openai import OpenAI
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from django.conf import settings
from user_account.models import Patient
from patientdashboard.models import Appointment
from practitionerdashboard.models import Prescription

import json
import os
import cv2
import numpy as np
import subprocess
import mediapipe as mp
from pydub import AudioSegment
from gtts import gTTS
from openai import OpenAI
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from django.conf import settings
import json
import os
import cv2
import numpy as np
import subprocess
import mediapipe as mp
from pydub import AudioSegment
from gtts import gTTS
from openai import OpenAI
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from django.conf import settings
from dotenv import load_dotenv
load_dotenv()

class EnhancedLipSyncAvatar:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        self.MOUTH_LANDMARKS = [
            61, 62, 63, 64, 65, 66, 67,
            291, 292, 293, 294, 295, 296, 297,
            78, 95, 88, 178, 87, 14,
            324, 308, 318, 402, 317, 14,
        ]

    def animate_avatar(self, image_path, audio_path):
        """Generate an enhanced animated talking avatar with realistic lip-sync."""
        try:
            # Load and process image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Failed to load avatar image")

            height, width = image.shape[:2]
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Process with face mesh
            results = self.face_mesh.process(rgb_image)
            if not results.multi_face_landmarks:
                raise ValueError("No face detected in the avatar image")

            # Process audio
            audio = AudioSegment.from_file(audio_path)
            audio_array = np.array(audio.get_array_of_samples())

            # Calculate frame-related data
            duration = len(audio) / 1000  # Convert to seconds
            fps = 30
            frame_count = int(duration * fps)
            samples_per_frame = len(audio_array) // frame_count

            # Setup video writer
            output_path = os.path.join(settings.MEDIA_ROOT, f"avatar_{now().timestamp()}.mp4")
            out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

            # Extract face landmarks
            landmarks = results.multi_face_landmarks[0].landmark
            base_mouth_points = np.array([
                [landmarks[idx].x * width, landmarks[idx].y * height]
                for idx in self.MOUTH_LANDMARKS
            ])

            # Generate animation frames
            for frame_idx in range(frame_count):
                frame = image.copy()

                # Calculate audio amplitude for current frame
                start_sample = frame_idx * samples_per_frame
                end_sample = min(start_sample + samples_per_frame, len(audio_array))
                if start_sample < len(audio_array):
                    current_samples = audio_array[start_sample:end_sample]
                    amplitude = np.mean(np.abs(current_samples)) / 32767.0  # Normalize
                else:
                    amplitude = 0

                # Apply mouth movement
                mouth_movement = amplitude * 15
                current_mouth_points = base_mouth_points.copy()
                lower_lip_indices = range(len(self.MOUTH_LANDMARKS) // 2, len(self.MOUTH_LANDMARKS))
                for i in lower_lip_indices:
                    current_mouth_points[i][1] += mouth_movement

                # Draw mouth only (without lines)
                mouth_region = current_mouth_points.astype(np.int32)
                cv2.fillPoly(frame, [mouth_region], (255, 200, 200))

                # Remove purple lines from frame
                frame = self.remove_purple_lines(frame)

                out.write(frame)

            out.release()

            # Merge audio and video
            return self.sync_audio_with_video(output_path, audio_path)

        except Exception as e:
            print(f"Animation error: {str(e)}")
            return None

    def remove_purple_lines(self, frame):
        """Detect and remove purple lines from the frame using OpenCV."""
        try:
            # Convert frame to HSV for better color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Define HSV range for detecting purple lines
            lower_purple = np.array([120, 50, 50])
            upper_purple = np.array([160, 255, 255])

            # Create a mask to detect purple areas
            mask = cv2.inRange(hsv, lower_purple, upper_purple)

            # Inpaint (remove) the detected purple lines
            cleaned_frame = cv2.inpaint(frame, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

            return cleaned_frame
        except Exception as e:
            print(f"Error removing purple lines: {str(e)}")
            return frame

    def sync_audio_with_video(self, video_path, audio_path):
        """Merge video and audio using FFmpeg with enhanced settings."""
        try:
            output_path = video_path.replace(".mp4", "_final.mp4")
            command = [
                "ffmpeg",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-y",
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)

            # Clean up temporary video file
            if os.path.exists(video_path):
                os.remove(video_path)

            return output_path
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            return None

# Initialize OpenAI client
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
class AIChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.avatar = EnhancedLipSyncAvatar()
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            patient_id = data.get("patient_id")
            user_message = data.get("message", "")

            if not patient_id or not user_message.strip():
                raise ValueError("Invalid patient ID or empty message")

            # Generate AI response
            bot_reply = await self.get_ai_response(user_message)
            
            # Generate speech and avatar animation
            audio_file = await sync_to_async(self.text_to_speech)(bot_reply)
            if not audio_file:
                raise RuntimeError("Failed to generate speech audio")
                
            avatar_video = await sync_to_async(self.avatar.animate_avatar)(
                os.path.join(settings.MEDIA_ROOT, "avatar.jpg"),
                audio_file
            )
            if not avatar_video:
                raise RuntimeError("Failed to generate avatar animation")

            # Send response
            await self.send(text_data=json.dumps({
                "message": bot_reply,
                "audio_url": self.get_media_url(audio_file),
                "avatar_video": self.get_media_url(avatar_video),
                "status": "success"
            }))

        except Exception as e:
            await self.send(text_data=json.dumps({
                "error": str(e),
                "status": "error"
            }))

    def text_to_speech(self, text):
        """Generate enhanced text-to-speech audio."""
        try:
            output_path = os.path.join(
                settings.MEDIA_ROOT,
                f"speech_{now().timestamp()}.mp3"
            )
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(output_path)
            return output_path
        except Exception as e:
            print(f"TTS error: {str(e)}")
            return None

    def get_media_url(self, file_path):
        """Convert file path to media URL."""
        if not file_path:
            return None
        relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
        return f"{settings.MEDIA_URL.rstrip('/')}/{relative_path}"

    async def get_ai_response(self, user_message):
        """Generate AI response using OpenAI."""
        try:
            response = await sync_to_async(self.client.chat.completions.create)(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful AI medical assistant."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {str(e)}")
            return "I apologize, but I am unable to process your request at the moment."

