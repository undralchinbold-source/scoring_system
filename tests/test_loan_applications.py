from tests.conftest import auth


class TestLoanApplicationList:
    def test_returns_list(self, client, admin_token):
        res = client.get("/api/loan-applications/", headers=auth(admin_token))
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_requires_auth(self, client):
        res = client.get("/api/loan-applications/")
        assert res.status_code == 401


class TestLoanApplicationCreate:
    def test_creates_successfully(self, client, super_token, client_fixture):
        res = client.post("/api/loan-applications/", json={
            "client_id": str(client_fixture.id),
            "requested_amount": 10_000_000,
        }, headers=auth(super_token))
        assert res.status_code == 201
        data = res.get_json()
        assert data["requested_amount"] == 10_000_000.0
        assert data["status"] == "pending"

    def test_missing_client_id_returns_400(self, client, super_token):
        res = client.post("/api/loan-applications/",
                          json={"requested_amount": 1000}, headers=auth(super_token))
        assert res.status_code == 400

    def test_missing_amount_returns_400(self, client, super_token, client_fixture):
        res = client.post("/api/loan-applications/",
                          json={"client_id": str(client_fixture.id)}, headers=auth(super_token))
        assert res.status_code == 400

    def test_admin_cannot_create(self, client, admin_token, client_fixture):
        res = client.post("/api/loan-applications/", json={
            "client_id": str(client_fixture.id), "requested_amount": 1000,
        }, headers=auth(admin_token))
        assert res.status_code == 403

    def test_requires_auth(self, client):
        res = client.post("/api/loan-applications/", json={})
        assert res.status_code == 401


class TestLoanApplicationGet:
    def test_returns_loan(self, client, admin_token, loan_app_fixture):
        res = client.get(f"/api/loan-applications/{loan_app_fixture.id}",
                         headers=auth(admin_token))
        assert res.status_code == 200
        assert res.get_json()["id"] == str(loan_app_fixture.id)

    def test_not_found(self, client, admin_token):
        res = client.get("/api/loan-applications/00000000-0000-0000-0000-000000000000",
                         headers=auth(admin_token))
        assert res.status_code == 404


class TestLoanApplicationUpdate:
    def test_updates_amount(self, client, super_token, loan_app_fixture):
        res = client.put(f"/api/loan-applications/{loan_app_fixture.id}",
                         json={"requested_amount": 999_999}, headers=auth(super_token))
        assert res.status_code == 200
        assert res.get_json()["requested_amount"] == 999_999.0

    def test_updates_valid_status(self, client, super_token, loan_app_fixture):
        res = client.put(f"/api/loan-applications/{loan_app_fixture.id}",
                         json={"status": "approved"}, headers=auth(super_token))
        assert res.status_code == 200
        assert res.get_json()["status"] == "approved"

    def test_invalid_status_returns_400(self, client, super_token, loan_app_fixture):
        res = client.put(f"/api/loan-applications/{loan_app_fixture.id}",
                         json={"status": "flying"}, headers=auth(super_token))
        assert res.status_code == 400

    def test_not_found(self, client, super_token):
        res = client.put("/api/loan-applications/00000000-0000-0000-0000-000000000000",
                         json={}, headers=auth(super_token))
        assert res.status_code == 404

    def test_admin_cannot_update(self, client, admin_token, loan_app_fixture):
        res = client.put(f"/api/loan-applications/{loan_app_fixture.id}",
                         json={}, headers=auth(admin_token))
        assert res.status_code == 403


class TestLoanApplicationDelete:
    def test_deletes_successfully(self, client, super_token, db, client_fixture):
        from app.models.loan_application import LoanApplication
        loan = LoanApplication(client_id=client_fixture.id, requested_amount=1000)
        db.session.add(loan)
        db.session.commit()
        lid = loan.id
        res = client.delete(f"/api/loan-applications/{lid}", headers=auth(super_token))
        assert res.status_code == 200

    def test_not_found(self, client, super_token):
        res = client.delete("/api/loan-applications/00000000-0000-0000-0000-000000000000",
                            headers=auth(super_token))
        assert res.status_code == 404
