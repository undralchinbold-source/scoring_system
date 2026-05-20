from http import HTTPStatus
from flask import jsonify


def validate_create(data: dict):
    required = ("application_id", "model_version", "score", "decision")
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), HTTPStatus.BAD_REQUEST
    return None
