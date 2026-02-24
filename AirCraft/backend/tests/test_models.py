import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import Aircraft, Employee, MaintenanceTask

# Thiết lập database in-memory cho testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Tạo các bảng
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Xoá các bảng sau mỗi test
        Base.metadata.drop_all(bind=engine)

def test_aircraft_creation(db_session):
    aircraft = Aircraft(
        aircraft_id="VN-A123",
        type="Airbus A321",
        data={"capacity": 200, "manufacturer": "Airbus"}
    )
    db_session.add(aircraft)
    db_session.commit()
    
    fetched_aircraft = db_session.query(Aircraft).filter_by(aircraft_id="VN-A123").first()
    assert fetched_aircraft is not None
    assert fetched_aircraft.type == "Airbus A321"
    assert fetched_aircraft.data["capacity"] == 200

def test_employee_creation(db_session):
    employee = Employee(
        employee_id="E001",
        name="Nguyen Van A",
        certificates=["B1", "B2"],
        skills=["Engine", "Avionics"]
    )
    db_session.add(employee)
    db_session.commit()
    
    fetched_employee = db_session.query(Employee).filter_by(employee_id="E001").first()
    assert fetched_employee is not None
    assert fetched_employee.name == "Nguyen Van A"
    assert "B1" in fetched_employee.certificates

def test_maintenance_task_creation_and_relationships(db_session):
    aircraft = Aircraft(aircraft_id="VN-A888", type="Boeing 787")
    employee = Employee(employee_id="E999", name="Tran Van B")
    
    db_session.add(aircraft)
    db_session.add(employee)
    db_session.commit()
    
    task = MaintenanceTask(
        task_code="TASK-001",
        aircraft_db_id=aircraft.id,
        assigned_employee_db_id=employee.id,
        start_time=datetime(2026, 3, 1, 8, 0),
        end_time=datetime(2026, 3, 1, 16, 0),
        status="PENDING"
    )
    db_session.add(task)
    db_session.commit()
    
    fetched_task = db_session.query(MaintenanceTask).filter_by(task_code="TASK-001").first()
    assert fetched_task is not None
    assert fetched_task.aircraft.aircraft_id == "VN-A888"
    assert fetched_task.assigned_employee.name == "Tran Van B"
    assert fetched_task.status == "PENDING"
