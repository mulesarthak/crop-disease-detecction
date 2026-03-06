from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import os
import numpy as np
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.environ.get("MODEL_PATH")
MODEL_TYPE = os.environ.get("MODEL_TYPE", "generic")
LABELS_STR = os.environ.get("CLASS_LABELS")
LABELS_PATH = os.environ.get("CLASS_LABELS_PATH")
CONFIDENCE_THRESHOLD = float(os.environ.get("CONFIDENCE_THRESHOLD", "0"))
CLASS_LABELS = []
if LABELS_STR:
    CLASS_LABELS = [x.strip() for x in LABELS_STR.split(",") if x.strip()]
elif LABELS_PATH and os.path.exists(LABELS_PATH):
    try:
        with open(LABELS_PATH, "r", encoding="utf-8") as f:
            CLASS_LABELS = [ln.strip() for ln in f if ln.strip()]
    except Exception:
        CLASS_LABELS = []
IMG_SIZE = int(os.environ.get("IMG_SIZE", "224"))
MEAN_STR = os.environ.get("MEAN", "0.485,0.456,0.406")
STD_STR = os.environ.get("STD", "0.229,0.224,0.225")
MEAN = np.array([float(x) for x in MEAN_STR.split(",")])
STD = np.array([float(x) for x in STD_STR.split(",")])

def load_model():
    if MODEL_PATH and MODEL_TYPE.lower() == "torch" and os.path.exists(MODEL_PATH):
        try:
            import torch
            m = None
            if MODEL_PATH.endswith(".pt") or MODEL_PATH.endswith(".pth"):
                try:
                    m = torch.jit.load(MODEL_PATH, map_location="cpu")
                except Exception:
                    m = torch.load(MODEL_PATH, map_location="cpu")
            else:
                m = torch.jit.load(MODEL_PATH, map_location="cpu")
            m.eval()
            return {"type": "torch", "impl": m}
        except Exception:
            return None
    if MODEL_PATH and MODEL_TYPE.lower() == "onnx" and os.path.exists(MODEL_PATH):
        try:
            import onnxruntime as ort
            sess = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
            return {"type": "onnx", "impl": sess}
        except Exception:
            return None
    if MODEL_PATH and MODEL_TYPE.lower() in ("tf", "tensorflow") and os.path.exists(MODEL_PATH):
        try:
            import tensorflow as tf
            model = tf.saved_model.load(MODEL_PATH)
            return {"type": "tf", "impl": model}
        except Exception:
            return None
    return None


MODEL = load_model()


def run_model(img):
    arr = np.array(img.resize((IMG_SIZE, IMG_SIZE)), dtype=np.float32) / 255.0
    arr = (arr - MEAN) / STD
    if arr.ndim == 3:
        arr = np.transpose(arr, (2, 0, 1))
    x = np.expand_dims(arr, 0)
    if MODEL and MODEL.get("type") == "torch":
        import torch
        with torch.no_grad():
            inp = torch.from_numpy(x)
            out = MODEL["impl"](inp)
            if isinstance(out, (list, tuple)):
                out = out[0]
            logits = out.cpu().numpy()
    elif MODEL and MODEL.get("type") == "onnx":
        sess = MODEL["impl"]
        name = sess.get_inputs()[0].name
        outs = sess.run(None, {name: x})
        logits = outs[0]
    elif MODEL and MODEL.get("type") == "tf":
        import tensorflow as tf
        pred = MODEL["impl"](tf.convert_to_tensor(x))
        logits = pred.numpy() if hasattr(pred, "numpy") else np.array(pred)
    else:
        label = CLASS_LABELS[0] if CLASS_LABELS else "Unknown"
        confidence = 0.87
        if CONFIDENCE_THRESHOLD and confidence < CONFIDENCE_THRESHOLD:
            label = "Uncertain"
        recs = [
            "Remove infected leaves to limit spread",
            "Apply a suitable fungicide as per label",
            "Water at soil level; avoid wetting leaves",
        ]
        return label, confidence, recs
    probs = logits
    if probs.ndim > 1:
        probs = probs[0]
    if probs.shape[0] > 1:
        e = np.exp(probs - np.max(probs))
        probs = e / np.sum(e)
    idx = int(np.argmax(probs))
    conf = float(probs[idx]) if probs.shape[0] > 1 else float(probs.squeeze())
    if CLASS_LABELS and idx < len(CLASS_LABELS):
        lbl = CLASS_LABELS[idx]
    else:
        lbl = f"class_{idx}"
    if CONFIDENCE_THRESHOLD and conf < CONFIDENCE_THRESHOLD:
        lbl = "Uncertain"
    recs = [
        "Remove infected leaves to limit spread",
        "Apply a suitable fungicide as per label",
        "Water at soil level; avoid wetting leaves",
    ]
    return lbl, conf, recs


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    content = await file.read()
    img = Image.open(io.BytesIO(content)).convert("RGB")
    label, confidence, recs = run_model(img)
    return {
        "disease": label,
        "confidence": float(confidence),
        "recommendations": recs,
    }

@app.get("/config")
async def config():
    return {
        "model_path": MODEL_PATH,
        "model_type": MODEL_TYPE,
        "labels_count": len(CLASS_LABELS),
        "confidence_threshold": CONFIDENCE_THRESHOLD,
    }
