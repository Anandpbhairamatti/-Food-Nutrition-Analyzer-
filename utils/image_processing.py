from PIL import Image, ImageDraw, ImageFont

def preprocess_image(image):
    image = image.copy()
    image = image.resize((512,512))
    return image

def draw_predictions(image, preds):
    img = image.copy().convert('RGB')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    for p in preds:
        bbox = p.get('bbox', [10,10,100,100])
        label = f"{p['label']} ({p['confidence']:.2f})"
        bbox_i = [int(b) for b in bbox]
        draw.rectangle(bbox_i, outline='red', width=2)
        draw.text((bbox_i[0], max(bbox_i[1]-12,0)), label, fill='red', font=font)
    return img
