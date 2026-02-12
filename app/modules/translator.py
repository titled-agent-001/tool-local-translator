"""Translation engine using deep-translator (Google Translate free backend)."""

import logging
from deep_translator import GoogleTranslator
from config import DEEP_TRANSLATOR_MAP

logger = logging.getLogger(__name__)


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source to target language.
    source_lang can be "auto" for auto-detection.
    """
    if not text or not text.strip():
        return text

    src = "auto" if source_lang == "auto" else DEEP_TRANSLATOR_MAP.get(source_lang, source_lang)
    tgt = DEEP_TRANSLATOR_MAP.get(target_lang, target_lang)

    try:
        translator = GoogleTranslator(source=src, target=tgt)
        # deep-translator has a 5000-char limit per call; chunk if needed
        chunks = _chunk_text(text, max_len=4500)
        translated_chunks = []
        for chunk in chunks:
            result = translator.translate(chunk)
            translated_chunks.append(result if result else chunk)
        return "".join(translated_chunks)
    except Exception as e:
        logger.error("Translation failed: %s", e)
        raise RuntimeError(f"Translation failed: {e}") from e


def _chunk_text(text: str, max_len: int = 4500) -> list[str]:
    """Split text into chunks respecting sentence boundaries where possible."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Try to split at last newline or period within limit
        split_at = max_len
        for sep in ["\n", ". ", "。", "！", "？"]:
            idx = text.rfind(sep, 0, max_len)
            if idx > max_len // 2:
                split_at = idx + len(sep)
                break
        chunks.append(text[:split_at])
        text = text[split_at:]
    return chunks
