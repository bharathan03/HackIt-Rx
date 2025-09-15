"""
app.py
Main Flask application that:
1. Receives file uploads + language selections from frontend
2. Uses openai_service to extract and translate text
3. Returns results as JSON
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import tempfile
import json
from openai_service import extract_text_from_image, translate_text

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Allow frontend (Next.js) to call this backend
CORS(app)

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

if __name__ == "__main__":
    # Run Flask locally
    app.run(debug=True, port=5000)
