# Multimodal Food Nutrition Analyzer (YOLOv8 Integrated)

This version replaces the demo predictor with a YOLOv8-based detector (ultralytics).
The app falls back to the stub predictor if ultralytics or Torch aren't available.

## Highlights
- `model/predict.py` now uses `ultralytics.YOLO` when installed.
- If `ultralytics` is missing or model weights can't be loaded, it automatically falls back to the demo stub.
- You can use the small `yolov8n.pt` model for quick testing (auto-downloaded by ultralytics).
- The rest of the app remains the same (uses local nutrition DB before USDA).

## Quick run (recommended)
1. Create & activate venv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
   ```
2. Install required packages (CPU example):
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   # If torch install fails, install PyTorch per official instructions, e.g. CPU wheel:
   # pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   ```
3. (Optional) Install ultralytics for YOLOv8:
   ```bash
   pip install ultralytics
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app_streamlit.py
   ```

## Notes on performance
- For faster detection, install a GPU-capable PyTorch and run with device='cuda' in `model/predict.py` or set environment variable `YOLO_DEVICE=cuda`.
- The first YOLO inference may download the model weights (~10-30 MB for yolov8n).

## Files changed/added
- model/predict.py — YOLOv8 integration with robust fallback.
- requirements.txt — includes ultralytics (optional) comment.

If you want, I can also add a `weights/` folder and pre-download `yolov8n.pt` into the repo (large ~20 MB), or prepare a Dockerfile for GPU setup.
