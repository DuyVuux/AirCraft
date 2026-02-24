import pytest
from fastapi.testclient import TestClient

import os
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-must-be-at-least-32-characters-long")
os.environ.setdefault("REFRESH_SECRET_KEY", "test-refresh-secret-key-must-be-32-chars-long")

from main import app
from src.database import engine
from src import models

models.Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def auth_headers(client):
    from src.database import SessionLocal
    from src.auth_utils import get_password_hash

    db = SessionLocal()
    existing = db.query(models.User).filter(models.User.username == "schedtestadmin").first()
    if not existing:
        user = models.User(
            username="schedtestadmin",
            hashed_password=get_password_hash("testpassword123"),
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.commit()
    db.close()

    response = client.post("/api/auth/login", data={"username": "schedtestadmin", "password": "testpassword123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestSchedulerAPI:
    def test_scheduler_status_requires_valid_job(self, client, auth_headers):
        response = client.get("/api/scheduler/status/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    def test_scheduler_algorithms_endpoint(self, client, auth_headers):
        response = client.get("/api/scheduler/algorithms", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "algorithms" in data
        assert len(data["algorithms"]) >= 3
        assert "optimizeOptions" in data
