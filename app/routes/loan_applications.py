from http import HTTPStatus

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models.loan_application import LoanApplication
from app.utils.decorators import any_role_required, super_user_required
from app.validators import loan_application_validator
from app.services import loan_application_service

bp = Blueprint("loan_applications", __name__, url_prefix="/api/loan-applications")


@bp.get("/")
@any_role_required
def list_loan_applications():
    apps = db.session.execute(db.select(LoanApplication)).scalars().all()
    return jsonify([a.to_dict() for a in apps]), HTTPStatus.OK


@bp.post("/")
@super_user_required
def create_loan_application():
    data = request.get_json() or {}
    err = loan_application_validator.validate_create(data)
    if err:
        return err
    loan = loan_application_service.create(data)
    return jsonify(loan.to_dict()), HTTPStatus.CREATED


@bp.get("/<uuid:id>")
@any_role_required
def get_loan_application(id):
    loan = db.get_or_404(LoanApplication, id)
    return jsonify(loan.to_dict()), HTTPStatus.OK


@bp.put("/<uuid:id>")
@super_user_required
def update_loan_application(id):
    loan = db.get_or_404(LoanApplication, id)
    data = request.get_json() or {}
    if "status" in data:
        err = loan_application_validator.validate_status(data["status"])
        if err:
            return err
    loan = loan_application_service.update(loan, data)
    return jsonify(loan.to_dict()), HTTPStatus.OK


@bp.delete("/<uuid:id>")
@super_user_required
def delete_loan_application(id):
    loan = db.get_or_404(LoanApplication, id)
    loan_application_service.delete(loan)
    return jsonify({"message": "Loan application deleted"}), HTTPStatus.OK
