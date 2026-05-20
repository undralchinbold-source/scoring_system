from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.client import Client
from app.utils.uuid_utils import parse_uuid


def find_by_national_id(national_id: str) -> Client | None:
    return db.session.execute(
        db.select(Client).filter_by(national_id=national_id)
    ).scalar_one_or_none()


def create(data: dict) -> Client:
    client = Client(
        national_id=data["national_id"],
        fullname=data["fullname"],
        income=data.get("income"),
        phone=data.get("phone"),
        created_by=parse_uuid(data.get("created_by")),
    )
    db.session.add(client)
    db.session.commit()
    return client


def update(client: Client, data: dict) -> Client:
    if "fullname" in data:
        client.fullname = data["fullname"]
    if "income" in data:
        client.income = data["income"]
    if "phone" in data:
        client.phone = data["phone"]
    db.session.commit()
    return client


def delete(client: Client) -> None:
    db.session.delete(client)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise
