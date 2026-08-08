import os
from pathlib import Path
from deepgram import DeepgramClient
from dotenv import load_dotenv

load_dotenv()

def convert_text_to_doctor_audio(text: str) -> str:
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    deepgram = DeepgramClient(api_key=api_key)
    
    # We pass the dictionary containing text if needed by SDK, but we use user's params here
    options = {
        "model": "aura-asteria-en",
        "encoding": "mp3",
    }
    
    # Deepgram limits text to 2000 characters per request
    text = text[:1999]
    
    audio = deepgram.speak.v1.audio.generate(
        text=text,
        model="aura-asteria-en",
        encoding="mp3",
    )
    
    audio_path = Path(__file__).parent / "doctor_response.mp3"
    with audio_path.open("wb") as file:
        for chunk in audio:
            file.write(chunk)
            
    return str(audio_path)