import os
from openai import OpenAI


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


# ---------- OCR WITH OPENAI ----------
async def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from an image using OpenAI's Vision model.
    Returns mock text if no API key is set.
    """
    client = get_client()
    if client is None:
        # Mock response for local testing
        return "MOCKED_OCR_RESULT: Take 1 tablet daily after meals."

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
    Returns mock translation if no API key is set.
    """
    client = get_client()
    if client is None:
        # Mock translation for testing
        return f"[MOCKED_TRANSLATION to {target_language}]: {text}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Translate this medical prescription into {target_language}."},
            {"role": "user", "content": text}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content
