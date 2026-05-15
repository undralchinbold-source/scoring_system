import os
import uuid
import threading
import numpy as np
import joblib
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.loan_application import LoanApplication
from app.models.score_history import ScoreHistory
from app.utils.decorators import any_role_required, current_user_id, validate_required

bp = Blueprint("predict", __name__, url_prefix="/api")

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_model", "loan_scoring_model.pkl")
_model_bundle = None
_model_lock = threading.Lock()

SCORE_MIN = 200
SCORE_MAX = 950

REQUIRED_FIELDS = (
    "application_id", "monthly_income", "employment_years",
    "requested_amount", "employment_type",
)


def _load_model():
    global _model_bundle
    if _model_bundle is None:
        with _model_lock:
            if _model_bundle is None:
                bundle = joblib.load(_MODEL_PATH)
                # Pre-compute static lookups once at load time
                bundle["_cls_idx"] = {
                    cls: i for i, cls in enumerate(bundle["label_encoder_decision"].classes_)
                }
                # Gradient Boosting was trained on unscaled data; only LR needs scaling
                bundle["_requires_scaling"] = bundle.get("model_name") == "Logistic Regression"
                _model_bundle = bundle
    return _model_bundle


def _probability_to_score(proba, cls_idx: dict) -> int:
    expected_quality = proba[cls_idx["approved"]] + proba[cls_idx["manual_review"]] * 0.5
    return int(round(SCORE_MIN + expected_quality * (SCORE_MAX - SCORE_MIN)))


@bp.post("/predict")
@any_role_required
def predict():
    data = request.get_json() or {}

    missing = validate_required(data, REQUIRED_FIELDS)
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        application_id   = uuid.UUID(str(data["application_id"]))
        monthly_income   = float(data["monthly_income"])
        employment_years = float(data["employment_years"])
        requested_amount = float(data["requested_amount"])
        employment_type  = str(data["employment_type"])
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid field value: {e}"}), 400

    if monthly_income <= 0 or requested_amount <= 0:
        return jsonify({"error": "monthly_income and requested_amount must be positive"}), 400

    db.get_or_404(LoanApplication, application_id)

    bundle  = _load_model()
    le_emp  = bundle["label_encoder_employment"]
    le_dec  = bundle["label_encoder_decision"]
    cls_idx = bundle["_cls_idx"]

    if employment_type not in le_emp.classes_:
        return jsonify({
            "error": f"Unknown employment_type '{employment_type}'",
            "valid_values": list(le_emp.classes_),
        }), 400

    emp_encoded            = le_emp.transform([employment_type])[0]
    amount_to_income_ratio = requested_amount / monthly_income
    annual_dti             = requested_amount / (monthly_income * 12)

    features = np.array([[
        monthly_income,
        employment_years,
        requested_amount,
        amount_to_income_ratio,
        annual_dti,
        np.log1p(monthly_income),
        np.log1p(requested_amount),
        emp_encoded,
    ]])

    x        = bundle["scaler"].transform(features) if bundle["_requires_scaling"] else features
    proba    = bundle["model"].predict_proba(x)[0]
    pred     = bundle["model"].predict(x)
    decision = le_dec.inverse_transform(pred)[0]

    credit_score = _probability_to_score(proba, cls_idx)

    history = ScoreHistory(
        application_id=application_id,
        model_version=bundle.get("model_version", "unknown"),
        score=credit_score,
        decision=decision,
        created_by=current_user_id(),
    )
    db.session.add(history)
    db.session.commit()

    return jsonify({
        "decision": decision,
        "credit_score": credit_score,
        "score_range": {"min": SCORE_MIN, "max": SCORE_MAX},
        "probabilities": {cls: round(float(p), 4) for cls, p in zip(le_dec.classes_, proba)},
        "model_name": bundle.get("model_name"),
        "model_version": bundle.get("model_version"),
        "score_history_id": str(history.id),
    }), 200
