import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes.submit import router as submit_router
from fastapi import FastAPI
from src.database import Base, get_db
from src import crud
from src.models import Aircraft, Employee

app = FastAPI()
app.include_router(submit_router, prefix="/api/submit")

from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_submit_data_success():
    payload = {
        "data": {
            "trackingId": "12345",
            "aircrafts": [
                {
                    "aircraft_id": "VN-123",
                    "type": "Boeing 737",
                    "data": {"capacity": 200}
                }
            ],
            "employees": [
                {
                    "employee_id": "EMP01",
                    "name": "Nguyen Van A",
                    "certificates": ["A"],
                    "skills": ["Mechanic"]
                }
            ]
        }
    }
    
    response = client.post("/api/submit/", json=payload)
    if response.status_code != 200:
        print("ERROR:", response.json())
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert res_json["aircrafts_saved"] == 1
    assert res_json["employees_saved"] == 1
    
    # Test update (Safe-Update feature)
    payload_update = {
        "data": {
            "trackingId": "12345-update",
            "aircrafts": [
                {
                    "aircraft_id": "VN-123",
                    "type": "Boeing 737 MAX",
                    "data": {"capacity": 220}
                }
            ],
            "employees": [
                {
                    "employee_id": "EMP01",
                    "name": "Nguyen Van A (Updated)",
                    "certificates": ["A", "B"],
                    "skills": ["Mechanic", "Electrician"]
                },
                {
                    "employee_id": "EMP02",
                    "name": "Tran Thi B",
                    "certificates": ["C"],
                    "skills": ["Engineer"]
                }
            ]
        }
    }
    
    response_update = client.post("/api/submit/", json=payload_update)
    assert response_update.status_code == 200
    res_update_json = response_update.json()
    assert res_update_json["success"] is True
    assert res_update_json["aircrafts_saved"] == 1
    assert res_update_json["employees_saved"] == 2
    
    # Verify in DB
    db = TestingSessionLocal()
    ac = crud.get_aircraft(db, "VN-123")
    assert ac.type == "Boeing 737 MAX"
    emp = crud.get_employee(db, "EMP01")
    assert emp.name == "Nguyen Van A (Updated)"
    assert len(emp.certificates) == 2
    db.close()
