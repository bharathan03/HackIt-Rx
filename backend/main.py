from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import tempfile, json

load_dotenv()


from services.openai_service import extract_text_from_image, translate_text

app = FastAPI()

# Allow frontend (Vercel) and local dev
origins = [
    "https://hack-it-rx-front-end.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://hack-it-rx-front-end.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, etc.
    allow_headers=["*"],            # Content-Type, Authorization, etc.
)


@app.get("/")
def read_root():
    return {"status": "ok"}


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
        extracted_text = await extract_text_from_image(tmp_path)
    except Exception as e:
        return JSONResponse({"error": f"OCR failed: {str(e)}"}, status_code=500)

    # Translate
    translations = {}
    for lang in langs:
        translations[lang] = await translate_text(extracted_text, lang)

    return {"original_text": extracted_text, "translations": translations}
