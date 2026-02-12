"""OCR module using EasyOCR for text extraction from images."""

import logging
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

# Lazy-loaded reader cache
_readers: dict = {}


def _get_reader(lang_codes: list[str]):
    """Get or create an EasyOCR reader for given languages."""
    import easyocr
    key = tuple(sorted(lang_codes))
    if key not in _readers:
        logger.info("Initializing EasyOCR reader for languages: %s", lang_codes)
        _readers[key] = easyocr.Reader(lang_codes, gpu=False)
    return _readers[key]


# EasyOCR language code mapping
EASYOCR_LANG_MAP = {
    "en": "en",
    "fr": "fr",
    "de": "de",
    "zh-TW": "ch_tra",
    "zh-CN": "ch_sim",
    "ko": "ko",
    "ja": "ja",
}


def extract_text_from_image(image_path: str, source_lang: str = "auto") -> list[dict]:
    """
    Extract text regions from an image.
    Returns list of dicts: {text, bbox, confidence}
    bbox is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    """
    if source_lang == "auto":
        lang_codes = ["en"]  # Default; EasyOCR auto-detects within supported set
    else:
        code = EASYOCR_LANG_MAP.get(source_lang, "en")
        # EasyOCR often needs 'en' alongside CJK languages
        lang_codes = [code] if code == "en" else [code, "en"]

    try:
        reader = _get_reader(lang_codes)
        results = reader.readtext(image_path)
        regions = []
        for bbox, text, confidence in results:
            regions.append({
                "text": text,
                "bbox": bbox,  # list of 4 [x,y] points
                "confidence": float(confidence),
            })
        return regions
    except Exception as e:
        logger.error("OCR failed: %s", e)
        raise RuntimeError(f"OCR failed: {e}") from e
