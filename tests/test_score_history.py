from tests.conftest import auth


class TestScoreHistoryList:
    def test_returns_list(self, client, admin_token):
        res = client.get("/api/score-history/", headers=auth(admin_token))
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_requires_auth(self, client):
        res = client.get("/api/score-history/")
        assert res.status_code == 401


class TestScoreHistoryCreate:
    def test_creates_successfully(self, client, super_token, loan_app_fixture):
        res = client.post("/api/score-history/", json={
            "application_id": str(loan_app_fixture.id),
            "model_version": "v1.0.0",
            "score": 800,
            "decision": "approved",
        }, headers=auth(super_token))
        assert res.status_code == 201
        data = res.get_json()
        assert data["score"] == 800.0
        assert data["decision"] == "approved"

    def test_missing_fields_returns_400(self, client, super_token):
        res = client.post("/api/score-history/", json={"model_version": "v1"},
                          headers=auth(super_token))
        assert res.status_code == 400

    def test_admin_cannot_create(self, client, admin_token, loan_app_fixture):
        res = client.post("/api/score-history/", json={
            "application_id": str(loan_app_fixture.id),
            "model_version": "v1", "score": 500, "decision": "rejected",
        }, headers=auth(admin_token))
        assert res.status_code == 403

    def test_requires_auth(self, client):
        res = client.post("/api/score-history/", json={})
        assert res.status_code == 401


class TestScoreHistoryGet:
    def test_returns_record(self, client, admin_token, score_history_fixture):
        res = client.get(f"/api/score-history/{score_history_fixture.id}",
                         headers=auth(admin_token))
        assert res.status_code == 200
        assert res.get_json()["id"] == str(score_history_fixture.id)

    def test_not_found(self, client, admin_token):
        res = client.get("/api/score-history/00000000-0000-0000-0000-000000000000",
                         headers=auth(admin_token))
        assert res.status_code == 404


class TestScoreHistoryUpdate:
    def test_updates_score(self, client, super_token, score_history_fixture):
        res = client.put(f"/api/score-history/{score_history_fixture.id}",
                         json={"score": 900}, headers=auth(super_token))
        assert res.status_code == 200
        assert res.get_json()["score"] == 900.0

    def test_updates_decision(self, client, super_token, score_history_fixture):
        res = client.put(f"/api/score-history/{score_history_fixture.id}",
                         json={"decision": "rejected"}, headers=auth(super_token))
        assert res.status_code == 200
        assert res.get_json()["decision"] == "rejected"

    def test_not_found(self, client, super_token):
        res = client.put("/api/score-history/00000000-0000-0000-0000-000000000000",
                         json={}, headers=auth(super_token))
        assert res.status_code == 404

    def test_admin_cannot_update(self, client, admin_token, score_history_fixture):
        res = client.put(f"/api/score-history/{score_history_fixture.id}",
                         json={}, headers=auth(admin_token))
        assert res.status_code == 403


class TestScoreHistoryDelete:
    def test_deletes_successfully(self, client, super_token, db, loan_app_fixture):
        from app.models.score_history import ScoreHistory
        s = ScoreHistory(application_id=loan_app_fixture.id,
                         model_version="v0", score=500, decision="rejected")
        db.session.add(s)
        db.session.commit()
        sid = s.id
        res = client.delete(f"/api/score-history/{sid}", headers=auth(super_token))
        assert res.status_code == 200

    def test_not_found(self, client, super_token):
        res = client.delete("/api/score-history/00000000-0000-0000-0000-000000000000",
                            headers=auth(super_token))
        assert res.status_code == 404
