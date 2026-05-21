# Resume YOLO + OCR Pipeline

This repository contains a small pipeline to detect resume sections using a YOLO model and extract text from the cropped regions with OCR.

Contents
- `models/` — trained YOLO model file (not checked in by default)
- `outputs/crops/` — cropped images produced by detection
- `scripts/` — helper scripts: `predict.py`, `ocr_pipeline.py`, `run_ocr.py` (main OCR runner)
- `test_images/` — example resume images

Quickstart

1. Create a virtual environment and install dependencies:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run detection (produces crops in `outputs/crops`):

```cmd
python scripts/predict.py
```

3. Run OCR on the crops (uses PaddleOCR if available, otherwise falls back to Tesseract via pytesseract):

```cmd
REM If you prefer the lightweight fallback (Tesseract must be installed):
set PATH=C:\Program Files\Tesseract-OCR;%PATH%
set PADDLE_SKIP=1
python scripts/run_ocr.py
```

Notes
- If you encounter a runtime error from Paddle (oneDNN / ConvertPirAttribute2RuntimeAttribute), see `README_OCR.md` for troubleshooting. The repository includes guarded initialization to avoid hangs and a pytesseract fallback.
- Do not commit heavy model files to the repository. Keep `models/` in `.gitignore` (already set).

API keys & secrets (how to store and update)
----------------------------------------

This project may need API keys or other secrets if you extend it (for example, calling external parsers, storing data in cloud, or using third-party OCR/LLM APIs). Follow these best practices:

- Use a local `.env` file during development and never commit it. Add `.env` to `.gitignore`.
- Provide a `.env.example` in the repo with descriptive placeholder names so contributors know which variables to set.
- Use the `python-dotenv` package or `os.environ` to read keys in your scripts.
- For CI/CD (GitHub Actions), set secrets in the repository settings and read them as environment variables in workflows.

Example `.env` (DO NOT COMMIT):

```env
API_KEY_MY_SERVICE=sk_live_...your_key_here...
STORAGE_URL=https://your-storage.example.com
OTHER_SECRET=foobar
```

How to load `.env` safely in Python:

```py
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env into environment
API_KEY = os.getenv('API_KEY_MY_SERVICE')
```

Updating API keys (local dev):

- Edit `.env` and set the new values.
- If your app caches tokens, restart the process to pick up the change.

Updating API keys (GitHub production):

1. Go to your GitHub repository -> Settings -> Secrets -> Actions.
2. Add a new repository secret (e.g. `API_KEY_MY_SERVICE`) with the secret value.
3. In your GitHub Actions workflow, access it via `secrets.API_KEY_MY_SERVICE` and pass it to the job step as an environment variable.

Security tips
- Never print secrets to logs. Mask them in CI where possible.
- Rotate keys regularly and delete revoked keys.
- Store long-lived credentials in a secure vault for production environments.

License
- Add your license file if you plan to publish this repo.
