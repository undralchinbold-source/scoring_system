import uuid
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.loan_application import LoanApplication
from app.utils.decorators import any_role_required, super_user_required

bp = Blueprint("loan_applications", __name__, url_prefix="/api/loan-applications")

ALLOWED_STATUSES = {"pending", "approved", "rejected", "cancelled"}


@bp.get("/")
@any_role_required
def list_loan_applications():
    apps = db.session.execute(db.select(LoanApplication)).scalars().all()
    return jsonify([a.to_dict() for a in apps]), 200


@bp.post("/")
@super_user_required
def create_loan_application():
    data = request.get_json() or {}
    required = ("client_id", "requested_amount")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    loan = LoanApplication(
        client_id=uuid.UUID(data["client_id"]),
        user_id=uuid.UUID(data["user_id"]) if data.get("user_id") else None,
        requested_amount=data["requested_amount"],
        status=data.get("status", "pending"),
    )
    db.session.add(loan)
    db.session.commit()
    return jsonify(loan.to_dict()), 201


@bp.get("/<uuid:id>")
@any_role_required
def get_loan_application(id):
    loan = db.get_or_404(LoanApplication, id)
    return jsonify(loan.to_dict()), 200


@bp.put("/<uuid:id>")
@super_user_required
def update_loan_application(id):
    loan = db.get_or_404(LoanApplication, id)
    data = request.get_json() or {}

    if "requested_amount" in data:
        loan.requested_amount = data["requested_amount"]
    if "status" in data:
        if data["status"] not in ALLOWED_STATUSES:
            return jsonify({"error": f"Invalid status. Choose from: {ALLOWED_STATUSES}"}), 400
        loan.status = data["status"]
    if "user_id" in data:
        loan.user_id = uuid.UUID(data["user_id"]) if data["user_id"] else None

    db.session.commit()
    return jsonify(loan.to_dict()), 200


@bp.delete("/<uuid:id>")
@super_user_required
def delete_loan_application(id):
    loan = db.get_or_404(LoanApplication, id)
    db.session.delete(loan)
    db.session.commit()
    return jsonify({"message": "Loan application deleted"}), 200
