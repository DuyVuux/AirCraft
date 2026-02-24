import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models import Aircraft, Employee
from src import crud

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_and_get_aircraft(db_session):
    aircraft_data = {
        "aircraft_id": "VN-123",
        "type": "Boeing 737",
        "data": {"capacity": 200}
    }
    created_aircraft = crud.create_aircraft(db_session, aircraft_data)
    assert created_aircraft.aircraft_id == "VN-123"
    assert created_aircraft.type == "Boeing 737"
    
    fetched_aircraft = crud.get_aircraft(db_session, "VN-123")
    assert fetched_aircraft is not None
    assert fetched_aircraft.id == created_aircraft.id

def test_get_nonexistent_aircraft(db_session):
    fetched_aircraft = crud.get_aircraft(db_session, "UNKNOWN")
    assert fetched_aircraft is None

def test_create_and_get_employees(db_session):
    emp1_data = {
        "employee_id": "EMP01",
        "name": "Nguyen Van A",
        "certificates": ["A", "B"],
        "skills": ["Mechanic"]
    }
    emp2_data = {
        "employee_id": "EMP02",
        "name": "Tran Thi B",
        "certificates": ["C"],
        "skills": ["Electrician"]
    }
    crud.create_employee(db_session, emp1_data)
    crud.create_employee(db_session, emp2_data)
    
    employees = crud.get_employees(db_session, skip=0, limit=10)
    assert len(employees) == 2
    assert employees[0].employee_id == "EMP01"
