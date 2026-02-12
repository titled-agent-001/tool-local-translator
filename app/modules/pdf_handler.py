"""PDF text extraction and translated PDF reconstruction using PyMuPDF."""

import logging
import os
import fitz  # PyMuPDF
from config import CJK_FONT_PATHS, LATIN_FONT_PATHS
from app.modules.translator import translate_text

logger = logging.getLogger(__name__)


def _find_font(paths: list[str]) -> str | None:
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def _is_cjk_target(target_lang: str) -> bool:
    return target_lang in ("zh-TW", "zh-CN", "ja", "ko")


def translate_pdf(input_path: str, source_lang: str, target_lang: str, output_path: str) -> str:
    """
    Translate a PDF: extract text blocks, translate them, rebuild the PDF
    preserving layout (position, font size, color).
    Returns the output file path.
    """
    doc = fitz.open(input_path)
    
    # Determine font to use
    if _is_cjk_target(target_lang):
        font_path = _find_font(CJK_FONT_PATHS)
        fontname = "cjk-font"
    else:
        font_path = _find_font(LATIN_FONT_PATHS)
        fontname = "latin-font"

    total_pages = len(doc)
    
    for page_num in range(total_pages):
        page = doc[page_num]
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        
        # Collect text spans with their properties
        edits = []
        for block in blocks:
            if block.get("type") != 0:  # text block
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    edits.append({
                        "bbox": fitz.Rect(span["bbox"]),
                        "text": text,
                        "size": span.get("size", 11),
                        "color": span.get("color", 0),
                        "origin": fitz.Point(span["origin"]) if "origin" in span else None,
                    })

        if not edits:
            continue

        # Batch translate all text on this page
        original_texts = [e["text"] for e in edits]
        combined = "\n|||DELIM|||\n".join(original_texts)
        
        try:
            translated_combined = translate_text(combined, source_lang, target_lang)
            translated_texts = translated_combined.split("\n|||DELIM|||\n")
            # Pad if split produced fewer items
            while len(translated_texts) < len(original_texts):
                translated_texts.append(original_texts[len(translated_texts)])
        except Exception as e:
            logger.warning("Page %d translation failed, keeping original: %s", page_num + 1, e)
            translated_texts = original_texts

        # Redact original text and insert translations
        for edit, translated in zip(edits, translated_texts):
            rect = edit["bbox"]
            # White-out the original text area
            page.draw_rect(rect, color=None, fill=(1, 1, 1))
            
            # Insert translated text
            fontsize = edit["size"]
            # Shrink font if translated text is longer to fit in same box
            text_width = fitz.get_text_length(translated, fontsize=fontsize)
            rect_width = rect.width
            if text_width > rect_width and rect_width > 0:
                fontsize = fontsize * rect_width / text_width
                fontsize = max(fontsize, 5)  # minimum readable size

            insertion_point = edit["origin"] if edit["origin"] else rect.tl + fitz.Point(0, fontsize)
            
            try:
                # Convert int color to RGB tuple
                c = edit["color"]
                if isinstance(c, int):
                    r = ((c >> 16) & 0xFF) / 255.0
                    g = ((c >> 8) & 0xFF) / 255.0
                    b = (c & 0xFF) / 255.0
                    color = (r, g, b)
                else:
                    color = (0, 0, 0)

                tw = fitz.TextWriter(page.rect)
                if font_path:
                    font = fitz.Font(fontfile=font_path)
                else:
                    font = fitz.Font("helv")
                
                tw.append(insertion_point, translated, font=font, fontsize=fontsize)
                tw.write_text(page, color=color)
            except Exception as e:
                logger.warning("Failed to write text at %s: %s", rect, e)
                # Fallback: simple insert
                page.insert_text(insertion_point, translated, fontsize=fontsize)

    doc.save(output_path)
    doc.close()
    return output_path


def extract_pdf_text(input_path: str) -> str:
    """Extract all text from a PDF (for preview/simple text mode)."""
    doc = fitz.open(input_path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n\n".join(text_parts)
