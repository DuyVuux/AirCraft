"""
Solution Validator - Check if solution satisfies all constraints.
"""
from typing import List, Tuple, Optional
from src.model.context import Context
from src.model.solution import Solution
from src.model.time import parse_time, format_duration


class SolutionValidator:
    """
    Validate solution against constraints.
    
    All time values are in SECONDS (Unix timestamps for absolute times, 
    durations in seconds for intervals).
    
    Checks:
    1. No-overlap: Same employee's tasks don't overlap
    2. Working time: Tasks within employee's working hours
    3. Time windows: Tasks within aircraft time windows  
    4. Employee certificates: Employee has required certificates for task
    5. Travel time: Sufficient gap between tasks at different locations
    """
    
    def __init__(self, context: Context, solution: Solution):
        self.context = context
        self.solution = solution
        self.warnings = []
        
        # Build lookup maps
        self._build_lookups()
    
    def _build_lookups(self):
        """Build lookup maps from context."""
        # Aircraft time windows
        self.aircraft_windows = {}
        self.aircraft_locations = {}
        for ac in self.context.aircrafts:
            self.aircraft_windows[ac.aircraftId] = (
                parse_time(ac.timeWindow.start),
                parse_time(ac.timeWindow.end)
            )
            self.aircraft_locations[ac.aircraftId] = ac.location.locationId
        
        # Task required certificates
        self.task_required_certs = {}
        for aircraft in self.context.aircrafts:
            for task in aircraft.requiredTasks:
                key = (aircraft.aircraftId, task.taskCode)
                self.task_required_certs[key] = task.requiredCertificates
        
        # Employee info
        self.employee_info = {}
        for emp in self.context.employees:
            work_start = parse_time(emp.workingTimes[0].start) if emp.workingTimes else 0
            work_end = parse_time(emp.workingTimes[0].end) if emp.workingTimes else float('inf')
            breaks = [(parse_time(b.start), parse_time(b.end)) for b in emp.fixedBreakTimes]
            self.employee_info[emp.employeeId] = {
                'certificates': emp.eType.certificates,
                'work_start': work_start,
                'work_end': work_end,
                'breaks': breaks
            }
        
        # Travel times
        self.travel_times = {}
        for entry in self.context.matrixConfigs.distance_entries:
            self.travel_times[(entry.srcCode, entry.destCode)] = entry.travelTime
    
    def validate(self) -> List[str]:
        """
        Run all validations.
        
        Returns:
            List of warning messages (empty if all valid)
        """
        self.warnings = []
        
        self._check_no_overlap()
        self._check_working_time()
        self._check_time_windows()
        self._check_employee_certificates()
        self._check_travel_time()
        self._check_breaks()
        
        return self.warnings
    
    def _check_no_overlap(self):
        """Check no-overlap constraint for each employee."""
        for emp_sol in self.solution.employees:
            assignments = emp_sol.assignments
            for i, a1 in enumerate(assignments):
                start1 = parse_time(a1.startTime)
                end1 = parse_time(a1.endTime)
                
                for j, a2 in enumerate(assignments):
                    if j <= i:
                        continue
                    
                    start2 = parse_time(a2.startTime)
                    end2 = parse_time(a2.endTime)
                    
                    # Check overlap
                    if not (end1 <= start2 or end2 <= start1):
                        self.warnings.append(
                            f"[NO-OVERLAP] Employee {emp_sol.employeeId}: "
                            f"Tasks {a1.taskCode}@{a1.aircraftId} and {a2.taskCode}@{a2.aircraftId} overlap"
                        )
    
    def _check_working_time(self):
        """Check tasks are within employee working hours."""
        for emp_sol in self.solution.employees:
            if emp_sol.employeeId not in self.employee_info:
                continue
                
            info = self.employee_info[emp_sol.employeeId]
            
            for asg in emp_sol.assignments:
                start = parse_time(asg.startTime)
                end = parse_time(asg.endTime)
                
                # Check start time (hard constraint)
                if start < info['work_start']:
                    self.warnings.append(
                        f"[WORKING-TIME] Employee {emp_sol.employeeId}: "
                        f"Task {asg.taskCode} starts before work start "
                        f"({asg.startTime})"
                    )
                
                # Check overtime (soft - just info)
                if end > info['work_end']:
                    overtime_seconds = end - info['work_end']
                    self.warnings.append(
                        f"[OVERTIME] Employee {emp_sol.employeeId}: "
                        f"Task {asg.taskCode} has {format_duration(overtime_seconds)} overtime"
                    )
    
    def _check_time_windows(self):
        """Check tasks are within aircraft time windows."""
        for emp_sol in self.solution.employees:
            for asg in emp_sol.assignments:
                ac_id = asg.aircraftId
                if ac_id not in self.aircraft_windows:
                    continue
                
                window_start, window_end = self.aircraft_windows[ac_id]
                task_start = parse_time(asg.startTime)
                task_end = parse_time(asg.endTime)
                
                if task_start < window_start:
                    self.warnings.append(
                        f"[TIME-WINDOW] Task {asg.taskCode}@{ac_id}: "
                        f"Starts before aircraft available"
                    )
                
                if task_end > window_end:
                    # Add detailed debug info
                    self.warnings.append(
                        f"[TIME-WINDOW] Task {asg.taskCode}@{ac_id}: "
                        f"Ends after aircraft deadline "
                        f"(task_end={task_end}, window_end={window_end}, diff={task_end-window_end}s)"
                    )
    
    def _check_employee_certificates(self):
        """Check employee has required certificates for task."""
        for emp_sol in self.solution.employees:
            if emp_sol.employeeId not in self.employee_info:
                continue
            
            emp_certs = set(self.employee_info[emp_sol.employeeId]['certificates'])
            
            for asg in emp_sol.assignments:
                key = (asg.aircraftId, asg.taskCode)
                if key in self.task_required_certs:
                    required_certs = set(self.task_required_certs[key])
                    missing_certs = required_certs - emp_certs
                    if missing_certs:
                        self.warnings.append(
                            f"[CERTIFICATES] Employee {emp_sol.employeeId}: "
                            f"Assigned task {asg.taskCode} but missing certificates: {', '.join(missing_certs)}"
                        )
    
    def _check_travel_time(self):
        """Check sufficient travel time between tasks at different locations."""
        for emp_sol in self.solution.employees:
            assignments = sorted(emp_sol.assignments, key=lambda x: parse_time(x.startTime))
            
            for i in range(len(assignments) - 1):
                curr = assignments[i]
                next_task = assignments[i + 1]
                
                curr_loc = self.aircraft_locations.get(curr.aircraftId)
                next_loc = self.aircraft_locations.get(next_task.aircraftId)
                
                if not curr_loc or not next_loc:
                    continue
                
                if curr_loc != next_loc:
                    travel_time = self.travel_times.get((curr_loc, next_loc), 0)
                    curr_end = parse_time(curr.endTime)
                    next_start = parse_time(next_task.startTime)
                    gap = next_start - curr_end  # Gap in seconds
                    
                    if gap < travel_time:
                        deficit = travel_time - gap
                        self.warnings.append(
                            f"[TRAVEL] Employee {emp_sol.employeeId}: "
                            f"Insufficient travel time from {curr_loc} to {next_loc} "
                            f"(gap: {format_duration(gap)}, required: {format_duration(travel_time)}, "
                            f"short by: {format_duration(deficit)})"
                        )
    
    def _check_breaks(self):
        """Check tasks don't overlap with breaks."""
        for emp_sol in self.solution.employees:
            if emp_sol.employeeId not in self.employee_info:
                continue
            
            breaks = self.employee_info[emp_sol.employeeId]['breaks']
            
            for asg in emp_sol.assignments:
                task_start = parse_time(asg.startTime)
                task_end = parse_time(asg.endTime)
                
                for break_start, break_end in breaks:
                    # Check overlap
                    if not (task_end <= break_start or break_end <= task_start):
                        self.warnings.append(
                            f"[BREAK] Employee {emp_sol.employeeId}: "
                            f"Task {asg.taskCode} overlaps with break "
                            f"({break_start}-{break_end})"
                        )


def validate_solution(context: Context, solution: Solution) -> bool:
    """
    Convenience function to validate solution and print warnings.
    
    Returns:
        True if valid (no warnings), False otherwise
    """
    validator = SolutionValidator(context, solution)
    warnings = validator.validate()
    
    if warnings:
        print(f"\n[VALIDATION] Found {len(warnings)} constraint violations:")
        for w in warnings:
            print(f"  [!] {w}")
        return False
    else:
        print("[VALIDATION] [OK] All constraints satisfied")
        return True
