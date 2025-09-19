import os
from openai import OpenAI

# Load API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------- OCR WITH OPENAI ----------
async def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from an image using OpenAI's Vision model.
    """
    with open(file_path, "rb") as image_file:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Vision-capable model
            messages=[
                {"role": "system", "content": "You are an OCR assistant. Extract prescription text from the image."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Extract the text clearly from this prescription image."},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + image_file.read().decode("latin1")}}
                ]}
            ],
            max_tokens=500
        )
    return response.choices[0].message.content


# ---------- TRANSLATION WITH OPENAI ----------
async def translate_text(text: str, target_language: str) -> str:
    """
    Translate given text into the target language using OpenAI.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Translate this medical prescription into {target_language}."},
            {"role": "user", "content": text}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content
