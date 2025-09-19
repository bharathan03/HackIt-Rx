import pytesseract
from PIL import Image

def fallback_ocr(file_path: str) -> str:
    """
    Extract text from an image using pytesseract (local OCR).
    Used if OpenAI OCR fails.
    """
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text
