"""
Model Builder - Create CP Model and decision variables for OR-Tools.
"""
from typing import Dict, Any, List, Tuple
from ortools.sat.python import cp_model


class ModelBuilder:
    """
    Build CP-SAT model and create decision variables.
    
    Responsible for:
    - Creating CpModel instance
    - Creating task variables (start, end, size, interval, unassigned)
    - Creating assignment variables (task-employee pairs)
    - Basic domain reduction (filter by constraints only)
    
    Note: No heuristic filtering (top_k, efficiency_threshold) to ensure global optimal.
    """
    
    def __init__(self):
        """Initialize model builder."""
        self.model = None
    
    def build(self, data: Dict[str, Any]) -> Tuple[cp_model.CpModel, Dict[str, Any]]:
        """
        Build CP model and create all decision variables.
        
        Args:
            data: Parsed context from OrAdapter
            
        Returns:
            (model, variables) where variables contains:
                - tasks: List of task variable dicts
                - Each task dict: {
                    'task': TaskData,
                    'start': IntVar,
                    'end': IntVar,
                    'size': IntVar,
                    'interval': IntervalVar,
                    'unassigned_var': BoolVar,
                    'assigned_vars': Dict[emp_idx, (BoolVar, duration, level_diff)]
                  }
        """
        self.model = cp_model.CpModel()
        
        tasks = data['tasks']
        employees = data['employees']
        task_durations = data['task_durations']
        max_time = data['max_time']
        
        task_vars = []
        
        # Create task variables
        for t_idx, task in enumerate(tasks):
            # Start can be anywhere in time horizon (constraints applied separately)
            start_var = self.model.NewIntVar(0, max_time, f'start_t{t_idx}')
            
            # End can be anywhere in time horizon
            end_var = self.model.NewIntVar(0, max_time, f'end_t{t_idx}')
            
            size_var = self.model.NewIntVar(0, max_time, f'size_t{t_idx}')
            
            interval_var = self.model.NewIntervalVar(
                start_var, size_var, end_var, f'interval_t{t_idx}'
            )
            unassigned_var = self.model.NewBoolVar(f'unassigned_t{t_idx}')
            
            task_var = {
                'task': task,
                'start': start_var,
                'end': end_var,
                'size': size_var,
                'interval': interval_var,
                'unassigned_var': unassigned_var,
                'assigned_vars': {}  # Will be populated below
            }
            task_vars.append(task_var)
        
        # Create assignment variables with basic domain reduction only
        # (No heuristic filtering - ensures global optimal)
        for t_idx, task_var in enumerate(task_vars):
            task = task_var['task']
            
            # Find eligible employees (basic domain reduction)
            for emp in employees:
                # Filter 1: Certificate requirement (constraint-based)
                if not all(cert in emp.certificates for cert in task.required_certificates):
                    continue  # Employee lacks required certificates
                
                # Filter 2: Role requirement (constraint-based) - Strict check from task definition
                if task.required_role and task.required_role not in emp.role:
                    continue
                
                # Filter 3: Duration lookup (find best match)
                dur_key = (task.task_code, task.aircraft_id)
                
                if dur_key not in task_durations:
                    continue
                
                # Find all valid duration entries for this employee
                valid_durations = []
                emp_certs = set(emp.certificates)
                
                # Iterate over all possible configurations for this task/aircraft
                for req_role, req_certs, duration in task_durations[dur_key]:
                    # Check 1: Role match (relaxed substring check)
                    # If task doesn't specify role, check if matrix role is compatible with emp
                    if req_role and req_role not in emp.role:
                        continue
                        
                    # Check 2: Certificates match (superset)
                    if emp_certs.issuperset(req_certs):
                        valid_durations.append(duration)
                
                if not valid_durations:
                    continue
                
                # Pick the best (fastest) duration
                duration = min(valid_durations)
                
                # Create assignment variable for this eligible employee
                assign_var = self.model.NewBoolVar(f'assign_t{t_idx}_e{emp.idx}')
                task_var['assigned_vars'][emp.idx] = (assign_var, duration, 0)  # 0 for compatibility
        
        variables = {
            'tasks': task_vars
        }
        
        return self.model, variables
