from app.extensions import db
from app.models.loan_application import LoanApplication
from app.utils.uuid_utils import parse_uuid


def create(data: dict) -> LoanApplication:
    loan = LoanApplication(
        client_id=parse_uuid(data["client_id"]),
        user_id=parse_uuid(data.get("user_id")),
        requested_amount=data["requested_amount"],
        status=data.get("status", "pending"),
    )
    db.session.add(loan)
    db.session.commit()
    return loan


def update(loan: LoanApplication, data: dict) -> LoanApplication:
    if "requested_amount" in data:
        loan.requested_amount = data["requested_amount"]
    if "status" in data:
        loan.status = data["status"]
    if "user_id" in data:
        loan.user_id = parse_uuid(data.get("user_id"))
    db.session.commit()
    return loan


def delete(loan: LoanApplication) -> None:
    db.session.delete(loan)
    db.session.commit()
