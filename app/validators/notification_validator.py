from http import HTTPStatus
from flask import jsonify


def validate_create(data: dict):
    required = ("channel", "recipient", "message_body")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), HTTPStatus.BAD_REQUEST
    return None
