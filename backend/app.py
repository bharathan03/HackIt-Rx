"""
app.py
Main Flask application that:
1. Receives file uploads + language selections from frontend
2. Uses openai_service to extract and translate text
3. Returns results as JSON
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import tempfile
import json
import os 
from openai_service import extract_text_from_image, translate_text

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Allow frontend (Next.js) to call this backend
CORS(app)

# In-memory storage for "sessions"
SESSIONS = {}

@app.route("/upload", methods=["POST"])
def upload_and_translate():
    """
    Handles image upload + translation.
    Steps:
    1. Receive image + languages from frontend
    2. Save image temporarily
    3. Extract text using OpenAI
    4. Translate text into selected languages
    5. Return result as JSON
    """

    # Check if image file is uploaded
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]

    # Get selected languages (sent as JSON string from frontend)
    languages = request.form.get("languages")
    if not languages:
        return jsonify({"error": "No languages provided"}), 400

    try:
        languages = json.loads(languages)  # Convert JSON string -> Python list
    except:
        return jsonify({"error": "Languages format invalid"}), 400 # For invalid language format

    # Save uploaded image to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name)
        tmp_path = tmp.name

    # Step 1: Extract text
    extracted_text = extract_text_from_image(tmp_path)

    # Step 2: Translate into each language
    translations = {}
    for lang in languages:
        translations[lang] = translate_text(extracted_text, lang)

    # Step 3: Send back JSON response
    return jsonify({
        "original_text": extracted_text,
        "translations": translations
    })

@app.route("/session/extract", methods=["POST"])
def session_extract():
    """
    Example endpoint for session-based extraction.
    Expects: { "session_id": "123", "languages": ["en", "fr"] }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    session_id = data.get("session_id")
    languages = data.get("languages", [])

    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    # Example: fetch stored medicines for session
    medicines = SESSIONS.get(session_id, [])

    # Translate medicine info
    for med in medicines:
        med["translations"] = {
            lang: {
                "medicine_name": translate_text(med["medicine_name"], lang),
                "dosage": translate_text(med["dosage"], lang)
            }
            for lang in languages
        }

    return jsonify({
        "session_id": session_id,
        "medicines": medicines
    })

@app.route("/image/<filename>", methods=["GET"])
def get_image(filename):
    """
    Returns an uploaded image by filename.
    """
    filepath = os.path.join("uploads", filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Image not found"}), 404
    return send_file(filepath, mimetype="image/jpeg")

if __name__ == "__main__":
    # Run Flask locally
    app.run(debug=True, port=5000)
