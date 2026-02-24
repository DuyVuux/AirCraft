from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class Aircraft(Base):
    __tablename__ = "aircraft"

    id = Column(Integer, primary_key=True, index=True)
    aircraft_id = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSON, nullable=True)

    maintenance_tasks = relationship("MaintenanceTask", back_populates="aircraft")


class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    certificates = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)

    maintenance_tasks = relationship("MaintenanceTask", back_populates="assigned_employee")


class MaintenanceTask(Base):
    __tablename__ = "maintenance_task"

    id = Column(Integer, primary_key=True, index=True)
    task_code = Column(String, nullable=False, index=True)
    aircraft_db_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)
    assigned_employee_db_id = Column(Integer, ForeignKey("employee.id"), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, index=True)

    aircraft = relationship("Aircraft", back_populates="maintenance_tasks")
    assigned_employee = relationship("Employee", back_populates="maintenance_tasks")


class ScheduleJob(Base):
    __tablename__ = "schedule_jobs"

    job_id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False, default="PENDING", index=True)
    result_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
