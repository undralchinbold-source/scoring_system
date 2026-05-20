from http import HTTPStatus

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models.score_history import ScoreHistory
from app.utils.decorators import any_role_required, super_user_required
from app.validators import score_history_validator
from app.services import score_history_service

bp = Blueprint("score_history", __name__, url_prefix="/api/score-history")


@bp.get("/")
@any_role_required
def list_score_history():
    records = db.session.execute(db.select(ScoreHistory)).scalars().all()
    return jsonify([r.to_dict() for r in records]), HTTPStatus.OK


@bp.post("/")
@super_user_required
def create_score_history():
    data = request.get_json() or {}
    err = score_history_validator.validate_create(data)
    if err:
        return err
    record = score_history_service.create(data)
    return jsonify(record.to_dict()), HTTPStatus.CREATED


@bp.get("/<uuid:id>")
@any_role_required
def get_score_history(id):
    record = db.get_or_404(ScoreHistory, id)
    return jsonify(record.to_dict()), HTTPStatus.OK


@bp.put("/<uuid:id>")
@super_user_required
def update_score_history(id):
    record = db.get_or_404(ScoreHistory, id)
    data = request.get_json() or {}
    record = score_history_service.update(record, data)
    return jsonify(record.to_dict()), HTTPStatus.OK


@bp.delete("/<uuid:id>")
@super_user_required
def delete_score_history(id):
    record = db.get_or_404(ScoreHistory, id)
    score_history_service.delete(record)
    return jsonify({"message": "Score history deleted"}), HTTPStatus.OK
