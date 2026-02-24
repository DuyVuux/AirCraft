import sys
import os
import json
import time
import logging
import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.database import SessionLocal, get_db
from src import models

ALGO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "AirCraft_algo"))

logger = logging.getLogger("scheduler")
router = APIRouter()

MAX_PAYLOAD_BYTES = 10 * 1024 * 1024


class SchedulerConfig(BaseModel):
    algorithm: str = "cpsat"
    timeLimit: int = Field(default=30, ge=1, le=600)
    optimizeFor: str = "makespan"


class SchedulerInput(BaseModel):
    trackingId: str = ""
    aircrafts: list = Field(min_length=1)
    employees: list = Field(min_length=1)
    matrixConfigs: dict
    config: SchedulerConfig = SchedulerConfig()
    hubs: list = Field(default_factory=list)


def _run_solver(job_id: str, data: dict, algorithm: str, time_limit: int):
    import importlib

    original_path = sys.path.copy()
    if ALGO_ROOT not in sys.path:
        sys.path.insert(0, ALGO_ROOT)

    try:
        context_mod = importlib.import_module("src.model.context")
        time_mod = importlib.import_module("src.model.time")
        Context = context_mod.Context
        parse_time = time_mod.parse_time

        algo = algorithm.lower()
        if algo == "lns":
            adapter_mod = importlib.import_module("src.strategy.optimization.adapter")
            strategy = adapter_mod.OptimizationEngineAdapter()
        elif algo == "greedy":
            greedy_mod = importlib.import_module("src.strategy.greedyStrategy.greedy_strategy")
            strategy = greedy_mod.GreedyStrategy()
        else:
            or_mod = importlib.import_module("src.strategy.orStrategy.orStrategy")
            strategy = or_mod.OrStrategy(time_limit)
    finally:
        sys.path = original_path

    from src.database import SessionLocal as BackendSessionLocal
    db = BackendSessionLocal()
    try:
        job = db.query(models.ScheduleJob).filter(models.ScheduleJob.job_id == job_id).first()
        if job:
            job.status = "RUNNING"
            db.commit()

        ctx = Context.from_dict(data)
        strategy.init(ctx)
        solution = strategy.execute()

        scheduled_tasks = []
        if solution:
            for emp in solution.employees:
                for assign in emp.assignments:
                    duration_min = (parse_time(assign.endTime) - parse_time(assign.startTime)) // 60
                    scheduled_tasks.append({
                        "taskId": f"{assign.taskCode}-{assign.aircraftId}",
                        "taskCode": assign.taskCode,
                        "aircraftId": assign.aircraftId,
                        "employeeId": emp.employeeId,
                        "employeeName": f"Emp {emp.employeeId}",
                        "startTime": assign.startTime,
                        "endTime": assign.endTime,
                        "duration": duration_min,
                        "type": "TASK",
                    })

                for brk in emp.breakTimes:
                    duration_min = (parse_time(brk.endTime) - parse_time(brk.startTime)) // 60
                    scheduled_tasks.append({
                        "taskId": f"break-{emp.employeeId}",
                        "taskCode": "BREAK",
                        "aircraftId": "",
                        "employeeId": emp.employeeId,
                        "employeeName": f"Emp {emp.employeeId}",
                        "startTime": brk.startTime,
                        "endTime": brk.endTime,
                        "duration": duration_min,
                        "type": "BREAK",
                    })

                sorted_assigns = sorted(emp.assignments, key=lambda a: parse_time(a.startTime))
                for i in range(len(sorted_assigns) - 1):
                    current = sorted_assigns[i]
                    next_task = sorted_assigns[i + 1]
                    if current.locationId != next_task.locationId:
                        duration = (parse_time(next_task.startTime) - parse_time(current.endTime)) // 60
                        if duration > 0:
                            scheduled_tasks.append({
                                "taskId": f"travel-{emp.employeeId}-{i}",
                                "taskCode": "TRAVEL",
                                "aircraftId": "",
                                "employeeId": emp.employeeId,
                                "employeeName": f"Emp {emp.employeeId}",
                                "startTime": current.endTime,
                                "endTime": next_task.startTime,
                                "duration": duration,
                                "type": "TRAVEL",
                            })

            result_dict = {
                "status": "OPTIMAL" if not solution.droppedTasks else "FEASIBLE",
                "message": f"Solved using {algorithm.upper()}. Dropped: {len(solution.droppedTasks)} tasks.",
                "scheduledTasks": scheduled_tasks,
                "totalCost": 0,
                "solveTimeMs": 0,
            }
        else:
            result_dict = {
                "status": "FAILED",
                "message": "No solution found",
                "scheduledTasks": [],
                "totalCost": 0,
                "solveTimeMs": 0,
            }

        job = db.query(models.ScheduleJob).filter(models.ScheduleJob.job_id == job_id).first()
        if job:
            job.status = "COMPLETED"
            job.result_json = json.dumps(result_dict)
            db.commit()

    except Exception as e:
        logger.error(f"Solver error for job {job_id}: {e}", exc_info=True)
        try:
            db.rollback()
            job = db.query(models.ScheduleJob).filter(models.ScheduleJob.job_id == job_id).first()
            if job:
                job.status = "FAILED"
                job.error_message = str(e)
                job.result_json = json.dumps({
                    "status": "FAILED",
                    "message": str(e),
                    "scheduledTasks": [],
                    "totalCost": 0,
                    "solveTimeMs": 0,
                })
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@router.post("/run")
async def run_scheduler(data: dict, db: Session = Depends(get_db)):
    config = data.get("config", {})
    algorithm = config.get("algorithm", "cpsat").lower()
    time_limit = int(config.get("timeLimit", 30))

    tracking_id = data.get("trackingId")
    if not tracking_id:
        tracking_id = f"REQ-{int(time.time())}"
        data["trackingId"] = tracking_id

    job = models.ScheduleJob(job_id=tracking_id, status="PENDING")
    db.add(job)
    db.commit()

    from app.services.solver_service import solver_executor
    solver_executor.submit(_run_solver, tracking_id, data, algorithm, time_limit)

    return {
        "job_id": tracking_id,
        "status": "PENDING",
        "message": f"Job submitted with {algorithm.upper()}",
    }


@router.get("/status/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(models.ScheduleJob).filter(models.ScheduleJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == "COMPLETED":
        result = json.loads(job.result_json) if job.result_json else {}
        return result
    elif job.status == "FAILED":
        result = json.loads(job.result_json) if job.result_json else {
            "status": "FAILED",
            "message": job.error_message or "Unknown Error",
            "scheduledTasks": [],
            "totalCost": 0,
            "solveTimeMs": 0,
        }
        return result
    else:
        return {
            "status": job.status,
            "message": "Algorithm is processing the schedule...",
            "scheduledTasks": [],
            "totalCost": 0,
            "solveTimeMs": 0,
        }


@router.get("/algorithms")
async def get_algorithms():
    return {
        "algorithms": [
            {"id": "cpsat", "name": "Google OR-Tools (CP-SAT)", "description": "Constraint Programming solver"},
            {"id": "lns", "name": "LNS + CP-SAT", "description": "Large Neighborhood Search with CP-SAT repair"},
            {"id": "greedy", "name": "Greedy Heuristic", "description": "Fast heuristic solution"},
        ],
        "optimizeOptions": [
            {"id": "makespan", "name": "Minimize Makespan"},
            {"id": "cost", "name": "Minimize Cost"},
            {"id": "balance", "name": "Load Balance"},
        ],
        "defaultTimeLimit": 60,
    }
