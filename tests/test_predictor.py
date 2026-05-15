"""
PPT Архитектур — tests/ хавтас
Predictor болон validator-ийн unit тест.
conftest.py Flask app-г тест горимд тохируулсан байна.
"""
import os
import pytest

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "ml_model", "loan_scoring_model.pkl"
)

VALID_INPUT = {
    "monthly_income": 3_000_000,
    "employment_years": 5,
    "requested_amount": 10_000_000,
    "employment_type": "Инженер",
}


# ---------------------------------------------------------------------------
# Predictor тест
# ---------------------------------------------------------------------------

class TestLoanPredictor:
    def setup_method(self):
        from app.ml.predictor import LoanPredictor
        # Singleton-ийг reset хийнэ — тест бүр цэвэр эхэлнэ
        LoanPredictor._instance = None

    def _get_predictor(self):
        from app.ml.predictor import LoanPredictor
        p = LoanPredictor()
        p.load(MODEL_PATH)
        return p

    def test_load_success(self):
        p = self._get_predictor()
        assert p._loaded is True
        assert p.model_version is not None

    def test_singleton(self):
        from app.ml.predictor import LoanPredictor
        p1 = LoanPredictor()
        p2 = LoanPredictor()
        assert p1 is p2

    def test_predict_returns_required_fields(self):
        p = self._get_predictor()
        result = p.predict(VALID_INPUT)
        assert "score" in result
        assert "decision" in result
        assert "probabilities" in result
        assert "model_version" in result

    def test_score_range(self):
        p = self._get_predictor()
        result = p.predict(VALID_INPUT)
        assert 0.0 <= result["score"] <= 1.0

    def test_decision_is_valid(self):
        p = self._get_predictor()
        result = p.predict(VALID_INPUT)
        assert result["decision"] in ("approved", "manual_review", "rejected")

    def test_probabilities_sum_to_one(self):
        p = self._get_predictor()
        result = p.predict(VALID_INPUT)
        total = sum(result["probabilities"].values())
        assert abs(total - 1.0) < 0.01

    def test_high_risk_case(self):
        p = self._get_predictor()
        result = p.predict({
            "monthly_income": 400_000,
            "employment_years": 0.5,
            "requested_amount": 80_000_000,
            "employment_type": "Худалдагч",
        })
        assert result["decision"] in ("rejected", "manual_review")

    def test_invalid_employment_type(self):
        p = self._get_predictor()
        with pytest.raises(Exception):
            p.predict({**VALID_INPUT, "employment_type": "InvalidType"})

    def test_model_not_loaded_raises(self):
        from app.ml.predictor import LoanPredictor
        p = LoanPredictor()
        p._loaded = False
        with pytest.raises(RuntimeError, match="ачаалагдаагүй"):
            p.predict({})

    def test_file_not_found(self):
        from app.ml.predictor import LoanPredictor
        p = LoanPredictor()
        with pytest.raises(FileNotFoundError):
            p.load("/nonexistent/path/model.pkl")


# ---------------------------------------------------------------------------
# Validator тест
# ---------------------------------------------------------------------------

class TestPredictValidator:
    def _validate(self, data):
        from app.validators.predict_validator import validate_predict_input
        return validate_predict_input(data)

    def test_valid_input_no_errors(self):
        errors = self._validate(VALID_INPUT)
        assert errors == []

    def test_missing_employment_type(self):
        data = {k: v for k, v in VALID_INPUT.items() if k != "employment_type"}
        errors = self._validate(data)
        assert any("employment_type" in e for e in errors)

    def test_missing_monthly_income(self):
        data = {k: v for k, v in VALID_INPUT.items() if k != "monthly_income"}
        errors = self._validate(data)
        assert any("monthly_income" in e for e in errors)

    def test_negative_income_rejected(self):
        errors = self._validate({**VALID_INPUT, "monthly_income": -100})
        assert any("monthly_income" in e for e in errors)

    def test_zero_amount_rejected(self):
        errors = self._validate({**VALID_INPUT, "requested_amount": 0})
        assert any("requested_amount" in e for e in errors)

    def test_invalid_employment_type_string(self):
        errors = self._validate({**VALID_INPUT, "employment_type": "Буруу төрөл"})
        assert any("employment_type" in e for e in errors)

    def test_non_numeric_income(self):
        errors = self._validate({**VALID_INPUT, "monthly_income": "тэрбум"})
        assert any("monthly_income" in e for e in errors)
