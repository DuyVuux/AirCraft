"""
Assignment Constraints - Ensure each task is assigned to exactly one employee or unassigned.
"""
from typing import Dict, Any
from ortools.sat.python import cp_model
from src.strategy.orStrategy.constraints.base import ConstraintBuilder


class AssignmentConstraint(ConstraintBuilder):
    """
    Build assignment constraints.
    
    Logic:
    1. Each task must be assigned to exactly one employee OR marked as unassigned
    2. Task duration equals the assigned employee's processing time
    3. If no valid candidates exist, force unassigned
    """
    
    def build(self, data: Dict[str, Any], variables: Dict[str, Any]) -> None:
        """Add assignment constraints to model."""
        
        for task_var in variables['tasks']:
            assigned_bools = [v[0] for v in task_var['assigned_vars'].values()]
            
            if not assigned_bools:
                # No candidates - must be unassigned
                self.model.Add(task_var['unassigned_var'] == 1)
                self.model.Add(task_var['size'] == 0)
            else:
                # Exactly one assignment: sum(assigned) + unassigned == 1
                self.model.Add(
                    sum(assigned_bools) + task_var['unassigned_var'] == 1
                )
                
                # Link duration: size == sum(assigned[e] * duration[e])
                duration_expr = sum(
                    assign_var * duration
                    for assign_var, duration, _ in task_var['assigned_vars'].values()
                )
                self.model.Add(task_var['size'] == duration_expr)
