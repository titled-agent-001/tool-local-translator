"""Image translation: OCR → translate → overlay text back on image."""

import logging
import os
import math
from PIL import Image, ImageDraw, ImageFont
from config import CJK_FONT_PATHS, LATIN_FONT_PATHS
from app.modules.ocr import extract_text_from_image
from app.modules.translator import translate_text

logger = logging.getLogger(__name__)


def _find_font(paths: list[str]) -> str | None:
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def _is_cjk(lang: str) -> bool:
    return lang in ("zh-TW", "zh-CN", "ja", "ko")


def _get_font(target_lang: str, size: int) -> ImageFont.FreeTypeFont:
    if _is_cjk(target_lang):
        path = _find_font(CJK_FONT_PATHS)
    else:
        path = _find_font(LATIN_FONT_PATHS)

    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _bbox_to_rect(bbox):
    """Convert 4-point bbox to (x_min, y_min, x_max, y_max)."""
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]
    return min(xs), min(ys), max(xs), max(ys)


def _fit_text_size(draw, text, font_path, max_width, max_height, start_size=40):
    """Find the largest font size that fits text in the given box."""
    for size in range(start_size, 4, -1):
        try:
            if font_path:
                font = ImageFont.truetype(font_path, size)
            else:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            if tw <= max_width and th <= max_height:
                return font, size
        except Exception:
            continue
    return ImageFont.load_default(), 10


def translate_image(
    input_path: str,
    source_lang: str,
    target_lang: str,
    output_path: str,
) -> str:
    """
    OCR an image, translate detected text, overlay translations.
    Returns the output file path.
    """
    # 1. OCR
    regions = extract_text_from_image(input_path, source_lang)
    if not regions:
        logger.info("No text detected in image")
        # Just copy the image
        img = Image.open(input_path)
        img.save(output_path)
        return output_path

    # 2. Open image
    img = Image.open(input_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    draw_base = ImageDraw.Draw(img)

    # Determine font path
    font_path = _find_font(CJK_FONT_PATHS if _is_cjk(target_lang) else LATIN_FONT_PATHS)

    # 3. Translate and overlay each region
    for region in regions:
        text = region["text"]
        bbox = region["bbox"]
        x_min, y_min, x_max, y_max = _bbox_to_rect(bbox)
        box_w = x_max - x_min
        box_h = y_max - y_min

        if box_w < 5 or box_h < 5:
            continue

        # Translate
        try:
            translated = translate_text(text, source_lang, target_lang)
        except Exception as e:
            logger.warning("Translation failed for region '%s': %s", text[:30], e)
            translated = text

        # Sample background color from region corners for fill
        try:
            pixels = []
            for px, py in [(x_min, y_min), (x_max, y_min), (x_min, y_max), (x_max, y_max)]:
                px = max(0, min(int(px), img.width - 1))
                py = max(0, min(int(py), img.height - 1))
                pixels.append(img.getpixel((px, py)))
            # Use most common or average as background
            avg_r = sum(p[0] for p in pixels) // 4
            avg_g = sum(p[1] for p in pixels) // 4
            avg_b = sum(p[2] for p in pixels) // 4
            bg_color = (avg_r, avg_g, avg_b, 255)
        except Exception:
            bg_color = (255, 255, 255, 255)

        # Determine text color (contrast with background)
        brightness = (bg_color[0] * 299 + bg_color[1] * 587 + bg_color[2] * 114) / 1000
        text_color = (0, 0, 0, 255) if brightness > 128 else (255, 255, 255, 255)

        # White-out original region
        draw_base.rectangle([x_min, y_min, x_max, y_max], fill=bg_color[:3])

        # Fit text
        temp_draw = ImageDraw.Draw(img)
        font, _ = _fit_text_size(temp_draw, translated, font_path, int(box_w), int(box_h), start_size=int(box_h))

        # Draw translated text
        draw_base.text(
            (x_min + 1, y_min + 1),
            translated,
            fill=text_color[:3],
            font=font,
        )

    # Save
    img = img.convert("RGB")
    img.save(output_path, quality=95)
    return output_path
