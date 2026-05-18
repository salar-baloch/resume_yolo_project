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

License
- Add your license file if you plan to publish this repo.
