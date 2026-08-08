import base64
import os
from io import BytesIO
import re

from dotenv import load_dotenv
from groq import Groq
from PIL import Image

load_dotenv()

def encode_image_for_groq(image_input):
    if isinstance(image_input, str):
        image = Image.open(image_input)
    else:
        image = image_input
        
    image.thumbnail((1024, 1024))
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=75)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def extract_frame_from_video(video_filepath):
    import cv2
    cap = cv2.VideoCapture(video_filepath)
    success, frame = cap.read()
    cap.release()
    if success:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)
    return None

def brain_of_the_doctor(patient_text, image_filepath=None, video_filepath=None):
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("Missing GROQ_API_KEY in .env or environment")

    image_to_encode = None
    if image_filepath:
        image_to_encode = image_filepath
    elif video_filepath:
        image_to_encode = extract_frame_from_video(video_filepath)
        if not image_to_encode:
            raise ValueError("Failed to extract a frame from the provided video.")
    else:
        raise ValueError("Groq vision requires an image or video. Please upload a skin image or video.")

    image_data = encode_image_for_groq(image_to_encode)

    prompt = (
        "You are a confident, natural doctor specializing in skin care. Speak with the reassurance, clarity, and authority of a real doctor. "
        "Limit your entire response to two or three sentences maximum. "
        "Do not use any special characters, symbols, asterisks, or markdown formatting in your response because it will be converted directly to audio.\n\n"
        f"Patient text: {patient_text}"
    )

    if video_filepath and not image_filepath:
        prompt += "\nThe patient uploaded a video. I have extracted a frame from it for you to review as the visual reference."
    elif video_filepath and image_filepath:
        prompt += "\nThe patient also uploaded a video, but use the provided image as the visual reference."

    client = Groq(api_key=groq_api_key)
    response = client.chat.completions.create(
        model=os.environ.get("GROQ_MODEL", "qwen/qwen3.6-27b"),
        max_completion_tokens=2000,
        messages=[
            {
                "role": "system",
                "content": "You are a careful skin care assistant. Give general information, not a diagnosis.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}",
                        },
                    },
                ],
            },
        ],
    )

    content = response.choices[0].message.content
    
    # Remove <think>...</think> blocks from the reasoning model (even if cut off)
    content = re.sub(r'<think>.*?(?:</think>|$)', '', content, flags=re.DOTALL).strip()
    return content
