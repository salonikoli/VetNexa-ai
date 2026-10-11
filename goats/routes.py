from flask import Blueprint, request, jsonify, render_template
import numpy as np
from PIL import Image
import io
import os

from disease_info import DISEASE_INFO
from history_service import save_prediction

bp = Blueprint("goats", __name__)

# -----------------------------
# Configuration
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "best_goat_disease_model.h5")
IMG_SIZE = (224, 224)

CLASS_NAMES = [
    "Flea_Allergy",
    "Health",
    "Ringworm",
    "Scabies"
]

# -----------------------------
# Lazy Model Loading
# -----------------------------

model = None

def get_model():
    global model

    if model is None:

        print(f"Loading Goat Model from {MODEL_PATH}...")

        # Lazy TensorFlow import
        import tensorflow as tf

        tf.get_logger().setLevel("ERROR")

        model = tf.keras.models.load_model(MODEL_PATH)

        print("[OK] Goat Model loaded successfully")

    return model


# -----------------------------
# Image preprocessing
# -----------------------------

def preprocess_image(image_bytes):

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize(IMG_SIZE)
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)

    return image


# -----------------------------
# Routes
# -----------------------------

@bp.route("/", methods=["GET"])
def index():
    return render_template("goats/index.html")


@bp.route("/predict", methods=["POST"])
def predict():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:

        image_bytes = file.read()

        processed_image = preprocess_image(image_bytes)

        # Load model lazily
        model = get_model()

        predictions = model.predict(processed_image)[0]

        predicted_index = int(np.argmax(predictions))
        confidence = float(predictions[predicted_index])

        result = CLASS_NAMES[predicted_index]

        info = DISEASE_INFO.get("goats", {}).get(result, {
            "causes": ["Unknown"],
            "precautions": ["Consult a veterinarian"],
            "medications": ["N/A"],
            "foodItems": ["Balanced diet"]
        })

        user_id = request.form.get("user_id")

        if user_id:
            save_prediction(
                user_id=user_id,
                animal="goat",
                disease=result,
                confidence=confidence,
                image_name=file.filename
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
