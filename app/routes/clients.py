import uuid
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.client import Client

bp = Blueprint("clients", __name__, url_prefix="/api/clients")


@bp.get("/")
def list_clients():
    clients = db.session.execute(db.select(Client)).scalars().all()
    return jsonify([c.to_dict() for c in clients]), 200


@bp.post("/")
def create_client():
    data = request.get_json() or {}
    required = ("national_id", "fullname")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if db.session.execute(
        db.select(Client).filter_by(national_id=data["national_id"])
    ).scalar_one_or_none():
        return jsonify({"error": "national_id already exists"}), 409

    client = Client(
        national_id=data["national_id"],
        fullname=data["fullname"],
        income=data.get("income"),
        phone=data.get("phone"),
        created_by=uuid.UUID(data["created_by"]) if data.get("created_by") else None,
    )
    db.session.add(client)
    db.session.commit()
    return jsonify(client.to_dict()), 201


@bp.get("/<uuid:id>")
def get_client(id):
    client = db.get_or_404(Client, id)
    return jsonify(client.to_dict()), 200


@bp.put("/<uuid:id>")
def update_client(id):
    client = db.get_or_404(Client, id)
    data = request.get_json() or {}

    if "fullname" in data:
        client.fullname = data["fullname"]
    if "income" in data:
        client.income = data["income"]
    if "phone" in data:
        client.phone = data["phone"]

    db.session.commit()
    return jsonify(client.to_dict()), 200


@bp.delete("/<uuid:id>")
def delete_client(id):
    client = db.get_or_404(Client, id)
    db.session.delete(client)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Cannot delete client with existing loan applications"}), 409
    return jsonify({"message": "Client deleted"}), 200
