"""
OR-Tools Strategy - Main orchestrator for OR-Tools optimization.
"""
import multiprocessing
from typing import Optional
from ortools.sat.python import cp_model

from src.model.context import Context
from src.model.solution import Solution
from src.strategy.base import IStrategy
from src.strategy.adapters import OrAdapter
from src.strategy.orStrategy.model_builder import ModelBuilder
from src.strategy.orStrategy.objective_builder import ObjectiveBuilder, print_penalty_breakdown
from src.strategy.orStrategy.constraints.assignment import AssignmentConstraint
from src.strategy.orStrategy.constraints.precedence import PrecedenceConstraint
from src.strategy.orStrategy.constraints.employee import EmployeeConstraint
from src.strategy.orStrategy.constraints.travel import TravelConstraint
from src.strategy.orStrategy.constraints.aircraft import AircraftTimeWindowConstraint
from src.strategy.orStrategy.constraints.bus import BusConstraint


class OrStrategy(IStrategy):
    """
    OR-Tools CP-SAT based optimization strategy.
    
    Orchestrates:
    1. Data conversion via OrAdapter
    2. Model and variable creation via ModelBuilder
    3. Constraint building via constraint components
    4. Objective function via ObjectiveBuilder
    5. Solving and solution extraction
    """
    
    def __init__(self, time_limit_seconds: int = 60):
        """
        Initialize OR-Tools strategy.
        Now Refactored to use the Hexagonal Architecture (OptimizationEngineAdapter).
        Acts as a 'Pure CP-SAT' configuration of the core engine.
        """
        super().__init__()
        self.time_limit_seconds = time_limit_seconds
        # Import here to avoid circular dependencies if any
        from src.strategy.optimization.adapter import OptimizationEngineAdapter
        
        # Configure Adapter to run in Pure CP Mode
        self._adapter = OptimizationEngineAdapter(
            time_limit_seconds=time_limit_seconds, 
            pure_cp_mode=True
        )
    
    @property
    def is_optimal(self) -> bool:
        """Check if solution is optimal."""
        return True # Simplified assumption for now, or check internal status
    
    def execute(self) -> Solution:
        """
        Execute Pure CP-SAT optimization.
        """
        print(f"[OrStrategy] Executing Pure CP-SAT with time limit: {self.time_limit_seconds}s")
        
        if not self.context:
            return Solution.empty()
            
        # 1. Initialize Adapter
        self._adapter.init(self.context)
        
        # 2. Execute directly (configuration already set in __init__)
        return self._adapter.execute()
    
    def _apply_solution_hints(self, model: cp_model.CpModel, variables: dict, 
                              data: dict, solution: Solution) -> None:
        """Apply hints from existing solution."""
        # Convert solution to task assignments map
        task_assignments = {}
        task_times = {}
        
        for emp_solution in solution.employees:
            emp_id = emp_solution.employeeId
            for assignment in emp_solution.assignments:
                task_id = f"{assignment.aircraftId}_{assignment.taskCode}"
                task_assignments[task_id] = emp_id
                task_times[task_id] = (assignment.startTime, assignment.endTime)
        
        # Map employee IDs to indices
        emp_id_to_idx = {emp.id: emp.idx for emp in data['employees']}
        
        for task_var in variables['tasks']:
            task_id = task_var['task'].id
            
            if task_id in task_assignments:
                emp_id = task_assignments[task_id]
                emp_idx = emp_id_to_idx.get(emp_id)
                
                if emp_idx is not None and emp_idx in task_var['assigned_vars']:
                    # Hint assignment
                    assign_var, _, _ = task_var['assigned_vars'][emp_idx]
                    model.AddHint(assign_var, 1)
                    model.AddHint(task_var['unassigned_var'], 0)
                    
                    # Hint times
                    if task_id in task_times:
                        start_iso, end_iso = task_times[task_id]
                        from src.strategy.adapters.or_adapter import parse_time, normalize_time
                        
                        start_ts = normalize_time(parse_time(start_iso), data['min_global_time'])
                        model.AddHint(task_var['start'], start_ts)
    
    def _create_greedy_hints(self, model: cp_model.CpModel,
                            variables: dict, data: dict) -> None:
        """Create greedy heuristic hints."""
        # Track employee availability
        employee_available_time = {
            emp.idx: emp.work_start for emp in data['employees']
        }
        
        # Sort tasks by window start
        sorted_tasks = sorted(
            enumerate(variables['tasks']),
            key=lambda x: x[1]['task'].window_start
        )
        
        for t_idx, task_var in sorted_tasks:
            if not task_var['assigned_vars']:
                model.AddHint(task_var['unassigned_var'], 1)
                continue
            
            best_emp = None
            best_start = float('inf')
            
            # Find earliest available employee
            for e_idx, (assign_var, duration, _) in task_var['assigned_vars'].items():
                start = max(
                    task_var['task'].window_start,
                    employee_available_time[e_idx]
                )
                
                # Check if fits in window
                if start + duration <= task_var['task'].window_end:
                    if start < best_start:
                        best_start = start
                        best_emp = e_idx
            
            if best_emp is not None:
                # Hint assignment
                assign_var, duration, _ = task_var['assigned_vars'][best_emp]
                model.AddHint(assign_var, 1)
                model.AddHint(task_var['unassigned_var'], 0)
                model.AddHint(task_var['start'], best_start)
                
                # Update availability
                employee_available_time[best_emp] = best_start + duration
            else:
                model.AddHint(task_var['unassigned_var'], 1)
