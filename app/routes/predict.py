"""
PPT Алхам 4: /api/predict endpoint
Route → Validator → Service → Predictor → DB → Response
"""
import uuid
from http import HTTPStatus

from flask import Blueprint, jsonify, request

from app.auth import both_roles
from app.extensions import db
from app.models.loan_application import LoanApplication
from app.services.predict_service import run_prediction
from app.validators.predict_validator import validate_predict_input

bp = Blueprint("predict", __name__, url_prefix="/api")


def _parse_uuid(raw_id: str) -> uuid.UUID:
    """UUID parse — формат буруу бол ValueError өргөнө."""
    try:
        return uuid.UUID(str(raw_id))
    except ValueError:
        raise ValueError("application_id формат буруу — UUID байх ёстой")


def _enrich_data_from_loan(data: dict, loan: LoanApplication) -> None:
    """DB-с авсан утгуудыг data dict-д default болгоно."""
    data.setdefault("requested_amount", float(loan.requested_amount))
    if loan.client and loan.client.income is not None:
        data.setdefault("monthly_income", float(loan.client.income))


def _resolve_loan(data: dict):
    """application_id байвал DB-с loan авч, data-г баяжуулна."""
    application_id = data.get("application_id")
    if not application_id:
        return None
    app_uuid = _parse_uuid(application_id)
    loan = db.get_or_404(LoanApplication, app_uuid)
    _enrich_data_from_loan(data, loan)
    return loan


@bp.post("/predict")
@both_roles
def predict():
    """POST /api/predict — зээлийн зэрэглэл тооцоолно."""
    data = request.get_json() or {}

    try:
        loan = _resolve_loan(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST

    errors = validate_predict_input(data)
    if errors:
        return jsonify({"errors": errors}), HTTPStatus.BAD_REQUEST

    try:
        result = run_prediction(
            input_data=data,
            application_id=loan.id if loan else None,
            user_id=request.current_user.id if loan else None,
        )
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR
    except ValueError as exc:
        return jsonify({"error": f"Оролтын алдаа: {exc}"}), HTTPStatus.BAD_REQUEST
    except Exception as exc:
        return jsonify({"error": f"Таамаглал гаргахад алдаа гарлаа: {exc}"}), HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify(result), HTTPStatus.OK
