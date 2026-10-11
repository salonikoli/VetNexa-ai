from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import numpy as np
from werkzeug.utils import secure_filename

from disease_info import DISEASE_INFO
from history_service import save_prediction

bp = Blueprint("poultry", __name__)

UPLOAD_FOLDER = os.path.join("poultry", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MODEL_PATH = os.path.join("poultry", "model", "mobilenetV2", "mobilenetv2.h5")

# -----------------------------
# Lazy Model Loading
# -----------------------------

model = None
tf = None


def get_model():
    global model, tf

    if model is None:

        print(f"Loading Poultry Model from {MODEL_PATH}...")

        # Lazy import TensorFlow
        import tensorflow as tensorflow_lib
        tf = tensorflow_lib

        tf.get_logger().setLevel("ERROR")

        class DepthwiseConv2DFixed(tf.keras.layers.DepthwiseConv2D):
            def __init__(self, **kwargs):
                kwargs.pop("groups", None)
                super().__init__(**kwargs)

        model = tf.keras.models.load_model(
            MODEL_PATH,
            compile=False,
            custom_objects={"DepthwiseConv2D": DepthwiseConv2DFixed}
        )

        print("[OK] Poultry Model loaded successfully")

    return model


# -----------------------------
# Helpers
# -----------------------------

def allowed_file(filename: str):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def predict_image(image_path: str):

    model = get_model()

    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(128, 128))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)

    predictions = model.predict(img_array * 1 / 255.0)

    score = tf.nn.softmax(predictions[0])

    classes = {
        "Coccidiosis": 0,
        "Healthy": 1,
        "NewCastleDisease": 2,
        "Salmonella": 3
    }

    pred_class = [j for j in classes if classes[j] == int(np.argmax(score))][0]
    confidence = round(100 * float(np.max(score)), 2)

    return pred_class, confidence


# -----------------------------
# Routes
# -----------------------------

@bp.route("/", methods=["GET"])
def index():
    return render_template("poultry/index.html")


@bp.route("/predict", methods=["POST"])
def predict():

    if "file" not in request.files:
        return redirect(url_for("poultry.index"))

    file = request.files["file"]

    if file.filename == "":
        return redirect(url_for("poultry.index"))

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file.save(filepath)

        prediction, confidence = predict_image(filepath)

        info = DISEASE_INFO.get("poultry", {}).get(prediction, {
            "causes": ["Unknown"],
            "precautions": ["Consult a veterinarian"],
            "medications": ["N/A"],
            "foodItems": ["Balanced diet"]
        })

        user_id = request.form.get("user_id")

        if user_id:
            save_prediction(
                user_id=user_id,
                animal="poultry",
                disease=prediction,
                confidence=confidence,
                image_name=filename
            )

        return jsonify({
            "prediction": prediction,
            "confidence": confidence,
            "causes": info["causes"],
            "precautions": info["precautions"],
            "medications": info["medications"],
            "foodItems": info["foodItems"]
        })

    return jsonify({"error": "Invalid file type"}), 400


@bp.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
