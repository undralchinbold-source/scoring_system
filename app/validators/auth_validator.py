from http import HTTPStatus
from flask import jsonify


def validate_login(data: dict):
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "email and password are required"}), HTTPStatus.BAD_REQUEST
    return None
