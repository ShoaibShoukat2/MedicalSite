import requests
import time
import os
from django.conf import settings

class DIDAvatarService:
    def __init__(self):
        self.api_key = getattr(settings, 'DID_API_KEY', 'your-did-api-key')
        self.base_url = "https://api.d-id.com"
        self.avatar_image = "https://res.cloudinary.com/dovwzsl4v/image/upload/v1752823658/avatar_zfdfcr.jpg"
    
    def create_talk(self, text, voice_id="en-US-JennyNeural"):
        """Create a talking video with D-ID API"""
        url = f"{self.base_url}/talks"
        
        payload = {
            "source_url": self.avatar_image,
            "script": {
                "type": "text",
                "input": text,
                "provider": {
                    "type": "microsoft",
                    "voice_id": voice_id
                }
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.0
            }
        }
        
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["id"]
        except Exception as e:
            print(f"D-ID API Error: {e}")
            return None
    
    def get_talk_result(self, talk_id):
        """Poll for talk completion and get result URL"""
        url = f"{self.base_url}/talks/{talk_id}"
        headers = {"Authorization": f"Basic {self.api_key}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "done":
                return data["result_url"]
            elif data["status"] == "error":
                print(f"D-ID Error: {data.get('error', 'Unknown error')}")
                return None
            else:
                return "processing"  # Still processing
                
        except Exception as e:
            print(f"D-ID Poll Error: {e}")
            return None
    
    def wait_for_completion(self, talk_id, max_wait=60):
        """Wait for talk to complete with polling"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            result = self.get_talk_result(talk_id)
            
            if result and result != "processing":
                return result
            
            time.sleep(2)  # Poll every 2 seconds
        
        return None  # Timeout
    
    def generate_avatar_video(self, text):
        """Complete flow: create talk and wait for result"""
        print(f"Generating avatar video for: {text[:50]}...")
        
        # Step 1: Create talk
        talk_id = self.create_talk(text)
        if not talk_id:
            return None
        
        print(f"Talk created with ID: {talk_id}")
        
        # Step 2: Wait for completion
        video_url = self.wait_for_completion(talk_id)
        
        if video_url:
            print(f"Video generated: {video_url}")
            return {
                "talk_id": talk_id,
                "video_url": video_url,
                "status": "completed"
            }
        else:
            return {
                "talk_id": talk_id,
                "status": "failed"
            }

# Singleton instance
did_service = DIDAvatarService()