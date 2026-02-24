from src.utils.logger import get_logger
logger = get_logger("src.strategy.hybridStrategy.hybrid_strategy")
"""
Hybrid Strategy - Two-phase CP-SAT + MIP optimization.

Phase 1: CP-SAT finds feasible task-employee assignments
Phase 2: MIP optimizes start times for minimal makespan/overtime
"""
import time
from typing import Optional, List
from collections import defaultdict

from src.model.context import Context
from src.model.solution import Solution, TaskAssignment
from src.model.time import timestamp_to_iso
from src.strategy.base import IStrategy
from src.strategy.adapters import OrAdapter
from .phase1_cpsat import Phase1CpSat
from .phase2_mip import Phase2Mip


class HybridStrategy(IStrategy):
    """
    Hybrid CP-SAT + MIP optimization strategy.
    
    Two-phase approach:
    1. CP-SAT: Find feasible assignments (minimize unassigned)
    2. MIP: Optimize timing (minimize makespan + overtime)
    
    If Phase 2 fails, falls back to Phase 1 solution.
    """
    
    def __init__(self, time_limit_seconds: int = 60,
                 phase1_ratio: float = 0.8):
        """
        Initialize Hybrid strategy.
        
        Args:
            time_limit_seconds: Total solver time limit
            phase1_ratio: Fraction of time allocated to Phase 1
        """
        super().__init__()
        self.time_limit_seconds = time_limit_seconds
        self.phase1_ratio = phase1_ratio
        
        self.adapter = OrAdapter()
        
        # Metrics
        self.phase1_time = 0.0
        self.phase2_time = 0.0
        self.phase1_status = None
        self.phase2_status = None
        self.used_phase2 = False
    
    def execute(self) -> Solution:
        """
        Execute Hybrid optimization strategy.
        
        Returns:
            Optimized solution or empty solution if infeasible
        """
        # 1. Adapt input
        data = self.adapter.adapt_input(self.context)
        
        # Calculate time budgets (0 = unlimited)
        if self.time_limit_seconds > 0:
            phase1_limit = int(self.time_limit_seconds * self.phase1_ratio)
            phase2_limit = self.time_limit_seconds - phase1_limit
        else:
            # Unlimited: use 0 for both phases (no limit)
            phase1_limit = 0
            phase2_limit = 0
        
        # 2. Phase 1: CP-SAT for assignments
        logger.info(f"[HybridStrategy] Phase 1: CP-SAT (limit={phase1_limit}s)")
        phase1_start = time.time()
        
        phase1 = Phase1CpSat()
        success1, assignments, variables = phase1.solve(data, phase1_limit)
        
        self.phase1_time = time.time() - phase1_start
        self.phase1_status = "FEASIBLE" if success1 else "INFEASIBLE"
        
        logger.info(f"[HybridStrategy] Phase 1 completed: {self.phase1_status} in {self.phase1_time:.2f}s")
        logger.info(f"[HybridStrategy] Assigned: {len(assignments)}/{len(data['tasks'])} tasks")
        
        if not success1:
            logger.info("[HybridStrategy] Phase 1 failed, returning empty solution")
            return Solution.empty()
        
        # 3. Phase 2: MIP for time optimization
        logger.info(f"[HybridStrategy] Phase 2: MIP (limit={phase2_limit}s)")
        phase2_start = time.time()
        
        phase2 = Phase2Mip(data, variables)
        success2, start_times = phase2.solve(assignments, phase2_limit)
        
        self.phase2_time = time.time() - phase2_start
        self.phase2_status = "OPTIMAL" if success2 else "FALLBACK"
        self.used_phase2 = success2
        
        logger.info(f"[HybridStrategy] Phase 2 completed: {self.phase2_status} in {self.phase2_time:.2f}s")
        
        # 4. Build solution
        if success2:
            solution = self._build_solution_from_mip(
                data, variables, assignments, start_times
            )
        else:
            logger.info("[HybridStrategy] Phase 2 failed, using Phase 1 times")
            solution = self._build_solution_from_cpsat(
                data, variables, assignments, phase1
            )
        
        # Add unassigned tasks
        assigned_task_indices = {t_idx for t_idx, _ in assignments}
        for t_idx, task_var in enumerate(variables['tasks']):
            if t_idx not in assigned_task_indices:
                task = task_var['task']
                # TODO: Check if task has required_certificates, default to empty list if not.
                # Xử lý gán min_level vào required_level của drop_task
                req_certs = getattr(task, 'required_certificates', [])
                min_level = getattr(task, 'min_level', None)
                
                solution.drop_task(
                    aircraft_id=task.aircraft_id,
                    task_code=task.task_code,
                    required_certificates=req_certs,
                    required_level=min_level
                )
        
        # Print summary
        total_time = self.phase1_time + self.phase2_time
        logger.info(f"[HybridStrategy] Total time: {total_time:.2f}s")
        logger.info(f"[HybridStrategy] Used Phase 2: {self.used_phase2}")
        
        return solution
    
    def _build_solution_from_mip(self, data: dict, variables: dict,
                                  assignments: list, start_times: dict) -> Solution:
        """Build solution using MIP-optimized start times."""
        solution = Solution.empty()
        employee_assignments = defaultdict(list)
        
        for t_idx, e_idx in assignments:
            task_var = variables['tasks'][t_idx]
            task = task_var['task']
            emp = data['employees'][e_idx]
            _, duration, _ = task_var['assigned_vars'][e_idx]
            
            start_norm = start_times[t_idx]
            end_norm = start_norm + duration
            
            # Denormalize times
            start_ts = start_norm + data['min_global_time']
            end_ts = end_norm + data['min_global_time']
            
            employee_assignments[emp.id].append({
                'taskCode': task.task_code,
                'aircraftId': task.aircraft_id,
                'minLevel': task.min_level,
                'locationId': task.location,
                'startTime': timestamp_to_iso(start_ts),
                'endTime': timestamp_to_iso(end_ts)
            })
        
        # Build employee solutions
        for emp in data['employees']:
            emp_solution = solution.add_employee(emp.id, emp.level)
            
            if emp.id in employee_assignments:
                sorted_assignments = sorted(
                    employee_assignments[emp.id],
                    key=lambda x: x['startTime']
                )
                for asg in sorted_assignments:
                    emp_solution.assignments.append(TaskAssignment(**asg))
        
        return solution
    
    def _build_solution_from_cpsat(self, data: dict, variables: dict,
                                    assignments: list, phase1: Phase1CpSat) -> Solution:
        """Build solution using Phase 1 CP-SAT times."""
        solution = Solution.empty()
        employee_assignments = defaultdict(list)
        
        for t_idx, e_idx in assignments:
            task_var = variables['tasks'][t_idx]
            task = task_var['task']
            emp = data['employees'][e_idx]
            
            start_norm = phase1.get_start_time(t_idx)
            end_norm = phase1.get_end_time(t_idx)
            
            # Denormalize times
            start_ts = start_norm + data['min_global_time']
            end_ts = end_norm + data['min_global_time']
            
            employee_assignments[emp.id].append({
                'taskCode': task.task_code,
                'aircraftId': task.aircraft_id,
                'minLevel': task.min_level,
                'locationId': task.location,
                'startTime': timestamp_to_iso(start_ts),
                'endTime': timestamp_to_iso(end_ts)
            })
        
        # Build employee solutions
        for emp in data['employees']:
            emp_solution = solution.add_employee(emp.id, emp.level)
            
            if emp.id in employee_assignments:
                sorted_assignments = sorted(
                    employee_assignments[emp.id],
                    key=lambda x: x['startTime']
                )
                for asg in sorted_assignments:
                    emp_solution.assignments.append(TaskAssignment(**asg))
        
        return solution
    
    def get_metrics(self) -> dict:
        """Get solver metrics."""
        return {
            'phase1_time_s': round(self.phase1_time, 3),
            'phase2_time_s': round(self.phase2_time, 3),
            'total_time_s': round(self.phase1_time + self.phase2_time, 3),
            'phase1_status': self.phase1_status,
            'phase2_status': self.phase2_status,
            'used_phase2': self.used_phase2,
            'is_optimal': self.is_optimal
        }
    
    @property
    def is_optimal(self) -> bool:
        """Check if solution is optimal (Phase 2 succeeded with OPTIMAL)."""
        return self.phase2_status == "OPTIMAL"
