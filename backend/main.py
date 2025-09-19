from fastapi import FastAPI, UploadFile, File, Form
from services.openai_service import extract_text_from_image, translate_text
from services.ocr_fallback import fallback_ocr

app = FastAPI()

@app.get("/health")
def health_check():
    """
    Quick check to make sure the API is running.
    """
    return {"status": "ok"}

@app.post("/translate")
async def translate_prescription(
    file: UploadFile = File(...),
    lang1: str = Form(...),
    lang2: str = Form(None),
    lang3: str = Form(None)
):
    """
    1. Accepts an uploaded image file and target languages.
    2. Runs OCR with OpenAI (fallbacks to pytesseract if needed).
    3. Translates extracted text into up to 3 languages.
    """
    # Save file temporarily
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    # OCR step: try OpenAI first, fallback to pytesseract
    try:
        extracted_text = await extract_text_from_image(file_location)
    except Exception as e:
        print(f"⚠️ OpenAI OCR failed: {e}, using fallback...")
        extracted_text = fallback_ocr(file_location)

    # Translate text into chosen languages
    translations = []
    for lang in [lang1, lang2, lang3]:
        if lang:  # Skip empty
            translated = await translate_text(extracted_text, lang)
            translations.append({lang: translated})

    return {"original": extracted_text, "translations": translations}
