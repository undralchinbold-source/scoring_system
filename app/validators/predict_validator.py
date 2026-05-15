"""
PPT Архитектур — Validation хэсэг
Оролтын мэдээллийг шалгаж, алдааны тайлбар буцаана.
"""
from app.ml.predictor import EMPLOYMENT_TYPES


def validate_predict_input(data: dict) -> list[str]:
    """
    Оролтыг шалгаж, алдааны жагсаалт буцаана.
    Жагсаалт хоосон бол алдаагүй гэсэн үг.
    """
    errors = []

    required_fields = {
        "monthly_income": "Сарын орлого",
        "employment_years": "Ажилласан жил",
        "requested_amount": "Зээлийн дүн",
        "employment_type": "Ажлын байрны төрөл",
    }

    for field, label in required_fields.items():
        if field not in data or data[field] is None or data[field] == "":
            errors.append(f"{label} ({field}) шаардлагатай")

    if errors:
        return errors

    # Тоон утгуудыг шалгана
    for field in ("monthly_income", "employment_years", "requested_amount"):
        try:
            val = float(data[field])
            if val <= 0:
                errors.append(f"{field} 0-ээс их байх ёстой")
        except (TypeError, ValueError):
            errors.append(f"{field} тоон утга байх ёстой")

    # Ажлын байрны төрлийг шалгана
    if isinstance(data.get("employment_type"), str):
        if data["employment_type"] not in EMPLOYMENT_TYPES:
            errors.append(
                f"employment_type буруу. Зөв утгууд: {', '.join(EMPLOYMENT_TYPES)}"
            )

    return errors
