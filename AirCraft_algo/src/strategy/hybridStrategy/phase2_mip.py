from src.utils.logger import get_logger
logger = get_logger("src.strategy.hybridStrategy.phase2_mip")
"""
Phase 2: MIP Time Optimization

Given fixed task-employee assignments from Phase 1,
optimizes start times to minimize makespan and overtime.
"""
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
from ortools.linear_solver import pywraplp


# Weight constants (same as main solver)
WEIGHT_MAKESPAN = 1
WEIGHT_OVERTIME = 100
WEIGHT_LEVEL = 10


class Phase2Mip:
    """
    Phase 2 of Hybrid Strategy: MIP for time optimization.
    
    Input: Fixed assignments from Phase 1
    Objective: Minimize makespan + overtime + level penalty
    """
    
    def __init__(self, data: Dict[str, Any], variables: Dict):
        self.data = data
        self.variables = variables
        self.solver = None
        
        # MIP variables
        self.start_vars = {}
        self.overtime_vars = {}
        self.order_vars = {}
        self.makespan_var = None
        
    def solve(self, assignments: List[Tuple[int, int]], 
              time_limit_seconds: int = 30) -> Tuple[bool, Dict[int, int]]:
        """
        Run Phase 2 MIP solver.
        
        Args:
            assignments: List of (task_idx, employee_idx) from Phase 1
            time_limit_seconds: Solver time limit
            
        Returns:
            Tuple of:
            - success: True if optimal/feasible solution found
            - start_times: Dict mapping task_idx -> start_time
        """
        # Create MIP solver
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        if not self.solver:
            # Fallback to CBC if SCIP not available
            self.solver = pywraplp.Solver.CreateSolver('CBC')
        
        if not self.solver:
            logger.info("[Phase2MIP] Warning: No MIP solver available")
            return False, {}
        
        if time_limit_seconds > 0:
            self.solver.SetTimeLimit(time_limit_seconds * 1000)  # milliseconds
        
        # Create variables
        self._create_variables(assignments)
        
        # Create constraints
        self._create_precedence_constraints(assignments)
        self._create_travel_constraints(assignments)
        self._create_no_overlap_constraints(assignments)
        
        # Create objective
        self._create_objective(assignments)
        
        # Solve
        status = self.solver.Solve()
        
        if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            start_times = {
                t_idx: int(self.start_vars[t_idx].solution_value())
                for t_idx in self.start_vars
            }
            return True, start_times
        else:
            return False, {}
    
    def _create_variables(self, assignments: List[Tuple[int, int]]):
        """Create MIP variables for start times and overtime."""
        max_time = self.data['max_time']
        
        for t_idx, e_idx in assignments:
            task_var = self.variables['tasks'][t_idx]
            task = task_var['task']
            _, duration, _ = task_var['assigned_vars'][e_idx]
            
            # Start time variable
            # Must fit within window: start + duration <= window_end
            max_start = task.window_end - duration
            self.start_vars[t_idx] = self.solver.IntVar(
                task.window_start,
                max(task.window_start, max_start),
                f'start_{t_idx}'
            )
            
            # Overtime variable
            emp = self.data['employees'][e_idx]
            self.overtime_vars[t_idx] = self.solver.IntVar(
                0, max_time, f'overtime_{t_idx}'
            )
            
            # Overtime >= end - work_end
            end_time_expr = self.start_vars[t_idx] + duration
            self.solver.Add(
                self.overtime_vars[t_idx] >= end_time_expr - emp.work_end
            )
        
        # Makespan variable
        self.makespan_var = self.solver.IntVar(0, max_time, 'makespan')
        
        for t_idx, e_idx in assignments:
            task_var = self.variables['tasks'][t_idx]
            _, duration, _ = task_var['assigned_vars'][e_idx]
            self.solver.Add(
                self.makespan_var >= self.start_vars[t_idx] + duration
            )
    
    def _create_precedence_constraints(self, assignments: List[Tuple[int, int]]):
        """Create precedence constraints between dependent tasks."""
        assigned_tasks = {t_idx for t_idx, _ in assignments}
        
        for t_idx, e_idx in assignments:
            task_var = self.variables['tasks'][t_idx]
            task = task_var['task']
            
            for dep_code in task.dependencies:
                pred_id = f"{task.aircraft_id}_{dep_code}"
                
                # Find predecessor task index
                for pred_idx, pred_var in enumerate(self.variables['tasks']):
                    if pred_var['task'].id == pred_id and pred_idx in assigned_tasks:
                        # Find predecessor's assigned employee
                        pred_e_idx = next(
                            (e for t, e in assignments if t == pred_idx),
                            None
                        )
                        if pred_e_idx is not None:
                            _, pred_duration, _ = pred_var['assigned_vars'][pred_e_idx]
                            # Start >= End of predecessor
                            self.solver.Add(
                                self.start_vars[t_idx] >= 
                                self.start_vars[pred_idx] + pred_duration
                            )
                        break
    
    def _create_travel_constraints(self, assignments: List[Tuple[int, int]]):
        """Create travel time constraints for tasks assigned to same employee."""
        # Group tasks by employee
        employee_tasks = defaultdict(list)
        for t_idx, e_idx in assignments:
            employee_tasks[e_idx].append(t_idx)
        
        max_time = self.data['max_time']
        
        for e_idx, task_indices in employee_tasks.items():
            if len(task_indices) < 2:
                continue
            
            # Create pairwise constraints
            for i, t1_idx in enumerate(task_indices):
                for t2_idx in task_indices[i+1:]:
                    task1 = self.variables['tasks'][t1_idx]['task']
                    task2 = self.variables['tasks'][t2_idx]['task']
                    
                    loc1 = task1.location
                    loc2 = task2.location
                    
                    if loc1 == loc2:
                        continue
                    
                    # Get travel time
                    travel_time = self.data['travel_times'].get((loc1, loc2), 300)
                    
                    # Get durations
                    _, dur1, _ = self.variables['tasks'][t1_idx]['assigned_vars'][e_idx]
                    _, dur2, _ = self.variables['tasks'][t2_idx]['assigned_vars'][e_idx]
                    
                    # Check if order is fixed by time windows
                    if task1.window_end + travel_time < task2.window_start:
                        # t1 -> t2 is forced
                        self.solver.Add(
                            self.start_vars[t2_idx] >= 
                            self.start_vars[t1_idx] + dur1 + travel_time
                        )
                    elif task2.window_end + travel_time < task1.window_start:
                        # t2 -> t1 is forced
                        self.solver.Add(
                            self.start_vars[t1_idx] >= 
                            self.start_vars[t2_idx] + dur2 + travel_time
                        )
                    else:
                        # Need order variable (Big-M formulation)
                        order_key = (e_idx, t1_idx, t2_idx)
                        order_var = self.solver.BoolVar(f'order_{e_idx}_{t1_idx}_{t2_idx}')
                        self.order_vars[order_key] = order_var
                        
                        M = max_time + travel_time + max(dur1, dur2)
                        
                        # If order = 1: t1 -> t2
                        self.solver.Add(
                            self.start_vars[t2_idx] >= 
                            self.start_vars[t1_idx] + dur1 + travel_time - M * (1 - order_var)
                        )
                        
                        # If order = 0: t2 -> t1
                        self.solver.Add(
                            self.start_vars[t1_idx] >= 
                            self.start_vars[t2_idx] + dur2 + travel_time - M * order_var
                        )
    
    def _create_no_overlap_constraints(self, assignments: List[Tuple[int, int]]):
        """Ensure tasks assigned to same employee don't overlap."""
        # Group tasks by employee
        employee_tasks = defaultdict(list)
        for t_idx, e_idx in assignments:
            employee_tasks[e_idx].append(t_idx)
        
        max_time = self.data['max_time']
        
        for e_idx, task_indices in employee_tasks.items():
            if len(task_indices) < 2:
                continue
            
            for i, t1_idx in enumerate(task_indices):
                for t2_idx in task_indices[i+1:]:
                    task1 = self.variables['tasks'][t1_idx]['task']
                    task2 = self.variables['tasks'][t2_idx]['task']
                    
                    # Skip if already handled by travel constraints for different locations
                    if task1.location != task2.location:
                        continue
                    
                    # Same location - simple no overlap
                    _, dur1, _ = self.variables['tasks'][t1_idx]['assigned_vars'][e_idx]
                    _, dur2, _ = self.variables['tasks'][t2_idx]['assigned_vars'][e_idx]
                    
                    # Check if order is fixed
                    if task1.window_end < task2.window_start:
                        self.solver.Add(
                            self.start_vars[t2_idx] >= 
                            self.start_vars[t1_idx] + dur1
                        )
                    elif task2.window_end < task1.window_start:
                        self.solver.Add(
                            self.start_vars[t1_idx] >= 
                            self.start_vars[t2_idx] + dur2
                        )
                    else:
                        # Need order variable
                        order_key = (e_idx, t1_idx, t2_idx)
                        if order_key in self.order_vars:
                            continue  # Already created
                        
                        order_var = self.solver.BoolVar(f'order_same_{e_idx}_{t1_idx}_{t2_idx}')
                        self.order_vars[order_key] = order_var
                        
                        M = max_time + max(dur1, dur2)
                        
                        self.solver.Add(
                            self.start_vars[t2_idx] >= 
                            self.start_vars[t1_idx] + dur1 - M * (1 - order_var)
                        )
                        self.solver.Add(
                            self.start_vars[t1_idx] >= 
                            self.start_vars[t2_idx] + dur2 - M * order_var
                        )
    
    def _create_objective(self, assignments: List[Tuple[int, int]]):
        """Create objective function."""
        # Level penalty (constant from Phase 1)
        level_penalty = 0
        for t_idx, e_idx in assignments:
            _, _, level_diff = self.variables['tasks'][t_idx]['assigned_vars'][e_idx]
            level_penalty += level_diff
        
        # Objective: minimize weighted sum
        objective = (
            WEIGHT_MAKESPAN * self.makespan_var +
            WEIGHT_OVERTIME * sum(self.overtime_vars.values()) +
            WEIGHT_LEVEL * level_penalty
        )
        
        self.solver.Minimize(objective)
    
    def get_objective_value(self) -> Optional[float]:
        """Get objective value from solved model."""
        if self.solver and self.solver.Objective():
            return self.solver.Objective().Value()
        return None
