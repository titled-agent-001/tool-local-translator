"""
Language configuration and app settings.
Add new languages here — they'll automatically appear in the UI and translation engine.
"""

# Supported languages: code -> display name
# The code is used by the OCR and translation engines
LANGUAGES = {
    "auto": "Auto-Detect",
    "en": "English",
    "fr": "French",
    "de": "German",
    "zh-TW": "Chinese (Traditional)",
    "zh-CN": "Chinese (Simplified)",
    "ko": "Korean",
    "ja": "Japanese",
}

# Ollama configuration
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:7b"

# CJK font fallback for PDF/image overlay (bundled or system)
# Update these paths for your OS if needed
CJK_FONT_PATHS = [
    # macOS
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    # Linux
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    # Windows
    "C:/Windows/Fonts/msgothic.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]

LATIN_FONT_PATHS = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

# App settings
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
ALLOWED_PDF_EXTENSIONS = {"pdf"}
