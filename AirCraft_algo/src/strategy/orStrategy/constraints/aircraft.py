"""
Aircraft Time Window Constraint - Tasks must respect aircraft availability.
"""
from .base import ConstraintBuilder
from typing import Dict, Any, List, Tuple


class AircraftTimeWindowConstraint(ConstraintBuilder):
    """
    Enforce aircraft time window constraints.
    
    Constraints:
    - Task start >= aircraft arrival time (window_start) - HARD
    - Task end <= aircraft departure time (window_end) - SOFT (penalty)
    """
    
    def build(self, data: Dict[str, Any], variables: Dict[str, Any]):
        """Build all aircraft time window constraints."""
        self._build_start_constraint(variables)
        self._build_tardiness_slack(data, variables)
    
    def _build_start_constraint(self, variables: Dict[str, Any]):
        """
        HARD: Task cannot start before aircraft arrives.
        
        Constraint: start >= window_start (when assigned)
        """
        task_vars = variables['tasks']
        
        for tv in task_vars:
            task = tv['task']
            start_var = tv['start']
            unassigned_var = tv['unassigned_var']
            
            self.model.Add(
                start_var >= task.window_start
            ).OnlyEnforceIf(unassigned_var.Not())
    
    def _build_tardiness_slack(self, data: Dict[str, Any], variables: Dict[str, Any]):
        """
        SOFT: Create slack variable for tardiness penalty.
        
        tardiness = max(0, end - window_end) when assigned
        Stored in variables['tardiness_vars'] for ObjectiveBuilder.
        """
        task_vars = variables['tasks']
        max_time = data['max_time']
        
        tardiness_vars: List[Tuple] = []
        
        for t_idx, tv in enumerate(task_vars):
            task = tv['task']
            end_var = tv['end']
            unassigned_var = tv['unassigned_var']
            
            tard_var = self.model.NewIntVar(0, max_time, f'tard_t{t_idx}')
            
            # tardiness >= end - window_end (when assigned)
            self.model.Add(
                tard_var >= end_var - task.window_end
            ).OnlyEnforceIf(unassigned_var.Not())
            
            # tardiness >= 0 always
            self.model.Add(tard_var >= 0)
            
            # tardiness = 0 when unassigned
            self.model.Add(tard_var == 0).OnlyEnforceIf(unassigned_var)
            
            tardiness_vars.append((
                tard_var,
                f"{task.task_code}@{task.aircraft_id}",
                task.window_end,
                end_var
            ))
        
        variables['tardiness_vars'] = tardiness_vars
