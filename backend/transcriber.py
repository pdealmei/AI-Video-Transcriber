import ssl
import certifi

ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where()
)


from faster_whisper import WhisperModel
import os

class Transcriber:
    def __init__(self, whisper_model: str = "base.en"):
        self.model = WhisperModel(whisper_model, 
            device = "auto", 
            compute_type="int8"
        )

    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio to text."""
        segments, info = self.model.transcribe(
            audio_path, beam_size=5, language="en", condition_on_previous_text=False
        )
        text = " ".join([segment.text for segment in segments]).strip()
        return text