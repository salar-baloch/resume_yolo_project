Troubleshooting PaddleOCR / PaddlePaddle on Windows

If you see errors like:

- NotImplementedError: ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]
- Long hangs during `import paddle` or during predictor creation

Try the following steps in order:

1) Use CPU-only Paddle build without oneDNN/mkldnn
   - Uninstall existing paddle: `pip uninstall paddlepaddle -y`
   - Install the CPU wheel without oneDNN (example):
     `pip install paddlepaddle==3.3.1 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html`
   - Alternatively, install a different Paddle that explicitly supports oneDNN for your platform.

2) Set environment flags (we added these to `scripts/run_ocr.py`):
   - FLAGS_use_mkldnn=0
   - PADDLE_WITH_MKLDNN=0
   - PADDLE_WITH_ONEDNN=0
   - PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True

3) If Paddle is not required, use the Tesseract fallback:
   - Install Tesseract (Windows): https://github.com/tesseract-ocr/tesseract
   - Add its install folder to PATH (e.g. C:\Program Files\Tesseract-OCR)
   - Install Python packages: `pip install pytesseract pillow`

4) If you still want to use Paddle but see the ConvertPirAttribute2RuntimeAttribute error,
   consider downgrading or upgrading Paddle to a version that matches the model artifacts.
   Some users reported success with different paddlepaddle builds distributed on the Paddle website.

Extra notes:
- The repo includes a guarded init in `scripts/run_ocr.py` that tries to avoid hangs by
  running a quick subprocess import check and will fall back to pytesseract if Paddle
  initialization repeatedly fails.

