"""
PPT Алхам 4: /api/predict endpoint
Route → Validator → Service → Predictor → DB → Response
"""
import uuid

from flask import Blueprint, jsonify, request

from app.auth import both_roles
from app.extensions import db
from app.models.loan_application import LoanApplication
from app.services.predict_service import run_prediction
from app.validators.predict_validator import validate_predict_input

bp = Blueprint("predict", __name__, url_prefix="/api")


@bp.post("/predict")
@both_roles
def predict():
    """
    POST /api/predict

    Body (JSON):
      Шаардлагатай талбарууд:
        monthly_income   – сарын орлого (₮)
        employment_years – ажилласан жил
        requested_amount – зээлийн дүн (₮)
        employment_type  – ажлын байрны төрөл (Монголоор)

      Нэмэлт (заавал биш):
        application_id   – зээлийн өргөдлийн UUID.
                           Байвал DB-с requested_amount болон monthly_income
                           автоматаар авч ScoreHistory-д хадгална.
                           Гараар оруулсан утга DB утгыг дарж бичнэ.

    Response:
      score        – зөвшөөрлийн магадлал [0-1]
      decision     – approved / manual_review / rejected
      probabilities – бүх классын магадлал
      model_version – загварын хувилбар
      score_history – DB-д хадгалагдсан бичлэг (application_id байвал)
    """
    data = request.get_json() or {}

    application_id = data.get("application_id")
    loan = None

    # application_id ирвэл DB-с мэдээлэл авна
    if application_id:
        try:
            app_uuid = uuid.UUID(str(application_id))
        except ValueError:
            return jsonify({"error": "application_id формат буруу — UUID байх ёстой"}), 400

        loan = db.get_or_404(LoanApplication, app_uuid)

        # DB-с авсан утгуудыг default болгоно (caller override хийж болно)
        data.setdefault("requested_amount", float(loan.requested_amount))
        if loan.client and loan.client.income is not None:
            data.setdefault("monthly_income", float(loan.client.income))

    # Validation
    errors = validate_predict_input(data)
    if errors:
        return jsonify({"errors": errors}), 400

    # Service давхарга руу шилжүүлнэ
    try:
        result = run_prediction(
            input_data=data,
            application_id=loan.id if loan else None,
            user_id=request.current_user.id if loan else None,
        )
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        return jsonify({"error": f"Оролтын алдаа: {exc}"}), 400
    except Exception as exc:
        return jsonify({"error": f"Таамаглал гаргахад алдаа гарлаа: {exc}"}), 500

    return jsonify(result), 200
