from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io
from model.predict import Predictor
from utils.nutrition import NutritionClient
import os

app = FastAPI(title='Food Nutrition Analyzer API (YOLOv8)')
predictor = Predictor(device=os.getenv('YOLO_DEVICE', 'cpu'), conf_thres=float(os.getenv('YOLO_CONF', '0.3')))
nutrition_client = NutritionClient(api_key=os.getenv('USDA_API_KEY', None))

@app.post('/analyze')
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert('RGB')
    preds = predictor.predict(image)
    results = []
    for p in preds:
        nutr = nutrition_client.lookup_food(p['label'])
        results.append({
            'label': p['label'],
            'confidence': float(p.get('confidence', 0.0)),
            'nutrition': nutr
        })
    return JSONResponse({'predictions': results})
