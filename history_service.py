from datetime import datetime
from database import users_collection


def save_prediction(user_id, animal, disease, confidence, image_name):

    history = {
        "animal": animal,
        "disease": disease,
        "confidence": float(confidence),
        "image": image_name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    users_collection.update_one(
        {"id": user_id},
        {"$push": {"history": history}}
    )