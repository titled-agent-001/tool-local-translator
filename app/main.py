"""Flask application — API routes for translation."""

import os
import sys
import uuid
import logging
from flask import Flask, request, jsonify, send_file, render_template

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    LANGUAGES, UPLOAD_FOLDER, OUTPUT_FOLDER,
    MAX_CONTENT_LENGTH, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_PDF_EXTENSIONS,
)
from app.modules.translator import translate_text, check_ollama_status
from app.modules.image_handler import translate_image
from app.modules.pdf_handler import translate_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Ensure directories exist
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)


def _allowed_file(filename: str, allowed: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ollama-status", methods=["GET"])
def api_ollama_status():
    """Check Ollama connection and model status."""
    return jsonify(check_ollama_status())


@app.route("/api/languages", methods=["GET"])
def get_languages():
    """Return the supported language list."""
    return jsonify({
        "languages": {k: v for k, v in LANGUAGES.items()},
        "source_languages": LANGUAGES,  # includes "auto"
        "target_languages": {k: v for k, v in LANGUAGES.items() if k != "auto"},
    })


@app.route("/api/translate/text", methods=["POST"])
def api_translate_text():
    """Translate plain text."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    text = data.get("text", "")
    source = data.get("source_lang", "auto")
    target = data.get("target_lang", "")

    if not text.strip():
        return jsonify({"error": "No text provided"}), 400
    if not target or target == "auto":
        return jsonify({"error": "Please select a target language"}), 400

    try:
        result = translate_text(text, source, target)
        return jsonify({"translated_text": result, "source_lang": source, "target_lang": target})
    except Exception as e:
        logger.error("Text translation error: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/translate/file", methods=["POST"])
def api_translate_file():
    """Translate an uploaded image or PDF."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    source = request.form.get("source_lang", "auto")
    target = request.form.get("target_lang", "")

    if not target or target == "auto":
        return jsonify({"error": "Please select a target language"}), 400
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
    uid = uuid.uuid4().hex[:12]

    if ext in ALLOWED_IMAGE_EXTENSIONS:
        mode = "image"
    elif ext in ALLOWED_PDF_EXTENSIONS:
        mode = "pdf"
    else:
        return jsonify({"error": f"Unsupported file type: .{ext}"}), 400

    # Save upload
    input_filename = f"{uid}_input.{ext}"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    file.save(input_path)

    try:
        if mode == "image":
            out_ext = "png" if ext == "png" else "jpg"
            output_filename = f"{uid}_translated.{out_ext}"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            translate_image(input_path, source, target, output_path)
        else:
            output_filename = f"{uid}_translated.pdf"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            translate_pdf(input_path, source, target, output_path)

        return jsonify({
            "download_url": f"/api/download/{output_filename}",
            "filename": output_filename,
            "mode": mode,
        })
    except Exception as e:
        logger.error("File translation error: %s", e)
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up input
        try:
            os.remove(input_path)
        except OSError:
            pass


@app.route("/api/download/<filename>")
def download_file(filename):
    """Download a translated file."""
    path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404
    return send_file(path, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
