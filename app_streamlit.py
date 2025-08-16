import streamlit as st
from PIL import Image
import io
import pandas as pd
from model.predict import Predictor
from utils.nutrition import NutritionClient
from utils.image_processing import preprocess_image, draw_predictions
import os

st.set_page_config(page_title="Food Nutrition Analyzer", layout="centered")
st.title("🍽️ Multimodal Food Nutrition Analyzer — YOLOv8")
st.markdown("Upload a photo of your meal and get an estimated calorie and nutrition breakdown.\n\nThis version uses YOLOv8 for detection if available.")

uploaded = st.file_uploader("Upload food photo", type=['png', 'jpg', 'jpeg'])
predictor = Predictor(device=os.getenv('YOLO_DEVICE', 'cpu'), conf_thres=float(os.getenv('YOLO_CONF', '0.3')))
nutrition_client = NutritionClient(api_key=os.getenv('USDA_API_KEY', None))

if uploaded is not None:
    image = Image.open(io.BytesIO(uploaded.read())).convert('RGB')
    st.image(image, caption='Uploaded image', use_container_width=True)

    with st.spinner('Detecting food items...'):
        preds = predictor.predict(image)

    if not preds:
        st.warning('No food items detected. Try another photo or check model.')
    else:
        # Normalize predictions into DataFrame
        for p in preds:
            p['confidence'] = float(p.get('confidence', 0.0))
        df = pd.DataFrame(preds)
        st.subheader('Detected items')
        st.dataframe(df[['label','confidence']].rename(columns={'confidence':'confidence (0-1)'}))

        with st.spinner('Fetching nutrition data...'):
            nutrition_rows = []
            for p in preds:
                label = p['label']
                nutr = nutrition_client.lookup_food(label)
                def safe(v):
                    try:
                        return None if v is None else float(v)
                    except Exception:
                        return None
                nutrition_rows.append({
                    'label': label,
                    'confidence': round(float(p.get('confidence',0)),3),
                    'matched_food': nutr.get('name') if isinstance(nutr.get('name'), str) else nutr.get('match', None),
                    'source': nutr.get('source', 'local' if nutr.get('match') else 'unknown'),
                    'calories': safe(nutr.get('calories')),
                    'protein_g': safe(nutr.get('protein_g')),
                    'fat_g': safe(nutr.get('fat_g')),
                    'carbs_g': safe(nutr.get('carbs_g')),
                })

        nutr_df = pd.DataFrame(nutrition_rows)
        st.subheader('Estimated nutrition per detected item')
        display_df = nutr_df.fillna('N/A')
        st.table(display_df[['label','confidence','matched_food','source','calories','protein_g','fat_g','carbs_g']])

        total = nutr_df[['calories','protein_g','fat_g','carbs_g']].apply(pd.to_numeric, errors='coerce').sum(skipna=True)
        total = total.round(1)
        st.subheader('Estimated total for meal')
        st.json({
            'calories': int(total.get('calories', 0)) if not pd.isna(total.get('calories', None)) else 0,
            'protein_g': float(total.get('protein_g', 0.0)),
            'fat_g': float(total.get('fat_g', 0.0)),
            'carbs_g': float(total.get('carbs_g', 0.0))
        })

        import matplotlib.pyplot as plt
        labels = ['protein_g','fat_g','carbs_g']
        vals = [float(total.get(c, 0.0)) for c in labels]
        if sum(vals) > 0:
            fig, ax = plt.subplots(figsize=(4,4))
            ax.pie(vals, labels=labels, autopct='%1.1f%%')
            ax.set_title('Macro-nutrient distribution (estimated)')
            st.pyplot(fig)
        else:
            st.info('Not enough numeric nutrition data to display macro distribution.')

        annotated = draw_predictions(image, preds)
        st.image(annotated, caption='Annotated detections', use_container_width=True)
else:
    st.info('Upload an image to get started.')
