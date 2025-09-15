"""
openai_service.py
This file handles all communication with OpenAI API.
It has two main functions:
1. extract_text_from_image(image_path) -> str
2. translate_text(text, target_language) -> str
"""

import base64
from openai import OpenAI

# Create OpenAI client (reads API key from .env automatically)
client = OpenAI()

def extract_text_from_image(image_path: str) -> str:
    """
    Reads an image (prescription photo) and extracts text using OpenAI's Vision model.
    - image_path: path to uploaded image file
    - returns: extracted text as a string
    """
    # Convert image to base64 so it can be sent to OpenAI
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Ask GPT-4o-mini to "read" the prescription
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # vision + text model
        messages=[
            {"role": "system", "content": "You are a medical prescription reader."},
            {"role": "user", "content": [
                {"type": "text", "text": "Extract the medication instructions from this prescription:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]}
        ],
        max_tokens=500
    )

    # Return only the text portion
    return response.choices[0].message.content.strip()

def translate_text(text: str, target_language: str) -> str:
    """
    Translates given text into the target language using GPT.
    - text: extracted prescription text
    - target_language: e.g., "Chinese", "Malay", "Tamil"
    - returns: translated text
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Translate the following prescription into {target_language}."},
            {"role": "user", "content": text}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()