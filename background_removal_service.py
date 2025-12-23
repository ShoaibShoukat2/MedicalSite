import requests
import subprocess
import os
from django.conf import settings

class BackgroundRemovalService:
    def __init__(self):
        self.unscreen_api_key = getattr(settings, 'UNSCREEN_API_KEY', None)
    
    def remove_background_ffmpeg(self, input_video_path, output_path):
        """Remove background using FFmpeg chromakey (for solid backgrounds)"""
        try:
            cmd = [
                'ffmpeg', '-i', input_video_path,
                '-vf', 'chromakey=white:0.3:0.1,format=yuva420p',
                '-c:v', 'libvpx-vp9',
                '-pix_fmt', 'yuva420p',
                '-b:v', '1M',
                '-auto-alt-ref', '0',
                '-an',  # Remove audio
                '-y',   # Overwrite output
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return output_path
            else:
                print(f"FFmpeg Error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Background removal error: {e}")
            return None
    
    def remove_background_unscreen(self, video_url):
        """Remove background using Unscreen API"""
        if not self.unscreen_api_key:
            print("Unscreen API key not configured")
            return None
        
        try:
            # Download video first
            response = requests.get(video_url)
            temp_input = "/tmp/input_video.mp4"
            
            with open(temp_input, 'wb') as f:
                f.write(response.content)
            
            # Upload to Unscreen
            with open(temp_input, 'rb') as f:
                files = {'source': f}
                headers = {'Authorization': f'Bearer {self.unscreen_api_key}'}
                
                response = requests.post(
                    'https://api.unscreen.com/v1.0/videos',
                    files=files,
                    headers=headers
                )
            
            if response.status_code == 200:
                result_url = response.json()['url']
                return result_url
            else:
                print(f"Unscreen API Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"Unscreen error: {e}")
            return None
    
    def process_did_video(self, video_url, output_filename):
        """Complete pipeline: download D-ID video and remove background"""
        try:
            # Download D-ID video
            response = requests.get(video_url)
            temp_input = f"/tmp/{output_filename}_input.mp4"
            
            with open(temp_input, 'wb') as f:
                f.write(response.content)
            
            # Remove background
            output_path = f"media/avatars/{output_filename}.webm"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            result = self.remove_background_ffmpeg(temp_input, output_path)
            
            # Cleanup
            if os.path.exists(temp_input):
                os.remove(temp_input)
            
            return result
            
        except Exception as e:
            print(f"Video processing error: {e}")
            return None

# Singleton instance
bg_removal_service = BackgroundRemovalService()