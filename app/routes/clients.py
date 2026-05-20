from http import HTTPStatus

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.client import Client
from app.utils.decorators import any_role_required, super_user_required
from app.validators import client_validator
from app.services import client_service

bp = Blueprint("clients", __name__, url_prefix="/api/clients")


@bp.get("/")
@any_role_required
def list_clients():
    clients = db.session.execute(db.select(Client)).scalars().all()
    return jsonify([c.to_dict() for c in clients]), HTTPStatus.OK


@bp.post("/")
@super_user_required
def create_client():
    data = request.get_json() or {}
    err = client_validator.validate_create(data)
    if err:
        return err
    if client_service.find_by_national_id(data["national_id"]):
        return jsonify({"error": "national_id already exists"}), HTTPStatus.CONFLICT
    client = client_service.create(data)
    return jsonify(client.to_dict()), HTTPStatus.CREATED


@bp.get("/<uuid:id>")
@any_role_required
def get_client(id):
    client = db.get_or_404(Client, id)
    return jsonify(client.to_dict()), HTTPStatus.OK


@bp.put("/<uuid:id>")
@super_user_required
def update_client(id):
    client = db.get_or_404(Client, id)
    data = request.get_json() or {}
    client = client_service.update(client, data)
    return jsonify(client.to_dict()), HTTPStatus.OK


@bp.delete("/<uuid:id>")
@super_user_required
def delete_client(id):
    client = db.get_or_404(Client, id)
    try:
        client_service.delete(client)
    except IntegrityError:
        return jsonify({"error": "Cannot delete client with existing loan applications"}), HTTPStatus.CONFLICT
    return jsonify({"message": "Client deleted"}), HTTPStatus.OK
