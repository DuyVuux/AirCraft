from sqlalchemy.orm import Session
from src.models import Aircraft, Employee


def get_aircraft(db: Session, aircraft_id: str) -> Aircraft | None:
    return db.query(Aircraft).filter(Aircraft.aircraft_id == aircraft_id).first()


def create_aircraft(db: Session, aircraft_data: dict) -> Aircraft:
    db_obj = Aircraft(**aircraft_data)
    db.add(db_obj)
    db.flush()
    return db_obj


def get_employees(db: Session, skip: int = 0, limit: int = 100) -> list[Employee]:
    return db.query(Employee).offset(skip).limit(limit).all()


def get_employee(db: Session, employee_id: str) -> Employee | None:
    return db.query(Employee).filter(Employee.employee_id == employee_id).first()


def create_employee(db: Session, employee_data: dict) -> Employee:
    db_obj = Employee(**employee_data)
    db.add(db_obj)
    db.flush()
    return db_obj
