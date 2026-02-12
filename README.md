# 🌐 Local Translator

A local translation web app for **images**, **PDFs**, and **text** with layout preservation.

![Screenshot placeholder](https://via.placeholder.com/800x400?text=Screenshots+Coming+Soon)

## Features

- **Text translation** — paste or type, get instant translations
- **Image translation** — OCR extracts text, translates, overlays back on the image
- **PDF translation** — extracts text blocks, translates, rebuilds PDF preserving layout
- **Auto-detect** source language
- Clean, modern web UI with drag-and-drop upload

## Supported Languages

| Code | Language |
|------|----------|
| en | English |
| fr | French |
| de | German |
| zh-TW | Chinese (Traditional) |
| zh-CN | Chinese (Simplified) |
| ko | Korean |
| ja | Japanese |

> Add more languages by editing `config.py` — they'll appear in the UI automatically.

## Quick Start (macOS)

Double-click **`start.command`** or drag it into Terminal — it handles everything (venv, deps, launch).

Then open **http://localhost:8080** in your browser.

## Manual Setup

```bash
# Clone
git clone https://github.com/titled-agent-001/tool-local-translator.git
cd tool-local-translator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python app/main.py
```

Open **http://localhost:8080** in your browser.

## Tech Stack

- **Backend**: Python / Flask
- **Translation**: deep-translator (Google Translate free API)
- **OCR**: EasyOCR
- **PDF**: PyMuPDF (fitz)
- **Image**: Pillow
- **Frontend**: Vanilla HTML/CSS/JS

## Project Structure

```
├── app/
│   ├── main.py              # Flask app & API routes
│   ├── modules/
│   │   ├── translator.py    # Translation engine
│   │   ├── ocr.py           # OCR text extraction
│   │   ├── pdf_handler.py   # PDF translate & rebuild
│   │   └── image_handler.py # Image translate & overlay
│   ├── static/              # CSS & JS
│   └── templates/           # HTML
├── config.py                # Language config & settings
├── requirements.txt
└── README.md
```

## License

MIT
