"""Translation engine using Ollama local LLM."""

import json
import logging
import requests
from config import OLLAMA_URL, OLLAMA_MODEL, LANGUAGES

logger = logging.getLogger(__name__)

# Language name lookup for prompts
LANG_NAMES = {
    "en": "English", "fr": "French", "de": "German",
    "zh-TW": "Traditional Chinese", "zh-CN": "Simplified Chinese",
    "ko": "Korean", "ja": "Japanese",
}


def _ollama_generate(prompt: str, timeout: int = 120) -> str:
    """Call Ollama generate API and return the response text."""
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 8192},
    }
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama. Please ensure Ollama is running "
            "(run 'ollama serve' or start it from Applications)."
        )
    except requests.Timeout:
        raise RuntimeError("Ollama translation timed out. Try with shorter text.")
    except Exception as e:
        raise RuntimeError(f"Ollama API error: {e}")


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text from source to target language using Ollama."""
    if not text or not text.strip():
        return text

    src_name = LANG_NAMES.get(source_lang, source_lang)
    tgt_name = LANG_NAMES.get(target_lang, target_lang)

    chunks = _chunk_text(text, max_len=3000)
    translated_chunks = []

    for chunk in chunks:
        if source_lang == "auto":
            prompt = (
                f"Translate the following text to {tgt_name}. "
                f"Auto-detect the source language.\n\n"
            )
        else:
            prompt = f"Translate the following text from {src_name} to {tgt_name}.\n\n"

        prompt += (
            "RULES:\n"
            "- Return ONLY the translated text, no explanations or notes\n"
            "- Preserve all numbers, dates, monetary amounts, and formatting exactly\n"
            "- Preserve financial terminology accurately (e.g. revenue, EBITDA, net income, 營收, 淨利)\n"
            "- Preserve paragraph breaks and structure\n"
            "- Do NOT add quotes around the translation\n\n"
            f"Text to translate:\n{chunk}"
        )

        result = _ollama_generate(prompt)
        translated_chunks.append(result if result else chunk)

    return "\n".join(translated_chunks) if len(chunks) > 1 else translated_chunks[0]


def check_ollama_status() -> dict:
    """Check if Ollama is running and the model is available."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        model_ready = any(OLLAMA_MODEL in m for m in models)
        return {"running": True, "model_ready": model_ready, "model": OLLAMA_MODEL, "models": models}
    except Exception:
        return {"running": False, "model_ready": False, "model": OLLAMA_MODEL}


def _chunk_text(text: str, max_len: int = 3000) -> list[str]:
    """Split text into chunks respecting sentence boundaries where possible."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        split_at = max_len
        for sep in ["\n\n", "\n", ". ", "。", "！", "？"]:
            idx = text.rfind(sep, 0, max_len)
            if idx > max_len // 2:
                split_at = idx + len(sep)
                break
        chunks.append(text[:split_at])
        text = text[split_at:]
    return chunks
