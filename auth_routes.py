import uuid
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import users_collection

auth_bp = Blueprint('auth', __name__)


# ---------------- SIGNUP ---------------- #

@auth_bp.route('/signup', methods=['POST'])
def signup():

    data = request.get_json() or {}

    email = data.get('email')
    password = data.get('password')
    name = data.get('username') or data.get('name')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    # Check if user already exists
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    new_user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "password": generate_password_hash(password),
        "name": name,
        "history": []
    }

    users_collection.insert_one(new_user)

    return jsonify({
        "message": "User created successfully",
        "user": {
            "id": new_user["id"],
            "email": email,
            "name": name
        }
    }), 201


# ---------------- LOGIN ---------------- #

@auth_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json() or {}

    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({"email": email})

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"]
        }
    }), 200


# ---------------- ADD HISTORY ---------------- #

@auth_bp.route('/history', methods=['POST'])
def add_history():

    data = request.get_json() or {}

    user_id = data.get("user_id")
    history_item = data.get("history_item")

    if not user_id or not history_item:
        return jsonify({"error": "Missing data"}), 400

    users_collection.update_one(
        {"id": user_id},
        {"$push": {"history": history_item}}
    )

    return jsonify({"message": "History saved"}), 200


# ---------------- GET HISTORY ---------------- #

@auth_bp.route('/history/<user_id>', methods=['GET'])
def get_history(user_id):

    user = users_collection.find_one({"id": user_id})

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.get("history", []))
