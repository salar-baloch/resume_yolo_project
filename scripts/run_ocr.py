import os
import logging
import sys
import subprocess
import time
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
# --- 0. ENVIRONMENT TWEAKS (must run before importing paddle/paddleocr) ---
# Disable oneDNN/mkldnn backends that can cause the "ConvertPirAttribute2RuntimeAttribute"
# NotImplementedError on some Windows/Paddle combinations. These flags are best-effort
# — if your environment requires oneDNN for performance, remove these lines and
# consider matching your PaddlePaddle version to the model artifacts instead.

os.environ.setdefault("FLAGS_use_mkldnn", "0")
os.environ.setdefault("PADDLE_WITH_MKLDNN", "0")
os.environ.setdefault("PADDLE_WITH_ONEDNN", "0")
# Avoid contacting model hosters (makes runs reproducible offline).
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

# Check whether the installed 'paddle' package can be imported quickly.
# Importing paddle in-process can hang on some setups (especially on Windows).
# We run a short subprocess that tries `import paddle` and times out quickly.
_paddle_available = False

# Allow forcing skip of Paddle check e.g. for testing fallback
if os.environ.get('PADDLE_SKIP', '').lower() in ('1', 'true', 'yes'):
    print('PADDLE_SKIP detected; skipping Paddle initialization and forcing pytesseract fallback.')
    _paddle_available = False
else:
    try:
        completed = subprocess.run(
            [sys.executable, "-c", "import paddle; print(paddle.__version__)"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if completed.returncode == 0:
            _paddle_available = True
            print("Detected paddle version:", completed.stdout.strip())
        else:
            print("Paddle import check failed (non-zero exit). Will skip PaddleOCR.")
            if completed.stderr:
                print(completed.stderr)
    except subprocess.TimeoutExpired:
        print("Paddle import check timed out. Skipping PaddleOCR to avoid hangs.")
    except Exception as e:
        print("Paddle import check raised an exception; skipping PaddleOCR.", e)

def try_create_paddleocr(timeout=10):
    """Try to import paddleocr and create an instance in a subprocess.
    Returns True if successful and False otherwise (including timeout).
    """
    import tempfile
    init_script = r"""
import json
from paddleocr import PaddleOCR
try:
    o = PaddleOCR(use_textline_orientation=True, lang='en', ocr_version='PP-OCRv4')
    print('OK')
except Exception as e:
    print('ERR:', e)
    raise
"""
    try:
        completed = subprocess.run(
            [sys.executable, "-c", init_script],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (completed.stdout or "") + (completed.stderr or "")
        if completed.returncode == 0 and 'OK' in out:
            return True
        print("PaddleOCR init subprocess failed:", out)
        return False
    except subprocess.TimeoutExpired:
        print("PaddleOCR init subprocess timed out (will fallback).")
        return False


if _paddle_available:
    _paddle_available = try_create_paddleocr(timeout=12)
    if _paddle_available:
        try:
            from paddleocr import PaddleOCR
        except Exception as e:
            print("Importing paddleocr failed after successful init check:", e)
            _paddle_available = False

# --- 1. SETUP & INITIALIZATION ---
logging.getLogger("ppocr").setLevel(logging.ERROR)

print("Loading OCR Model... ")

# Try to create a PaddleOCR instance but guard against long hangs / failures
ocr = None
_paddle_failed = False
try:
    # Use a stable v4 pipeline and enable orientation detection for textlines
    ocr = PaddleOCR(
        use_textline_orientation=True,
        lang='en',
        ocr_version='PP-OCRv4'
    )
except Exception as e:
    _paddle_failed = True
    print("Notice: PaddleOCR failed to initialize:", e)
    print("Attempting to fall back to pytesseract (if available)...\n")
    ocr = None

CROPS_DIR = "outputs/crops"

print("\nStarting Text Extraction...\n")

# --- 2. SAFETY CHECKS ---
if not os.path.isdir(CROPS_DIR):
    print(f"ERROR: crops directory '{CROPS_DIR}' not found. Make sure you ran the detection/crop step first.")
    sys.exit(1)

files = sorted([f for f in os.listdir(CROPS_DIR) if f.lower().endswith(('.jpg', '.png'))])
if not files:
    print(f"ERROR: no image files found in '{CROPS_DIR}'. Nothing to run OCR on.")
    sys.exit(1)

# --- 3. PROCESS EACH CROP ---
for image_file in files:
    image_path = os.path.join(CROPS_DIR, image_file)

    try:
        section_name = image_file.split('_', 1)[1].rsplit('.', 1)[0]
    except Exception:
        section_name = os.path.splitext(image_file)[0]

    print(f"========== {section_name.upper()} ==========")

    # --- 4. RUN OCR ---
    result = None
    if ocr is not None:
        # Try PaddleOCR predict (preferred)
        try:
            result = ocr.predict(image_path)
        except NotImplementedError as e:
            print("\nPaddle inference raised NotImplementedError:", e)
            print("Try installing a different Paddle build or use the pytesseract fallback.")
            ocr = None
            _paddle_failed = True
        except Exception as e:
            print("PaddleOCR predict failed:", e)
            # fall through to fallback if available
            ocr = None
            _paddle_failed = True

    if ocr is None:
        # Fallback: try pytesseract (lighter-weight and more likely to be available)
        try:
            from PIL import Image
            import pytesseract

            pil_img = Image.open(image_path).convert('RGB')
            text_string = pytesseract.image_to_string(pil_img)
            extracted_text = [line.strip() for line in text_string.splitlines() if line.strip()]
            print("\n".join(extracted_text))
            print("========================================\n")
            continue
        except Exception as e:
            # Neither paddle nor pytesseract is usable
            if _paddle_failed:
                print("ERROR: Both PaddleOCR failed and pytesseract is not available or errored.")
                print("To enable PaddleOCR: install paddlepaddle/paddlex per their docs, or to use pytesseract: pip install pytesseract pillow and install Tesseract OCR engine.")
            else:
                print("ERROR running OCR fallback:", e)
            continue

    # --- 5. CLEAN THE OUTPUT ---
    extracted_text = []

    # PaddleOCR predict returns a structure like: [ [ (box, (text, score)), ... ] ]
    try:
        page = result[0] if isinstance(result, (list, tuple)) and result else result
        for line in page:
            # line is (box, (text, score)) or similar
            if len(line) >= 2 and isinstance(line[1], (list, tuple)):
                text_string = line[1][0]
            elif len(line) >= 2:
                text_string = str(line[1])
            else:
                text_string = ''
            extracted_text.append(text_string)
    except Exception:
        # Fallback safe parsing for unexpected formats
        extracted_text = [str(r) for r in result]

    print("\n".join([t for t in extracted_text if t]))
    print("========================================\n")