import uuid
from flask import jsonify, make_response
from http import HTTPStatus
from app.utils.decorators import validate_required

REQUIRED_FIELDS = (
    "application_id", "monthly_income", "employment_years",
    "requested_amount", "employment_type",
)


def _err(body: dict, status: int):
    return make_response(jsonify(body), status), None


def validate_inputs(data: dict, valid_employment_types: list):
    missing = validate_required(data, REQUIRED_FIELDS)
    if missing:
        return _err({"error": f"Missing fields: {', '.join(missing)}"}, HTTPStatus.BAD_REQUEST)

    try:
        application_id   = uuid.UUID(str(data["application_id"]))
        monthly_income   = float(data["monthly_income"])
        employment_years = float(data["employment_years"])
        requested_amount = float(data["requested_amount"])
        employment_type  = str(data["employment_type"])
    except (ValueError, TypeError) as e:
        return _err({"error": f"Invalid field value: {e}"}, HTTPStatus.BAD_REQUEST)

    if monthly_income <= 0 or requested_amount <= 0:
        return _err(
            {"error": "monthly_income and requested_amount must be positive"},
            HTTPStatus.BAD_REQUEST,
        )

    if employment_type not in valid_employment_types:
        return _err(
            {
                "error": f"Unknown employment_type '{employment_type}'",
                "valid_values": list(valid_employment_types),
            },
            HTTPStatus.BAD_REQUEST,
        )

    return None, {
        "application_id":   application_id,
        "monthly_income":   monthly_income,
        "employment_years": employment_years,
        "requested_amount": requested_amount,
        "employment_type":  employment_type,
    }
