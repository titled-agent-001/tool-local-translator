# 🌐 Local Translator

A local translation web app for **images**, **PDFs**, and **text** with layout preservation. Powered by **Ollama** for high-quality, private, local AI translation.

![Screenshot placeholder](https://via.placeholder.com/800x400?text=Screenshots+Coming+Soon)

## Features

- **Text translation** — paste or type, get instant translations
- **Image translation** — OCR extracts text, translates, overlays back on the image
- **PDF translation** — extracts text blocks, translates, rebuilds PDF preserving layout
- **Auto-detect** source language
- **Financial document accuracy** — optimized prompts preserve financial terminology, numbers, and formatting
- **100% local & private** — all translation runs on your machine via Ollama, no data leaves your computer
- Clean, modern web UI with drag-and-drop upload and Ollama status indicator

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

### Prerequisites

1. **Install Ollama:**
   ```bash
   brew install ollama
   ```
   Or download from [ollama.com](https://ollama.com/download).

2. **Pull the translation model:**
   ```bash
   ollama pull qwen2.5:7b
   ```
   > `start.command` will do this automatically if needed, but pre-pulling avoids the wait.

### Run

Double-click **`start.command`** or drag it into Terminal — it handles everything (Ollama check, venv, deps, launch).

Then open **http://localhost:8080** in your browser.

## Manual Setup

```bash
# Clone
git clone https://github.com/titled-agent-001/tool-local-translator.git
cd tool-local-translator

# Ensure Ollama is running
ollama serve &
ollama pull qwen2.5:7b

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
- **Translation**: Ollama local LLM (qwen2.5:7b) — private, accurate, no API keys needed
- **OCR**: EasyOCR
- **PDF**: PyMuPDF (fitz)
- **Image**: Pillow
- **Frontend**: Vanilla HTML/CSS/JS

## Financial Document Translation

This tool is optimized for translating financial documents:
- Preserves numbers, dates, and monetary amounts exactly
- Maintains financial terminology (revenue, EBITDA, net income, 營收, 淨利, etc.)
- Keeps formatting and paragraph structure intact
- Works well with earnings reports, balance sheets, and regulatory filings

## Project Structure

```
├── app/
│   ├── main.py              # Flask app & API routes
│   ├── modules/
│   │   ├── translator.py    # Ollama translation engine
│   │   ├── ocr.py           # OCR text extraction
│   │   ├── pdf_handler.py   # PDF translate & rebuild
│   │   └── image_handler.py # Image translate & overlay
│   ├── static/              # CSS & JS
│   └── templates/           # HTML
├── config.py                # Language & Ollama config
├── requirements.txt
└── README.md
```

## Troubleshooting

### Ollama not running

If you see a ❌ next to the Ollama badge in the UI:
```bash
ollama serve
```
Or check if it's already running: `curl http://localhost:11434/api/tags`

### Model not found

If you see ⚠️ in the UI:
```bash
ollama pull qwen2.5:7b
```

### Translation is slow

The first translation after starting Ollama loads the model into memory (~4GB RAM for 7B). Subsequent translations are much faster. On Apple Silicon Macs, the model runs on GPU automatically.

### `NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+`

Install a newer Python via Homebrew:
```bash
brew install python3
rm -rf venv
```
Then run `start.command` again.

### Port 8080 already in use

Change the port in `app/main.py`.

## License

MIT
