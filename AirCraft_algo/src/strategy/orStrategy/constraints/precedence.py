"""
Precedence Constraints - Enforce task dependencies.
"""
from typing import Dict, Any
from ortools.sat.python import cp_model
from src.strategy.orStrategy.constraints.base import ConstraintBuilder


class PrecedenceConstraint(ConstraintBuilder):
    """
    Build precedence constraints for task dependencies.
    
    Logic:
    - For each task dependency: successor.start >= predecessor.end
    - Applies regardless of assignment status (if unassigned, size=0)
    """
    
    def build(self, data: Dict[str, Any], variables: Dict[str, Any]) -> None:
        """Add precedence constraints to model."""
        
        tasks = data['tasks']
        task_vars = variables['tasks']
        
        # Build task ID to index mapping
        task_id_to_idx = {task.id: idx for idx, task in enumerate(tasks)}
        
        for idx, task_var in enumerate(task_vars):
            task = task_var['task']
            
            for dep_code in task.dependencies:
                # Construct predecessor task ID
                pred_id = f"{task.aircraft_id}_{dep_code}"
                
                if pred_id in task_id_to_idx:
                    pred_idx = task_id_to_idx[pred_id]
                    pred_var = task_vars[pred_idx]
                    
                    # Enforce: current task start >= predecessor end
                    self.model.Add(
                        task_var['start'] >= pred_var['end']
                    )
