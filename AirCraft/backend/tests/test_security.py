import os
import subprocess
import sys
import pytest
from src.models import User
from src.auth_utils import (
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    require_role,
    SECRET_KEY,
    REFRESH_SECRET_KEY,
)


class TestJWTSecretValidation:
    def test_secret_key_is_loaded(self):
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) >= 32

    def test_refresh_secret_key_is_loaded(self):
        assert REFRESH_SECRET_KEY is not None
        assert len(REFRESH_SECRET_KEY) >= 32

    def test_missing_jwt_secret_raises_runtime_error(self):
        result = subprocess.run(
            [
                sys.executable, "-c",
                "import os; os.environ.pop('JWT_SECRET_KEY', None); "
                "os.environ['REFRESH_SECRET_KEY'] = 'x' * 32; "
                "from src.auth_utils import SECRET_KEY"
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        assert result.returncode != 0
        assert "RuntimeError" in result.stderr

    def test_short_jwt_secret_raises_runtime_error(self):
        result = subprocess.run(
            [
                sys.executable, "-c",
                "import os; os.environ['JWT_SECRET_KEY'] = 'short'; "
                "os.environ['REFRESH_SECRET_KEY'] = 'x' * 32; "
                "from src.auth_utils import SECRET_KEY"
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        assert result.returncode != 0
        assert "RuntimeError" in result.stderr


class TestRefreshToken:
    def test_login_returns_refresh_token(self, client, db_session):
        hashed = get_password_hash("testpassword")
        user = User(username="reftestuser", hashed_password=hashed, role="admin", is_active=True)
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/auth/login",
            data={"username": "reftestuser", "password": "testpassword"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_endpoint(self, client, db_session):
        hashed = get_password_hash("testpassword")
        user = User(username="reftestuser2", hashed_password=hashed, role="operator", is_active=True)
        db_session.add(user)
        db_session.commit()

        login_response = client.post(
            "/api/auth/login",
            data={"username": "reftestuser2", "password": "testpassword"},
        )
        refresh_token = login_response.json()["refresh_token"]

        refresh_response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_response.status_code == 200
        assert "access_token" in refresh_response.json()

    def test_refresh_with_invalid_token(self, client):
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert response.status_code == 401

    def test_create_and_decode_refresh_token(self):
        token = create_refresh_token(data={"sub": "testuser"})
        payload = decode_refresh_token(token)
        assert payload["sub"] == "testuser"
        assert payload["type"] == "refresh"


class TestRBAC:
    def _get_token(self, client, db_session, username, role):
        hashed = get_password_hash("password123")
        user = User(username=username, hashed_password=hashed, role=role, is_active=True)
        db_session.add(user)
        db_session.commit()
        return create_access_token(data={"sub": username, "role": role})

    def test_admin_can_register_user(self, client, db_session):
        admin_token = self._get_token(client, db_session, "adminuser", "admin")
        response = client.post(
            "/api/auth/register",
            json={"username": "newuser", "password": "password123", "role": "viewer"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["username"] == "newuser"
        assert response.json()["role"] == "viewer"

    def test_operator_cannot_register_user(self, client, db_session):
        op_token = self._get_token(client, db_session, "opuser", "operator")
        response = client.post(
            "/api/auth/register",
            json={"username": "newuser2", "password": "password123", "role": "viewer"},
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert response.status_code == 403

    def test_viewer_cannot_register_user(self, client, db_session):
        viewer_token = self._get_token(client, db_session, "viewuser", "viewer")
        response = client.post(
            "/api/auth/register",
            json={"username": "newuser3", "password": "password123", "role": "viewer"},
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert response.status_code == 403

    def test_require_role_accepts_valid_role(self):
        class MockUser:
            role = "admin"
        checker = require_role(["admin", "operator"])
        result = checker(MockUser())
        assert result.role == "admin"

    def test_require_role_rejects_invalid_role(self):
        class MockUser:
            role = "viewer"
        checker = require_role(["admin"])
        with pytest.raises(Exception):
            checker(MockUser())

    def test_register_duplicate_username(self, client, db_session):
        admin_token = self._get_token(client, db_session, "admindup", "admin")
        client.post(
            "/api/auth/register",
            json={"username": "dupuser", "password": "password123", "role": "viewer"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        response = client.post(
            "/api/auth/register",
            json={"username": "dupuser", "password": "password123", "role": "viewer"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 409

    def test_register_invalid_role(self, client, db_session):
        admin_token = self._get_token(client, db_session, "adminrole", "admin")
        response = client.post(
            "/api/auth/register",
            json={"username": "baduser", "password": "password123", "role": "superadmin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 422


class TestCORS:
    def test_cors_allows_configured_origin(self, client):
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

    def test_cors_blocks_unknown_origin(self, client):
        response = client.options(
            "/",
            headers={
                "Origin": "http://evil.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") != "http://evil.com"
