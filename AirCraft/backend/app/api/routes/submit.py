import json
import os
import logging

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src import crud

logger = logging.getLogger(__name__)

router = APIRouter()


class SubmitDataRequest(BaseModel):
    data: dict


@router.post("/")
async def submit_data(request: SubmitDataRequest, db: Session = Depends(get_db)):
    """Submit final JSON data"""
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Empty data")
        
        tracking_id = request.data.get("trackingId", "unknown")
        
        # Backup JSON logic
        backup_dir = "data/submissions"
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"backup_{tracking_id}.json")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(request.data, f, ensure_ascii=False, indent=4)
        
        logger.info("Data also persisted to Database")
        
        # Database persistence with Safe-Update logic
        aircrafts_saved = 0
        employees_saved = 0
        
        aircrafts_data = request.data.get("aircrafts", [])
        for ac_data in aircrafts_data:
            ac_id = ac_data.get("aircraft_id")
            if ac_id:
                existing_ac = crud.get_aircraft(db, ac_id)
                if existing_ac:
                    existing_ac.type = ac_data.get("type", existing_ac.type)
                    existing_ac.data = ac_data.get("data", existing_ac.data)
                    db.commit()
                    db.refresh(existing_ac)
                else:
                    crud.create_aircraft(db, ac_data)
                    db.commit()
                aircrafts_saved += 1
                
        employees_data = request.data.get("employees", [])
        for emp_data in employees_data:
            emp_id = emp_data.get("employee_id")
            if emp_id:
                existing_emp = crud.get_employee(db, emp_id)
                if existing_emp:
                    existing_emp.name = emp_data.get("name", existing_emp.name)
                    existing_emp.certificates = emp_data.get("certificates", existing_emp.certificates)
                    existing_emp.skills = emp_data.get("skills", existing_emp.skills)
                    db.commit()
                    db.refresh(existing_emp)
                else:
                    crud.create_employee(db, emp_data)
                    db.commit()
                employees_saved += 1
        
        return {
            "success": True,
            "message": "Data submitted successfully",
            "trackingId": tracking_id,
            "aircrafts_saved": aircrafts_saved,
            "employees_saved": employees_saved
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

