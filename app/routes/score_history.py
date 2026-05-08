import uuid
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.score_history import ScoreHistory

bp = Blueprint("score_history", __name__, url_prefix="/api/score-history")


@bp.get("/")
def list_score_history():
    records = db.session.execute(db.select(ScoreHistory)).scalars().all()
    return jsonify([r.to_dict() for r in records]), 200


@bp.post("/")
def create_score_history():
    data = request.get_json() or {}
    required = ("application_id", "model_version", "score", "decision")
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    record = ScoreHistory(
        application_id=uuid.UUID(data["application_id"]),
        model_version=data["model_version"],
        score=data["score"],
        decision=data["decision"],
        created_by=uuid.UUID(data["created_by"]) if data.get("created_by") else None,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@bp.get("/<uuid:id>")
def get_score_history(id):
    record = db.get_or_404(ScoreHistory, id)
    return jsonify(record.to_dict()), 200


@bp.put("/<uuid:id>")
def update_score_history(id):
    record = db.get_or_404(ScoreHistory, id)
    data = request.get_json() or {}

    if "model_version" in data:
        record.model_version = data["model_version"]
    if "score" in data:
        record.score = data["score"]
    if "decision" in data:
        record.decision = data["decision"]

    db.session.commit()
    return jsonify(record.to_dict()), 200


@bp.delete("/<uuid:id>")
def delete_score_history(id):
    record = db.get_or_404(ScoreHistory, id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Score history deleted"}), 200
