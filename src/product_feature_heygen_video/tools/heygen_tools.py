import os
import requests
import time
import json
import re
from crewai.tools import BaseTool

class HeyGenVideoTool(BaseTool):
    name: str = "HeyGen AI Video Generation Tool"
    description: str = "Takes a script, background video URL, avatar ID, and voice ID to generate a video using HeyGen API. It also positions the avatar."

    def _run(self, script: str, background_video_url: str, avatar_id: str = "avatar_id_placeholder", voice_id: str = "voice_id_placeholder") -> str:
        """HeyGen API ka istemal karke video generate karne ka core function."""
        api_key = "ZjliMDg1ZmE5NTEyNGIxYmFjYmExOWRiYjgzYWI2OGUtMTc1MDUzMDYyMQ=="
        
        # Validate background video URL
        if not background_video_url or not re.match(r'^https?://', background_video_url):
            return f"Error: Invalid background video URL: '{background_video_url}'. URL must start with http:// or https://"
            
        # Use default avatar and voice IDs if not provided
        if not avatar_id or avatar_id == "avatar_id_placeholder":
            avatar_id = "avatar-0qgz9jf0l6"  # Default HeyGen avatar
            
        if not voice_id or voice_id == "voice_id_placeholder":
            voice_id = "voice-1"  # Default HeyGen voice
        
        print(f"Using background video URL: {background_video_url}")
        print(f"Using avatar ID: {avatar_id}")
        print(f"Using voice ID: {voice_id}")
        
        headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json"
        }

        script_scenes = [scene.strip() for scene in script.split('[NEXT]')]
        
        video_inputs = []
        for text in script_scenes:
            if text:
                scene = {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "circle",
                        "scale": 0.35,
                        "x": 0.3,
                        "y": -0.4
                    },
                    "voice": {
                        "type": "text",
                        "input_text": text,
                        "voice_id": voice_id
                    },
                    "background": {
                        "type": "video",
                        "video_url": background_video_url,
                        "set_as_background": True
                    }
                }
                video_inputs.append(scene)

        payload = {
            "video_inputs": video_inputs,
            "dimension": { "width": 1080, "height": 1920 },
            "test": False,
            "title": "Automated CrewAI Video"
        }

        try:
            print("Sending request to HeyGen API...")
            gen_response = requests.post("https://api.heygen.com/v2/video/generate", headers=headers, data=json.dumps(payload))
            gen_response.raise_for_status()
            response_data = gen_response.json()
            
            if 'data' not in response_data or 'video_id' not in response_data.get('data', {}):
                error_msg = f"Error in API response format: {response_data}"
                print(error_msg)
                return error_msg
                
            video_id = response_data['data']['video_id']
            print(f"Video generation shuru ho gayi hai. Video ID: {video_id}")
        except requests.exceptions.RequestException as e:
            error_msg = f"Error while starting video generation: {e}"
            if 'gen_response' in locals() and hasattr(gen_response, 'text'):
                error_msg += f". Response: {gen_response.text}"
            print(error_msg)
            return error_msg

        status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
        
        max_retries = 10
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                status_response = requests.get(status_url, headers={"X-Api-Key": api_key})
                status_response.raise_for_status()
                status_data = status_response.json().get('data', {})
                
                if not status_data:
                    print("Warning: Empty status data received")
                    retry_count += 1
                    time.sleep(20)
                    continue
                
                print(f"Current video status: {status_data.get('status', 'unknown')}")
                
                if status_data.get('status') == 'completed':
                    print("Video safaltapoorvak generate ho gayi hai!")
                    return f"Video generation complete. You can view it here: {status_data.get('video_url', 'URL not available')}"
                elif status_data.get('status') in ['failed', 'error']:
                    error_message = f"Video generation failed. Error: {status_data.get('error', 'Unknown error')}"
                    print(error_message)
                    return error_message
                
                time.sleep(20)
            except requests.exceptions.RequestException as e:
                error_msg = f"Error while checking video status: {e}"
                print(error_msg)
                retry_count += 1
                time.sleep(30)
        
        return "Video generation timed out or failed after multiple retries. Please check HeyGen dashboard manually."
