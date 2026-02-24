import pytest
from src.models import User
from src.auth_utils import get_password_hash

def test_create_mock_user(db_session):
    hashed_password = get_password_hash("testpassword")
    new_user = User(
        username="testuser",
        hashed_password=hashed_password,
        role="Admin",
        is_active=True
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    
    assert new_user.id is not None
    assert new_user.username == "testuser"
    assert new_user.role == "Admin"
    assert new_user.is_active is True

def test_login_success(client, db_session):
    hashed_password = get_password_hash("testpassword")
    new_user = User(
        username="testuser",
        hashed_password=hashed_password,
        role="Admin",
        is_active=True
    )
    db_session.add(new_user)
    db_session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_failure(client, db_session):
    hashed_password = get_password_hash("testpassword")
    new_user = User(
        username="testuser",
        hashed_password=hashed_password,
        role="Admin",
        is_active=True
    )
    db_session.add(new_user)
    db_session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
