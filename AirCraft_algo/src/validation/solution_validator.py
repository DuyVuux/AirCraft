"""
Solution Validator - Verify solution correctness and constraint satisfaction.
"""
from typing import Dict, List, Set, Tuple
from src.model.context import Context
from src.model.solution import Solution
from src.model.time import parse_time
from src.utils.logger import get_logger
logger = get_logger("src.validation.solution_validator")


class ValidationError(Exception):
    """Raised when solution violates hard constraints."""
    pass


class SolutionValidator:
    """Validates solution against context constraints."""
    
    def __init__(self, context: Context, solution: Solution):
        self.context = context
        self.solution = solution
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> None:
        """
        Validate solution and raise ValidationError if hard constraints violated.
        
        Raises:
            ValidationError: If any hard constraint is violated
        """
        # Hard constraints
        self._check_assignment_uniqueness()
        self._check_no_overlap()
        self._check_time_windows()
        self._check_breaks()
        self._check_certificates()
        
        # Soft constraints (warnings only)
        self._check_overtime()
        self._check_tardiness()
        
        # Report
        if self.warnings:
            logger.info("\n[VALIDATION WARNINGS]")
            for warning in self.warnings:
                logger.info(f"  ⚠️  {warning}")
        
        if self.errors:
            error_msg = "\n".join([f"  ❌ {e}" for e in self.errors])
            raise ValidationError(f"Solution validation failed:\n{error_msg}")
    
    def _check_assignment_uniqueness(self) -> None:
        """Each task should be assigned to exactly one employee or dropped."""
        assigned_tasks: Set[str] = set()
        
        for emp in self.solution.employees:
            for assignment in emp.assignments:
                task_id = f"{assignment.aircraftId}_{assignment.taskCode}"
                
                if task_id in assigned_tasks:
                    self.errors.append(
                        f"Task {task_id} assigned to multiple employees"
                    )
                assigned_tasks.add(task_id)
    
    def _check_no_overlap(self) -> None:
        """Employee tasks should not overlap."""
        for emp in self.solution.employees:
            assignments = sorted(emp.assignments, key=lambda a: parse_time(a.startTime))
            
            for i in range(len(assignments) - 1):
                curr = assignments[i]
                next_task = assignments[i + 1]
                
                curr_end = parse_time(curr.endTime)
                next_start = parse_time(next_task.startTime)
                
                if curr_end > next_start:
                    self.errors.append(
                        f"Employee {emp.employeeId}: Tasks overlap - "
                        f"{curr.taskCode} ends at {curr.endTime}, "
                        f"{next_task.taskCode} starts at {next_task.startTime}"
                    )
    
    def _check_time_windows(self) -> None:
        """Tasks should start within aircraft time windows."""
        # Build aircraft time windows map
        aircraft_windows = {}
        for aircraft in self.context.aircrafts:
            aircraft_windows[aircraft.aircraftId] = (
                parse_time(aircraft.timeWindow.start),
                parse_time(aircraft.timeWindow.end)
            )
        
        for emp in self.solution.employees:
            for assignment in emp.assignments:
                if assignment.aircraftId not in aircraft_windows:
                    continue
                
                window_start, window_end = aircraft_windows[assignment.aircraftId]
                task_start = parse_time(assignment.startTime)
                
                if task_start < window_start:
                    self.errors.append(
                        f"Task {assignment.taskCode} on {assignment.aircraftId} "
                        f"starts before aircraft arrival: "
                        f"{assignment.startTime} < {self.context.aircrafts[0].timeWindow.start}"
                    )
    
    def _check_breaks(self) -> None:
        """Tasks should not overlap with employee breaks."""
        for emp_sol in self.solution.employees:
            # Find employee in context
            emp_data = next(
                (e for e in self.context.employees if e.employeeId == emp_sol.employeeId),
                None
            )
            if not emp_data:
                continue
            
            # Check all assignments against break times
            for assignment in emp_sol.assignments:
                task_start = parse_time(assignment.startTime)
                task_end = parse_time(assignment.endTime)
                
                for break_time in emp_data.fixedBreakTimes:
                    break_start = parse_time(break_time.start)
                    break_end = parse_time(break_time.end)
                    
                    # Check overlap: task and break intersect
                    if not (task_end <= break_start or task_start >= break_end):
                        self.errors.append(
                            f"Employee {emp_sol.employeeId}: Task {assignment.taskCode} "
                            f"overlaps with break time {break_time.start} - {break_time.end}"
                        )
    
    def _check_certificates(self) -> None:
        """Employees should have required certificates for assigned tasks."""
        # Build task requirements map
        task_requirements = {}
        for aircraft in self.context.aircrafts:
            for task in aircraft.requiredTasks:
                task_id = f"{aircraft.aircraftId}_{task.taskCode}"
                task_requirements[task_id] = set(task.requiredCertificates)
        
        for emp_sol in self.solution.employees:
            emp_certs = set(emp_sol.certificates)
            
            for assignment in emp_sol.assignments:
                task_id = f"{assignment.aircraftId}_{assignment.taskCode}"
                required = task_requirements.get(task_id, set())
                
                if not required.issubset(emp_certs):
                    missing = required - emp_certs
                    self.warnings.append(
                        f"Employee {emp_sol.employeeId} missing certificates for "
                        f"{assignment.taskCode}: {', '.join(missing)}"
                    )
    
    def _check_overtime(self) -> None:
        """Check if employees work beyond their shift."""
        for emp_sol in self.solution.employees:
            if not emp_sol.assignments:
                continue
            
            # Find employee working times
            emp_data = next(
                (e for e in self.context.employees if e.employeeId == emp_sol.employeeId),
                None
            )
            if not emp_data or not emp_data.workingTimes:
                continue
            
            work_end = parse_time(emp_data.workingTimes[0].end)
            
            for assignment in emp_sol.assignments:
                task_end = parse_time(assignment.endTime)
                
                if task_end > work_end:
                    overtime_sec = task_end - work_end
                    self.warnings.append(
                        f"Employee {emp_sol.employeeId}: Task {assignment.taskCode} "
                        f"ends {overtime_sec}s after shift end"
                    )
    
    def _check_tardiness(self) -> None:
        """Check if tasks finish after aircraft departure."""
        aircraft_windows = {}
        for aircraft in self.context.aircrafts:
            aircraft_windows[aircraft.aircraftId] = parse_time(aircraft.timeWindow.end)
        
        for emp in self.solution.employees:
            for assignment in emp.assignments:
                if assignment.aircraftId not in aircraft_windows:
                    continue
                
                deadline = aircraft_windows[assignment.aircraftId]
                task_end = parse_time(assignment.endTime)
                
                if task_end > deadline:
                    tardiness = task_end - deadline
                    self.warnings.append(
                        f"Task {assignment.taskCode} on {assignment.aircraftId} "
                        f"finishes {tardiness}s after aircraft departure"
                    )


def validate_solution(context: Context, solution: Solution) -> None:
    """
    Validate solution against context constraints.
    
    Args:
        context: Problem context
        solution: Proposed solution
        
    Raises:
        ValidationError: If solution violates hard constraints
    """
    validator = SolutionValidator(context, solution)
    validator.validate()
