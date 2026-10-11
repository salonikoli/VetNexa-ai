from flask import Blueprint, render_template, request, jsonify
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename

from disease_info import DISEASE_INFO
from history_service import save_prediction

bp = Blueprint("cattle", __name__)

# -------------------------
# Configuration
# -------------------------

MODEL_PATH = os.path.join("cattle", "model", "best_densenet_cattle.keras")
IMG_SIZE = 224

DISEASE_TYPES = [
    "Foot and Mouth Disease",
    "Healthy",
    "Lumpy Skin Disease"
]

UPLOAD_FOLDER = os.path.join("cattle", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# Lazy Model Loading
# -------------------------

model = None

def get_model():
    global model

    if model is None:

        print(f"Loading Cattle Disease Model from {MODEL_PATH}...")

        # Lazy TensorFlow import
        import tensorflow as tf
        from tensorflow.keras.models import load_model

        tf.get_logger().setLevel("ERROR")

        model = load_model(MODEL_PATH)

        print("[OK] Cattle Model loaded successfully")

    return model


# -------------------------
# Image preprocessing
# -------------------------

def preprocess_image(filepath):

    img = cv2.imread(filepath)

    if img is None:
        raise ValueError("Invalid image or image not found")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    return img


# -------------------------
# Routes
# -------------------------

@bp.route("/")
def index():
    return render_template("cattle/index.html")


@bp.route("/predict", methods=["POST"])
def predict():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    try:

        img = preprocess_image(filepath)

        # Load model lazily
        model = get_model()

        preds = model.predict(img)

        class_id = int(np.argmax(preds))
        confidence = float(np.max(preds))

        result = DISEASE_TYPES[class_id]

        info = DISEASE_INFO.get("cattle", {}).get(result, {
            "causes": ["Unknown"],
            "precautions": ["Consult a veterinarian"],
            "medications": ["N/A"],
            "foodItems": ["Balanced diet"]
        })

        user_id = request.form.get("user_id")

        if user_id:
            save_prediction(
                user_id=user_id,
                animal="cattle",
                disease=result,
                confidence=confidence,
                image_name=filename
            )

        return jsonify({
            "prediction": result,
            "confidence": round(confidence * 100, 2),
            "causes": info["causes"],
            "precautions": info["precautions"],
            "medications": info["medications"],
            "foodItems": info["foodItems"]
        })

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": str(e)}), 500
