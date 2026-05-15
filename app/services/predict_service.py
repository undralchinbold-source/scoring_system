"""
PPT Архитектур — Service хэсэг
Business logic энд байна: predictor дуудах, DB-д хадгалах.
"""
import os

from flask import current_app

from app.extensions import db
from app.ml.predictor import predictor
from app.models.score_history import ScoreHistory


def _get_model_path() -> str:
    return os.path.join(
        os.path.dirname(current_app.root_path),
        "ml_model",
        "loan_scoring_model.pkl",
    )


def run_prediction(input_data: dict, application_id=None, user_id=None) -> dict:
    """
    1. Predictor-г ачаална (нэг удаа л ачаална)
    2. Таамаглал гаргана
    3. application_id байвал ScoreHistory-д хадгална
    4. Үр дүнг буцаана
    """
    predictor.load(_get_model_path())

    result = predictor.predict(input_data)

    score_record = None
    if application_id and user_id:
        history = ScoreHistory(
            application_id=application_id,
            model_version=result["model_version"],
            score=result["score"],
            decision=result["decision"],
            created_by=user_id,
        )
        db.session.add(history)
        db.session.commit()
        score_record = history.to_dict()

    result["score_history"] = score_record
    return result
