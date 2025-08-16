"""YOLOv8-based Predictor with robust fallback to demo stub.

Behavior:
- Attempts to import ultralytics.YOLO and use it for detection.
- If ultralytics or torch is not available, falls back to the lightweight demo stub.
- Outputs detections as [{'label':str,'confidence':float,'bbox':[x1,y1,x2,y2]}, ...]
"""
from typing import List, Dict, Optional
from PIL import Image
import numpy as np

# Try to import ultralytics; if unavailable, we'll fallback to stub implementation
try:
    from ultralytics import YOLO
    _HAS_ULTRALYTICS = True
except Exception:
    _HAS_ULTRALYTICS = False

import random

class DemoStubPredictor:
    def __init__(self):
        self.labels = ['apple','banana','pizza','burger','salad','rice','pasta','fries','egg']

    def predict(self, image: Image.Image) -> List[Dict]:
        n = random.randint(1,3)
        out = []
        w,h = image.size
        for _ in range(n):
            label = random.choice(self.labels)
            conf = round(random.uniform(0.6,0.99),2)
            bbox = [int(w*0.1), int(h*0.1), int(w*0.6), int(h*0.6)]
            out.append({'label': label, 'confidence': conf, 'bbox': bbox})
        return out

class YOLOPredictor:
    def __init__(self, model_path: Optional[str] = 'yolov8n.pt', device: str = 'cpu', conf_thres: float = 0.3):
        # model_path can be a local path or an ultralytics model string
        self.device = device
        self.conf_thres = conf_thres
        self.model_path = model_path
        self.model = None
        try:
            self.model = YOLO(self.model_path)
            # Set model device if supported
            try:
                # ultralytics allows setting model.to(device) or passing device in predict
                pass
            except Exception:
                pass
        except Exception as e:
            # If model fails to load, raise to let caller fallback
            raise RuntimeError(f"Failed to initialize YOLO model: {e}")

    def predict(self, image: Image.Image) -> List[Dict]:
        # ultralytics can accept numpy arrays
        arr = np.array(image)
        # run prediction; pass device and conf threshold
        results = self.model.predict(source=arr, imgsz=640, conf=self.conf_thres, device=self.device)
        if not results or len(results) == 0:
            return []
        res = results[0]
        boxes = getattr(res, 'boxes', None)
        if boxes is None or len(boxes) == 0:
            return []
        xyxy = boxes.xyxy.cpu().numpy()  # (N,4)
        confs = boxes.conf.cpu().numpy() # (N,)
        clss = boxes.cls.cpu().numpy()   # (N,)
        out = []
        for bbox, conf, cls_idx in zip(xyxy, confs, clss):
            label = self.model.names[int(cls_idx)]
            out.append({
                'label': str(label),
                'confidence': float(conf),
                'bbox': [float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])]
            })
        return out

class Predictor:
    def __init__(self, model_path: Optional[str] = 'yolov8n.pt', device: str = 'cpu', conf_thres: float = 0.3):
        self.device = device
        self.conf_thres = conf_thres
        self.model_path = model_path
        self._predictor = None
        # Prefer YOLO if available
        if _HAS_ULTRALYTICS:
            try:
                self._predictor = YOLOPredictor(model_path=self.model_path, device=self.device, conf_thres=self.conf_thres)
            except Exception as e:
                # Fallback to demo stub if loading fails
                print(f"[Predictor] YOLO init failed, falling back to demo stub: {e}")
                self._predictor = DemoStubPredictor()
        else:
            print("[Predictor] ultralytics not available — using demo stub predictor. To enable YOLO, pip install ultralytics and torch.")
            self._predictor = DemoStubPredictor()

    def predict(self, image: Image.Image) -> List[Dict]:
        return self._predictor.predict(image)
