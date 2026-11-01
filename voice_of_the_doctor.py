import os
import tempfile
from pathlib import Path
from deepgram import DeepgramClient
from dotenv import load_dotenv

load_dotenv()

def convert_text_to_doctor_audio(text: str) -> str:
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    deepgram = DeepgramClient(api_key=api_key)
    
    # Deepgram limits text to 2000 characters per request
    text = text[:1999]
    
    audio = deepgram.speak.v1.audio.generate(
        text=text,
        model="aura-asteria-en",
        encoding="mp3",
    )
    
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    for chunk in audio:
        temp_audio.write(chunk)
    temp_audio.close()
            
    return temp_audio.name