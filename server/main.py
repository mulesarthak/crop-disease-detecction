from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import os
import json
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Load model
model = load_model("model/cotton_baseline_model.h5")
print("Model Loaded Successfully")

labels_path = os.environ.get("CLASS_LABELS_PATH", "model/labels.txt")
indices_path = os.environ.get("CLASS_INDICES_PATH", "model/class_indices.json")
classes = None
if os.path.exists(indices_path):
    try:
        with open(indices_path, "r", encoding="utf-8") as f:
            mapping = json.load(f)
        items = sorted(mapping.items(), key=lambda kv: kv[1])
        classes = [k for k, _ in items]
    except Exception:
        classes = None
if classes is None and os.path.exists(labels_path):
    try:
        with open(labels_path, "r", encoding="utf-8") as f:
            classes = [ln.strip() for ln in f if ln.strip()]
    except Exception:
        classes = None
if classes is None:
    classes = ["Bacterial Blight", "Curl Virus", "Fusarium Wilt", "Healthy"]

# Create FastAPI app
app = FastAPI()

# Enable CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health endpoint
@app.get("/")
def root():
    return {"status": "ok"}

# API docs available at /docs

# Prediction function
IMG_SIZE = int(os.environ.get("IMG_SIZE", "224"))
PREPROCESS = os.environ.get("PREPROCESS", "rescale_0_1").lower()

def preprocess(img_rgb):
    img = cv2.resize(img_rgb, (IMG_SIZE, IMG_SIZE))
    img = img.astype("float32")
    if PREPROCESS == "mobilenet_v2":
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        img = preprocess_input(img)
    elif PREPROCESS == "rescale_0_1":
        img = img / 255.0
    x = np.expand_dims(img, axis=0)
    return x

def predict_disease(img_bgr):
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    x = preprocess(img_rgb)
    prediction = model.predict(x)
    probs = prediction[0]
    idx = int(np.argmax(probs))
    label = classes[idx] if 0 <= idx < len(classes) else f"class_{idx}"
    conf = float(probs[idx])
    return label, conf


# API endpoint
@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    contents = await file.read()

    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    disease, conf = predict_disease(img)

    return {
        "disease": disease,
        "confidence": conf
    }


# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
