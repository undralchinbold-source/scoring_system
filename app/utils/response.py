"""
DRY helper: route-уудад давтагддаг error response-уудыг нэг газарт цуглуулав.
"""
from http import HTTPStatus

from flask import jsonify


def error_response(message: str, status: int = HTTPStatus.BAD_REQUEST):
    return jsonify({"error": message}), status


def missing_fields_error(missing: list):
    return error_response(f"Missing fields: {', '.join(missing)}")
