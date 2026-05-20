from http import HTTPStatus
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.loan_application import LoanApplication
from app.utils.decorators import any_role_required, current_user_id
from app.validators import predict_validator
from app.services import predict_service

bp = Blueprint("predict", __name__, url_prefix="/api")


@bp.post("/predict")
@any_role_required
def predict():
    data = request.get_json() or {}

    bundle = predict_service.load_model()
    valid_employment_types = list(bundle["label_encoder_employment"].classes_)

    err, inputs = predict_validator.validate_inputs(data, valid_employment_types)
    if err is not None:
        return err

    db.get_or_404(LoanApplication, inputs["application_id"])

    result = predict_service.score(inputs, current_user_id())
    return jsonify(result), HTTPStatus.OK
