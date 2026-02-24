import pytest
from src.models import User, Aircraft, Employee
from src.auth_utils import get_password_hash

def test_submit_data_flow(client, db_session):
    hashed_password = get_password_hash("testpassword")
    new_user = User(
        username="admin_test",
        hashed_password=hashed_password,
        role="Admin",
        is_active=True
    )
    db_session.add(new_user)
    db_session.commit()

    login_response = client.post(
        "/api/auth/login",
        data={"username": "admin_test", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    submit_payload = {
        "trackingId": "test_track_001",
        "aircrafts": [
            {
                "aircraft_id": "VN-A123",
                "type": "A321",
                "data": {"capacity": 200}
            }
        ],
        "employees": [
            {
                "employee_id": "EMP-001",
                "name": "Nguyen Van A",
                "certificates": ["A321 Basic"],
                "skills": ["Engine Repair"]
            }
        ]
    }

    submit_response = client.post(
        "/api/submit/",
        json={"data": submit_payload},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert submit_response.status_code == 200
    assert submit_response.json()["success"] is True

    saved_aircraft = db_session.query(Aircraft).filter(Aircraft.aircraft_id == "VN-A123").first()
    assert saved_aircraft is not None
    assert saved_aircraft.type == "A321"

    saved_employee = db_session.query(Employee).filter(Employee.employee_id == "EMP-001").first()
    assert saved_employee is not None
    assert saved_employee.name == "Nguyen Van A"
