import ssl
import certifi

ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where()
)

import subprocess
import whisper
import os

def extract_audio(video_path: str, audio_path: str = "temp_audio.wav") -> str:
    """Extract audio from a video file."""
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    command = [
        "ffmpeg",
        "-i", video_path,
        "-q:a", "0",
        "-map", "a",
        audio_path,
        "-y"
    ]
    try:
        subprocess.run(command, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL, 
                        check=True)
        return audio_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def transcribe_audio(audio_path: str, model_size: str = "base") -> str:
    """Transcribe audio to text."""
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result["text"]