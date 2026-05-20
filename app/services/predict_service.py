import os
import threading
import numpy as np
import joblib
from app.extensions import db
from app.models.score_history import ScoreHistory
from app.config.constants import SCORE_MIN, SCORE_MAX, MANUAL_REVIEW_WEIGHT

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_model", "loan_scoring_model.pkl")
_model_bundle = None
_model_lock = threading.Lock()


def load_model():
    global _model_bundle
    if _model_bundle is None:
        with _model_lock:
            if _model_bundle is None:
                bundle = joblib.load(_MODEL_PATH)
                bundle["_cls_idx"] = {
                    cls: i for i, cls in enumerate(bundle["label_encoder_decision"].classes_)
                }
                # Gradient Boosting was trained on unscaled data; only LR needs scaling
                bundle["_requires_scaling"] = bundle.get("model_name") == "Logistic Regression"
                _model_bundle = bundle
    return _model_bundle


def _build_features(monthly_income: float, employment_years: float,
                    requested_amount: float, emp_encoded: int) -> np.ndarray:
    amount_to_income_ratio = requested_amount / monthly_income
    annual_dti             = requested_amount / (monthly_income * 12)
    return np.array([[
        monthly_income,
        employment_years,
        requested_amount,
        amount_to_income_ratio,
        annual_dti,
        np.log1p(monthly_income),
        np.log1p(requested_amount),
        emp_encoded,
    ]])


def _probability_to_score(proba, cls_idx: dict) -> int:
    expected_quality = proba[cls_idx["approved"]] + proba[cls_idx["manual_review"]] * MANUAL_REVIEW_WEIGHT
    return int(round(SCORE_MIN + expected_quality * (SCORE_MAX - SCORE_MIN)))


def score(inputs: dict, user_id) -> dict:
    bundle  = load_model()
    le_emp  = bundle["label_encoder_employment"]
    le_dec  = bundle["label_encoder_decision"]
    cls_idx = bundle["_cls_idx"]

    emp_encoded = le_emp.transform([inputs["employment_type"]])[0]
    features    = _build_features(
        inputs["monthly_income"],
        inputs["employment_years"],
        inputs["requested_amount"],
        emp_encoded,
    )

    x        = bundle["scaler"].transform(features) if bundle["_requires_scaling"] else features
    proba    = bundle["model"].predict_proba(x)[0]
    pred     = bundle["model"].predict(x)
    decision = le_dec.inverse_transform(pred)[0]

    credit_score = _probability_to_score(proba, cls_idx)

    history = ScoreHistory(
        application_id=inputs["application_id"],
        model_version=bundle.get("model_version", "unknown"),
        score=credit_score,
        decision=decision,
        created_by=user_id,
    )
    db.session.add(history)
    db.session.commit()

    return {
        "decision":        decision,
        "credit_score":    credit_score,
        "score_range":     {"min": SCORE_MIN, "max": SCORE_MAX},
        "probabilities":   {cls: round(float(p), 4) for cls, p in zip(le_dec.classes_, proba)},
        "model_name":      bundle.get("model_name"),
        "model_version":   bundle.get("model_version"),
        "score_history_id": str(history.id),
    }
