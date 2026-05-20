import uuid
import pytest
from unittest.mock import patch, MagicMock
from werkzeug.exceptions import NotFound
from tests.conftest import auth

EMPLOYMENT_TYPES = ["employed", "self_employed", "unemployed"]

MOCK_RESULT = {
    "decision": "approved",
    "credit_score": 750,
    "score_range": {"min": 200, "max": 950},
    "probabilities": {"approved": 0.75, "rejected": 0.20, "manual_review": 0.05},
    "model_name": "Gradient Boosting",
    "model_version": "v1.0",
    "score_history_id": "00000000-0000-0000-0000-000000000099",
}

_FAKE_APP_ID = str(uuid.uuid4())


def _mock_bundle():
    le_emp = MagicMock()
    le_emp.classes_ = EMPLOYMENT_TYPES
    return {"label_encoder_employment": le_emp}


def _valid_payload(application_id=None):
    return {
        "application_id": application_id or _FAKE_APP_ID,
        "monthly_income": 5_000_000,
        "employment_years": 3.0,
        "requested_amount": 10_000_000,
        "employment_type": "employed",
    }


def _mock_db_found():
    return patch("app.routes.predict.db.get_or_404", return_value=MagicMock())


def _mock_db_not_found():
    return patch("app.routes.predict.db.get_or_404", side_effect=NotFound())


class TestPredictAuth:
    """POST /api/predict — authentication"""

    def test_no_token_returns_401(self, client):
        res = client.post("/api/predict", json={})
        assert res.status_code == 401

    def test_admin_token_allowed(self, client, admin_token):
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()), \
             _mock_db_found(), \
             patch("app.services.predict_service.score", return_value=MOCK_RESULT):
            res = client.post("/api/predict", json=_valid_payload(), headers=auth(admin_token))
        assert res.status_code == 200

    def test_super_user_token_allowed(self, client, super_token):
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()), \
             _mock_db_found(), \
             patch("app.services.predict_service.score", return_value=MOCK_RESULT):
            res = client.post("/api/predict", json=_valid_payload(), headers=auth(super_token))
        assert res.status_code == 200


class TestPredictValidation:
    """POST /api/predict — input validation"""

    def test_missing_fields_returns_400(self, client, admin_token):
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()):
            res = client.post("/api/predict", json={}, headers=auth(admin_token))
        assert res.status_code == 400
        assert "error" in res.get_json()

    def test_missing_single_field_returns_400(self, client, admin_token):
        payload = {
            "monthly_income": 5_000_000,
            "employment_years": 3.0,
            "requested_amount": 10_000_000,
            "employment_type": "employed",
            # application_id missing
        }
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()):
            res = client.post("/api/predict", json=payload, headers=auth(admin_token))
        assert res.status_code == 400

    def test_invalid_uuid_returns_400(self, client, admin_token):
        payload = {
            "application_id": "not-a-uuid",
            "monthly_income": 5_000_000,
            "employment_years": 3.0,
            "requested_amount": 10_000_000,
            "employment_type": "employed",
        }
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()):
            res = client.post("/api/predict", json=payload, headers=auth(admin_token))
        assert res.status_code == 400
        assert "Invalid field value" in res.get_json()["error"]

    def test_invalid_numeric_type_returns_400(self, client, admin_token):
        payload = {
            "application_id": str(uuid.uuid4()),
            "monthly_income": "not-a-number",
            "employment_years": 3.0,
            "requested_amount": 10_000_000,
            "employment_type": "employed",
        }
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()):
            res = client.post("/api/predict", json=payload, headers=auth(admin_token))
        assert res.status_code == 400

    def test_zero_income_returns_400(self, client, admin_token):
        payload = {
            "application_id": str(uuid.uuid4()),
            "monthly_income": 0,
            "employment_years": 3.0,
            "requested_amount": 10_000_000,
            "employment_type": "employed",
        }
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()):
            res = client.post("/api/predict", json=payload, headers=auth(admin_token))
        assert res.status_code == 400
        assert "must be positive" in res.get_json()["error"]

    def test_negative_amount_returns_400(self, client, admin_token):
        payload = {
            "application_id": str(uuid.uuid4()),
            "monthly_income": 5_000_000,
            "employment_years": 3.0,
            "requested_amount": -1,
            "employment_type": "employed",
        }
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()):
            res = client.post("/api/predict", json=payload, headers=auth(admin_token))
        assert res.status_code == 400

    def test_unknown_employment_type_returns_400(self, client, admin_token):
        payload = {
            "application_id": str(uuid.uuid4()),
            "monthly_income": 5_000_000,
            "employment_years": 3.0,
            "requested_amount": 10_000_000,
            "employment_type": "astronaut",
        }
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()):
            res = client.post("/api/predict", json=payload, headers=auth(admin_token))
        assert res.status_code == 400
        data = res.get_json()
        assert "valid_values" in data
        assert data["valid_values"] == EMPLOYMENT_TYPES


class TestPredictNotFound:
    """POST /api/predict — loan application lookup"""

    def test_nonexistent_application_returns_404(self, client, admin_token):
        payload = _valid_payload("00000000-0000-0000-0000-000000000000")
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()), \
             _mock_db_not_found():
            res = client.post("/api/predict", json=payload, headers=auth(admin_token))
        assert res.status_code == 404


class TestPredictSuccess:
    """POST /api/predict — happy path"""

    def test_returns_200(self, client, admin_token):
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()), \
             _mock_db_found(), \
             patch("app.services.predict_service.score", return_value=MOCK_RESULT):
            res = client.post("/api/predict", json=_valid_payload(), headers=auth(admin_token))
        assert res.status_code == 200

    def test_response_contains_decision(self, client, admin_token):
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()), \
             _mock_db_found(), \
             patch("app.services.predict_service.score", return_value=MOCK_RESULT):
            res = client.post("/api/predict", json=_valid_payload(), headers=auth(admin_token))
        assert "decision" in res.get_json()

    def test_response_contains_credit_score(self, client, admin_token):
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()), \
             _mock_db_found(), \
             patch("app.services.predict_service.score", return_value=MOCK_RESULT):
            res = client.post("/api/predict", json=_valid_payload(), headers=auth(admin_token))
        assert "credit_score" in res.get_json()

    def test_response_contains_score_range(self, client, admin_token):
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()), \
             _mock_db_found(), \
             patch("app.services.predict_service.score", return_value=MOCK_RESULT):
            res = client.post("/api/predict", json=_valid_payload(), headers=auth(admin_token))
        data = res.get_json()
        assert data["score_range"]["min"] == 200
        assert data["score_range"]["max"] == 950

    def test_response_contains_probabilities(self, client, admin_token):
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()), \
             _mock_db_found(), \
             patch("app.services.predict_service.score", return_value=MOCK_RESULT):
            res = client.post("/api/predict", json=_valid_payload(), headers=auth(admin_token))
        assert "probabilities" in res.get_json()

    def test_response_contains_score_history_id(self, client, admin_token):
        with patch("app.services.predict_service.load_model", return_value=_mock_bundle()), \
             _mock_db_found(), \
             patch("app.services.predict_service.score", return_value=MOCK_RESULT):
            res = client.post("/api/predict", json=_valid_payload(), headers=auth(admin_token))
        assert "score_history_id" in res.get_json()
