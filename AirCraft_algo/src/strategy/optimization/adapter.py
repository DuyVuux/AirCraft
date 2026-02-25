from src.utils.logger import get_logger
logger = get_logger("src.strategy.optimization.adapter")
from typing import Optional
from src.strategy.base import IStrategy
from src.model.solution import Solution, EmployeeSolution, DroppedAircraft, DroppedTask
from src.strategy.optimization.context_builder import ContextBuilder
from src.strategy.optimization.solver import LNSSolver
from src.model.time import timestamp_to_iso

class OptimizationEngineAdapter(IStrategy):
    """
    Adapter implementing the Strategy Interface.
    Uses the Hexagonal Optimization Engine (ContextBuilder -> Models -> Solver).
    """
    
    def __init__(self, **solver_args):
        super().__init__()
        self.solver_args = solver_args

    def execute(self) -> Solution:
        if not self.context:
            raise ValueError("Context not initialized")
        
        # 1. Build Optimization Context
        logger.info("[Adapter] Building Context...")
        builder = ContextBuilder()
        opt_ctx = builder.build(self.context)
        logger.info(f"[Adapter] Context Built. {len(opt_ctx.tasks)} tasks, {len(opt_ctx.employees)} employees.")
        
        # 2. Run Solver
        logger.info("[Adapter] Running Solver...")
        # Default defaults
        final_args = {'time_limit_seconds': 10}
        final_args.update(self.solver_args)
        
        solver = LNSSolver(**final_args)
        final_state = solver.solve(opt_ctx)
        
        # 3. Map back to Solution
        logger.info("[Adapter] Converting Solution...")
        solution = Solution.empty()
        
        # Initialize Employee Solutions
        emp_map = {} # emp_id -> EmployeeSolution
        for emp in self.context.employees:
            # Reconstruct employee details
            # Base strategy usually doesn't modify context, but solution needs details.
            # Using context.employees is clearer.
            emp_sol = solution.add_employee(
                employee_id=emp.employeeId,
                certificates=emp.certifications # + role certs? 
            )
            emp_map[emp.employeeId] = emp_sol
            
        # Fill Assignments
        # Build reverse location map
        idx_to_loc = {v: k for k, v in opt_ctx.location_to_idx.items()}
        
        # Fill Assignments
        for task_id, emp_id_idx in final_state.assignments.items():
            # Get IDs
            # Emp ID is stored as INT in model
            # We need to map back using opt_ctx.employees[idx].original_id
            emp_original_id = opt_ctx.employees[emp_id_idx].original_id
            
            # Task info
            # task_map: id -> (aircraft_id, task_code)
            aircraft_id, task_code = opt_ctx.task_map[task_id]
            task_obj = opt_ctx.tasks[task_id]
            
            # Time: stored as int keys
            start_ts = final_state.start_times[task_id]
            # Lookup specific duration based on assigned employee's level
            emp_level = opt_ctx.employees[emp_id_idx].level
            dur = opt_ctx.task_level_durations.get((task_id, emp_level), task_obj.duration)
            end_ts = start_ts + dur
            
            # Location ID
            # Map back? 
            # We have location_idx, need dict?
            # opt_ctx.location_to_idx is 'str -> int'.
            # We need 'int -> str'.
            # ContextBuilder doesn't expose idx_to_location publicly in dataclass (checked).
            # Wait, OptimizationContext HAS location_to_idx. 
            # We can reverse it easily.
            loc_id = idx_to_loc[task_obj.location_idx]
            
            # Certificates
            # task_obj.required_certs is [int]
            req_certs = [opt_ctx.idx_to_cert[c] for c in task_obj.required_certs]
            
            solution.assign_task(
                employee_id=emp_original_id,
                task_code=task_code,
                aircraft_id=aircraft_id,
                required_certificates=req_certs,
                location_id=loc_id,
                start_time=timestamp_to_iso(start_ts),
                end_time=timestamp_to_iso(end_ts)
            )
            
        # Fill Dropped Tasks
        for task_id in final_state.dropped_tasks:
            aircraft_id, task_code = opt_ctx.task_map[task_id]
            task_obj = opt_ctx.tasks[task_id]
            req_certs = [opt_ctx.idx_to_cert[c] for c in task_obj.required_certs]
            
            loc_id = idx_to_loc.get(task_obj.location_idx)
            
            solution.drop_task(
                aircraft_id=aircraft_id,
                task_code=task_code,
                required_certificates=req_certs,
                location_id=loc_id,
                required_level=task_obj.min_level,
                start_time=timestamp_to_iso(task_obj.earliest_start),
                end_time=timestamp_to_iso(task_obj.latest_finish)
            )
            
        return solution
