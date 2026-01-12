"""
Travel Time Constraints - Enforce travel time between tasks at different locations.
"""
from typing import Dict, Any
from ortools.sat.python import cp_model
from src.strategy.orStrategy.constraints.base import ConstraintBuilder


class TravelConstraint(ConstraintBuilder):
    """
    Build travel time constraints.
    
    Logic:
    - For each pair of tasks assigned to the same employee at different locations:
      - Either task1.end + travel_time <= task2.start
      - Or task2.end + travel_time <= task1.start
    - Use boolean variable to decide order if time windows overlap
    """
    
    def build(self, data: Dict[str, Any], variables: Dict[str, Any]) -> None:
        """Add travel time constraints to model."""
        
        self._add_initial_travel(data, variables)  # NEW: Initial travel from currentLocation
        self._add_consecutive_travel(data, variables)  # Existing: Between tasks
    
    def _add_initial_travel(self, data: Dict[str, Any], variables: Dict[str, Any]) -> None:
        """
        Add initial travel constraint from employee currentLocation to tasks.
        
        Logic: For each employee with currentLocation, for each assigned task:
            task.start >= work_start + travel_time(currentLocation, task.location)
        
        This applies to ALL tasks in parallel. The first task will be forced to respect
        initial travel time, and subsequent tasks are automatically satisfied.
        """
        employees = data['employees']
        task_vars = variables['tasks']
        travel_times = data['travel_times']
        
        for emp in employees:
            if emp.current_location is None:
                continue  # No initial location, skip
            
            # For each task that might be assigned to this employee
            for task_var in task_vars:
                if emp.idx not in task_var['assigned_vars']:
                    continue  # Employee not eligible for this task
                
                assign_var, _, _ = task_var['assigned_vars'][emp.idx]
                task_location = task_var['task'].location
                
                # Get travel time from current location to task location
                # Default to 0 if same location or not found
                if emp.current_location == task_location:
                    travel_time = 0
                else:
                    travel_time = travel_times.get((emp.current_location, task_location), 300)
                
                # Constraint: If assigned to this employee, must start after work_start + travel
                self.model.Add(
                    task_var['start'] >= emp.work_start + travel_time
                ).OnlyEnforceIf(assign_var)
    
    def _add_consecutive_travel(self, data: Dict[str, Any], variables: Dict[str, Any]) -> None:
        """Add travel constraints between consecutive tasks."""
        
        employees = data['employees']
        task_vars = variables['tasks']
        travel_times = data['travel_times']
        
        for emp in employees:
            # Collect tasks that could be assigned to this employee
            candidate_tasks = []
            for t_idx, task_var in enumerate(task_vars):
                if emp.idx in task_var['assigned_vars']:
                    candidate_tasks.append((t_idx, task_var))
            
            # Sort by window start to optimize constraint generation
            candidate_tasks.sort(key=lambda x: x[1]['task'].window_start)
            
            # Add pairwise travel constraints
            for i in range(len(candidate_tasks)):
                t1_idx, tv1 = candidate_tasks[i]
                
                for j in range(i + 1, len(candidate_tasks)):
                    t2_idx, tv2 = candidate_tasks[j]
                    
                    loc1 = tv1['task'].location
                    loc2 = tv2['task'].location
                    
                    # Skip if same location
                    if loc1 == loc2:
                        continue
                    
                    # Get travel time (default 300 if not found)
                    travel_time = travel_times.get((loc1, loc2), 300)
                    
                    assign1 = tv1['assigned_vars'][emp.idx][0]
                    assign2 = tv2['assigned_vars'][emp.idx][0]
                    
                    # Check if time windows allow determining order
                    if tv1['task'].window_end + travel_time < tv2['task'].window_start:
                        # Only T1 -> T2 is possible
                        self.model.Add(
                            tv2['start'] >= tv1['end'] + travel_time
                        ).OnlyEnforceIf([assign1, assign2])
                        
                    elif tv2['task'].window_end + travel_time < tv1['task'].window_start:
                        # Only T2 -> T1 is possible
                        self.model.Add(
                            tv1['start'] >= tv2['end'] + travel_time
                        ).OnlyEnforceIf([assign1, assign2])
                        
                    else:
                        # Windows overlap - need ordering variable
                        order_var = self.model.NewBoolVar(
                            f'order_{emp.idx}_{t1_idx}_{t2_idx}'
                        )
                        
                        # If order=1: T1 -> T2
                        self.model.Add(
                            tv2['start'] >= tv1['end'] + travel_time
                        ).OnlyEnforceIf([assign1, assign2, order_var])
                        
                        # If order=0: T2 -> T1
                        self.model.Add(
                            tv1['start'] >= tv2['end'] + travel_time
                        ).OnlyEnforceIf([assign1, assign2, order_var.Not()])

