import traceback
import os
import time
import logging
import json
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Optional

from src.service.registry import get_api_handler
from src.model.context import Context
from src.model.solution import Solution
from src.utils.input_describer import generate_input_description
from src.utils.output_describer import generate_solution_summary
from src.app.database import SessionLocal, ScheduleJob

logging.basicConfig(level=logging.ERROR)

from src.strategy.optimization.adapter import OptimizationEngineAdapter
from src.strategy.greedyStrategy.greedy_strategy import GreedyStrategy
from src.strategy.orStrategy.orStrategy import OrStrategy

import src.service.nbp_client  # noqa: F401
import src.service.greedy_client  # noqa: F401
from src.model.time import parse_time
from src.utils.logger import get_logger
logger = get_logger("src.app.routes")

executor = ThreadPoolExecutor(max_workers=4)

api = Blueprint('api', __name__, url_prefix='/api')

APP_ENV = os.getenv("APP_ENV", "development").lower()

_api_key = os.getenv("API_KEY")
if APP_ENV == "production" and not _api_key:
    raise RuntimeError("API_KEY must be set in production environment")
elif not _api_key:
    logging.warning("API_KEY not set — running in development mode without API key enforcement")


class TaskItem(BaseModel):
    taskCode: str
    aircraftId: str
    requiredCertificates: list[str] = Field(default_factory=list)
    duration: Optional[int] = None


class AircraftItem(BaseModel):
    aircraftId: str
    location: Optional[str] = None
    timeWindow: Optional[dict] = None
    requiredTasks: list[TaskItem] = Field(min_length=1)


class EmployeeItem(BaseModel):
    employeeId: str
    certificates: list[str] = Field(default_factory=list)


class MatrixConfigs(BaseModel):
    distanceMatrix: dict | list
    timeMatrix: dict | list


class SchedulerConfig(BaseModel):
    algorithm: str = "cpsat"
    timeLimit: int = 30


class SchedulerInput(BaseModel):
    aircrafts: list[AircraftItem] = Field(min_length=1)
    employees: list[EmployeeItem] = Field(min_length=1)
    matrixConfigs: MatrixConfigs
    config: SchedulerConfig = Field(default_factory=SchedulerConfig)
    trackingId: Optional[str] = None

    @field_validator("aircrafts", "employees", mode="before")
    @classmethod
    def check_max_depth(cls, v):
        _check_depth(v, max_depth=10)
        return v


def _check_depth(obj, max_depth=10, current=0):
    if current > max_depth:
        raise ValueError(f"Object nesting exceeds maximum depth of {max_depth}")
    if isinstance(obj, dict):
        for v in obj.values():
            _check_depth(v, max_depth, current + 1)
    elif isinstance(obj, list):
        for item in obj:
            _check_depth(item, max_depth, current + 1)


MAX_PAYLOAD_BYTES = 10 * 1024 * 1024


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if APP_ENV == "development" and not _api_key:
            return f(*args, **kwargs)

        provided_key = request.headers.get("X-API-Key")

        if not provided_key:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                provided_key = auth_header.split(" ")[1]

        if not provided_key or provided_key != _api_key:
            return jsonify({"error": "Invalid or missing API Key"}), 401

        return f(*args, **kwargs)
    return decorated_function


def process_solver_job(job_id, data, strategy):
    db = SessionLocal()
    try:
        job = db.query(ScheduleJob).filter(ScheduleJob.job_id == job_id).first()
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
                        "type": "TASK"
                    })

                for brk in emp.breakTimes:
                    duration_min = (parse_time(brk.endTime) - parse_time(brk.startTime)) // 60
                    scheduled_tasks.append({
                        "taskId": f"BREAK-{emp.employeeId}-{brk.startTime}",
                        "taskCode": "BREAK",
                        "aircraftId": "",
                        "employeeId": emp.employeeId,
                        "employeeName": f"Emp {emp.employeeId}",
                        "startTime": brk.startTime,
                        "endTime": brk.endTime,
                        "duration": duration_min,
                        "type": "BREAK"
                    })

                sorted_assigns = sorted(emp.assignments, key=lambda x: parse_time(x.startTime))
                for i in range(len(sorted_assigns) - 1):
                    current = sorted_assigns[i]
                    next_task = sorted_assigns[i + 1]

                    t_end = parse_time(current.endTime)
                    t_next_start = parse_time(next_task.startTime)

                    if t_next_start > t_end:
                        duration = (t_next_start - t_end) // 60
                        if duration > 0:
                            travel_type = "BUS" if duration > 15 else "WALK"
                            scheduled_tasks.append({
                                "taskId": f"TRAVEL-{emp.employeeId}-{current.endTime}",
                                "taskCode": travel_type,
                                "aircraftId": "",
                                "employeeId": emp.employeeId,
                                "employeeName": f"Emp {emp.employeeId}",
                                "startTime": current.endTime,
                                "endTime": next_task.startTime,
                                "duration": duration,
                                "type": travel_type
                            })

            algorithm = data.get('config', {}).get('algorithm', 'cpsat').upper()
            result_dict = {
                "status": "OPTIMAL" if not solution.droppedTasks else "FEASIBLE",
                "message": f"Solved using {algorithm}. Dropped: {len(solution.droppedTasks)} tasks.",
                "scheduledTasks": scheduled_tasks,
                "totalCost": 0,
                "solveTimeMs": 0
            }
        else:
            result_dict = {
                "status": "FAILED",
                "message": "No solution found",
                "scheduledTasks": [],
                "totalCost": 0,
                "solveTimeMs": 0
            }

        job = db.query(ScheduleJob).filter(ScheduleJob.job_id == job_id).first()
        if job:
            job.status = "COMPLETED"
            job.result_json = json.dumps(result_dict)
            job.error_message = None
            db.commit()

    except Exception as e:
        logging.error(f"Error in process_solver_job {job_id}: {e}", exc_info=True)
        try:
            db.rollback()
            job = db.query(ScheduleJob).filter(ScheduleJob.job_id == job_id).first()
            if job:
                job.status = "FAILED"
                job.error_message = str(e)
                job.result_json = json.dumps({
                    "status": "FAILED",
                    "message": "Algorithm calculation failed due to an internal error.",
                    "scheduledTasks": [],
                    "totalCost": 0,
                    "solveTimeMs": 0
                })
                db.commit()
        except Exception as db_err:
            logging.error(f"Failed to update error to DB for job {job_id}: {db_err}")
    finally:
        db.close()


@api.route('/scheduler/run', methods=['POST'])
@require_api_key
def run_scheduler():
    try:
        content_length = request.content_length or 0
        if content_length > MAX_PAYLOAD_BYTES:
            return jsonify({"error": f"Payload too large. Max: {MAX_PAYLOAD_BYTES // (1024*1024)}MB"}), 413

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload"}), 400

        try:
            validated = SchedulerInput(**data)
        except ValidationError as ve:
            return jsonify({"error": "Validation failed", "details": ve.errors()}), 422

        config = data.get('config', {})
        algorithm = config.get('algorithm', 'cpsat').lower()

        if algorithm == 'lns':
            strategy = OptimizationEngineAdapter()
        elif algorithm == 'greedy':
            strategy = GreedyStrategy()
        else:
            time_limit = int(config.get('timeLimit', 30))
            strategy = OrStrategy(time_limit)

        tracking_id = data.get('trackingId')
        if not tracking_id:
            tracking_id = f"REQ-{int(time.time())}"
            data['trackingId'] = tracking_id

        db = SessionLocal()
        try:
            job = ScheduleJob(job_id=tracking_id, status="PENDING")
            db.add(job)
            db.commit()
        except Exception as e:
            db.rollback()
            logging.error(f"DB Error creating tracking_id {tracking_id}: {e}")
            return jsonify({"error": "Failed to create tracking record."}), 500
        finally:
            db.close()

        executor.submit(process_solver_job, tracking_id, data, strategy)

        return jsonify({
            "job_id": tracking_id,
            "status": "RUNNING",
            "message": f"Job submitted with {algorithm.upper()}"
        }), 200

    except Exception as e:
        logging.error(f"Error in run_scheduler: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500


@api.route('/scheduler/status/<job_id>', methods=['GET'])
@require_api_key
def get_job_status(job_id):
    db = SessionLocal()
    try:
        job = db.query(ScheduleJob).filter(ScheduleJob.job_id == job_id).first()
        if not job:
            return jsonify({"error": "Job not found"}), 404

        if job.status == 'COMPLETED':
            result_dict = json.loads(job.result_json) if job.result_json else {}
            return jsonify(result_dict), 200
        elif job.status == 'FAILED':
            result_dict = json.loads(job.result_json) if job.result_json else {
                "status": "FAILED",
                "message": job.error_message or "Unknown Error",
                "scheduledTasks": [],
                "totalCost": 0,
                "solveTimeMs": 0
            }
            return jsonify(result_dict), 200
        else:
            return jsonify({
                "status": "RUNNING",
                "message": "Algorithm is processing the schedule...",
                "scheduledTasks": [],
                "totalCost": 0,
                "solveTimeMs": 0
            }), 200
    except Exception as e:
        logging.error(f"Error fetching status for {job_id}: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500
    finally:
        db.close()


@api.route('/solver/<api_name>', methods=['POST'])
@require_api_key
def handle_api(api_name: str):
    try:
        try:
            handler = get_api_handler(api_name)
        except ValueError as e:
            return jsonify({"error": str(e)}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        try:
            tracking_id = data.get('trackingId', 'unknown')
            safe_tracking_id = os.path.basename(str(tracking_id))
            if not safe_tracking_id or safe_tracking_id in ('.', '..'):
                safe_tracking_id = 'unknown'

            ctx = Context.from_dict(data)
            tracking_dir = os.path.join('data', safe_tracking_id)
            os.makedirs(tracking_dir, exist_ok=True)
            desc_file = os.path.join(tracking_dir, 'input_description.md')
            generate_input_description(ctx, desc_file)
        except Exception as e:
            logging.warning(f"Failed to generate input description: {e}")

        result = handler.process(data)

        try:
            from src.model.solution import Solution, EmployeeSolution, TaskAssignment, TimeSlot, DroppedAircraft, DroppedTask

            solution_data = result.get('solution', [])
            dropped_data = result.get('droppedTasks', [])

            solution = Solution()

            for emp_data in solution_data:
                emp = solution.add_employee(emp_data['employeeId'], emp_data.get('certificates', []))
                for assign_data in emp_data.get('assignment', []):
                    task_info = assign_data['task']
                    emp.assignments.append(TaskAssignment(
                        taskCode=task_info['taskCode'],
                        aircraftId=task_info['aircraftId'],
                        requiredCertificates=task_info.get('requiredCertificates', []),
                        locationId=assign_data['locationId'],
                        startTime=assign_data['startTime'],
                        endTime=assign_data['endTime']
                    ))
                for break_data in emp_data.get('breakTimes', []):
                    emp.breakTimes.append(TimeSlot(
                        startTime=break_data['startTime'],
                        endTime=break_data['endTime']
                    ))

            for aircraft_data in dropped_data:
                aircraft = DroppedAircraft(aircraftId=aircraft_data['aircraftId'])
                for task_data in aircraft_data['tasks']:
                    aircraft.tasks.append(DroppedTask(
                        taskCode=task_data['taskCode'],
                        aircraftId=task_data['aircraftId'],
                        requiredCertificates=task_data.get('requiredCertificates', [])
                    ))
                solution.droppedTasks.append(aircraft)

            summary_file = os.path.join(tracking_dir, 'output_summary.md')
            generate_solution_summary(solution, summary_file)
        except Exception as e:
            logging.warning(f"Failed to generate solution summary: {e}")

        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error in handle_api: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred. Please check server logs or contact administrator."}), 500
