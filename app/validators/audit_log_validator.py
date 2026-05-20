from flask import jsonify
from http import HTTPStatus


def validate_create(data: dict):
    required = ("action", "entity_type")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), HTTPStatus.BAD_REQUEST
    return None
