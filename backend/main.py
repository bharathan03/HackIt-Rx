from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse,Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, tempfile, json


from services.openai_service import extract_text_from_image, translate_text
from services.ocr_fallback import fallback_ocr

app = FastAPI()

# Allow frontend (Vercel) and local dev
origins = [
    "https://hack-it-rx-front-end.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # frontend URL(s) whitelist origins
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, etc.
    allow_headers=["*"],            # Content-Type, Authorization, etc.
)

# ----- catch-all OPTIONS to ensure preflight is handled in serverless envs -----
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return Response(status_code=200, headers={
        "Access-Control-Allow-Origin": ", ".join(origins),
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, DELETE",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Allow-Credentials": "true",
    })

@app.get("/")
def read_root():
    return {"status": "ok"}

# In-memory storage for sessions
SESSIONS = {}

# ---------------------------
# MODELS
# ---------------------------
class SessionExtractRequest(BaseModel):
    session_id: str
    languages: list[str]

# ---------------------------
# ROUTES
# ---------------------------

@app.post("/upload")
async def upload_and_translate(image: UploadFile = File(...), languages: str = Form(...)):
    """
    Handles image upload + translation.
    1. Receive image + languages
    2. Extract text
    3. Translate into target languages
    """
    try:
        langs = json.loads(languages)  # stringified JSON → Python list
    except:
        return JSONResponse({"error": "Languages format invalid"}, status_code=400)

    # Save uploaded image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(await image.read())
        tmp_path = tmp.name

    # OCR step
    try:
        extracted_text = extract_text_from_image(tmp_path)
    except Exception as e:
        print(f"⚠️ OpenAI OCR failed: {e}, using fallback...")
        extracted_text = fallback_ocr(tmp_path)

    # Translate
    translations = {}
    for lang in langs:
        translations[lang] = translate_text(extracted_text, lang)

    return {"original_text": extracted_text, "translations": translations}


@app.post("/session/extract")
async def session_extract(req: SessionExtractRequest):
    """
    Example endpoint for session-based extraction.
    Expects: { "session_id": "123", "languages": ["en", "fr"] }
    """
    session_id = req.session_id
    languages = req.languages

    medicines = SESSIONS.get(session_id, [])

    # Translate each medicine
    for med in medicines:
        med["translations"] = {
            lang: {
                "medicine_name": translate_text(med["medicine_name"], lang),
                "dosage": translate_text(med["dosage"], lang),
            }
            for lang in languages
        }

    return {"session_id": session_id, "medicines": medicines}


@app.get("/image/{filename}")
async def get_image(filename: str):
    """
    Returns an uploaded image by filename.
    """
    filepath = os.path.join("uploads", filename)
    if not os.path.exists(filepath):
        return JSONResponse({"error": "Image not found"}, status_code=404)
    return FileResponse(filepath, media_type="image/jpeg")


@app.get("/health")
async def health_check():
    """
    Quick check to make sure the API is running.
    """
    return {"status": "ok"}


@app.post("/translate")
async def translate_prescription(
    file: UploadFile = File(...),
    lang1: str = Form(...),
    lang2: str = Form(None),
    lang3: str = Form(None),
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

    # OCR step
    try:
        extracted_text = extract_text_from_image(file_location)
    except Exception as e:
        print(f"⚠️ OpenAI OCR failed: {e}, using fallback...")
        extracted_text = fallback_ocr(file_location)

    # Translate
    translations = []
    for lang in [lang1, lang2, lang3]:
        if lang:
            translated = translate_text(extracted_text, lang)
            translations.append({lang: translated})

    return {"original": extracted_text, "translations": translations}
