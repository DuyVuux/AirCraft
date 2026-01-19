"""
Greedy Strategy - Earliest Deadline First (EDF) algorithm.

Heuristic:
1. Sort tasks by aircraft deadline (earliest first)
2. For each task, assign to the employee with earliest available time
3. If no employee can complete task within deadline, mark as dropped
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from src.strategy.base import IStrategy
from src.model.context import Context
from src.model.solution import Solution, TaskAssignment
from src.model.time import parse_time, timestamp_to_iso


@dataclass
class TaskItem:
    """Represents a task to be scheduled."""
    task_code: str
    aircraft_id: str
    location_id: str
    required_certificates: List[str]
    deadline: int
    earliest_start: int
    priority: int = 2  # 0=ARR, 1=TOW, 2=WO, 3=DEP


@dataclass
class EmployeeState:
    """Tracks employee scheduling state."""
    employee_id: str
    role: str
    certificates: List[str]
    capabilities: List[str]
    working_windows: List[Tuple[int, int]]
    current_location: Optional[str]
    available_time: int = 0
    assigned_tasks: List[TaskAssignment] = field(default_factory=list)


class GreedyStrategy(IStrategy):
    """
    Greedy scheduling strategy using Earliest Deadline First heuristic
    with Sequential Execution constraint per aircraft.
    
    Algorithm:
    1. Collect all tasks from all aircrafts
    2. Sort tasks by:
       - Deadline (EDF)
       - Priority (ARR -> TOW -> WO -> DEP)
    3. Track aircraft_ready_time to ensure sequential execution
    4. For each task, find best available employee
       - Start time must be >= max(employee_available, aircraft_ready)
    """
    
    def __init__(self):
        super().__init__()
        self._task_duration_cache: Dict[str, int] = {}
        self._employee_states: Dict[str, EmployeeState] = {}
        # Track when each aircraft is free for next task
        self._aircraft_ready_times: Dict[str, int] = {}
    
    def execute(self) -> Solution:
        """Execute the greedy algorithm."""
        if self.context is None:
            return Solution.empty()
        
        self._build_task_duration_cache()
        self._init_employee_states()
        self._aircraft_ready_times.clear()
        
        tasks = self._collect_all_tasks()
        
        # Sort by deadline (EDF), then by priority (Sequential)
        tasks.sort(key=lambda t: (t.deadline, t.priority))
        
        solution = Solution.empty()
        
        for task in tasks:
            assigned = self._try_assign_task(task, solution)
            if not assigned:
                solution.drop_task(
                    task.aircraft_id,
                    task.task_code,
                    task.required_certificates
                )
        
        return solution
    
    def _get_task_priority(self, task_code: str) -> int:
        """Get priority for sorting: ARR < TOW < WO < DEP."""
        code = task_code.upper()
        if 'ARR' in code: return 0
        if 'TOW' in code: return 1
        if 'DEP' in code: return 3
        return 2  # WO and others
    
    def _build_task_duration_cache(self):
        """Build cache for task durations from timeMatrix."""
        self._task_duration_cache.clear()
        
        for entry in self.context.matrixConfigs.time_entries:
            key = (entry.taskCode, entry.role, entry.aircraftId)
            self._task_duration_cache[key] = entry.timeProcess
    
    def _init_employee_states(self):
        """Initialize employee states for scheduling."""
        self._employee_states.clear()
        
        for emp in self.context.employees:
            working_windows = []
            for wt in emp.workingTimes:
                start = parse_time(wt.start)
                end = parse_time(wt.end)
                working_windows.append((start, end))
            
            earliest_start = min(w[0] for w in working_windows) if working_windows else 0
            
            capabilities = []
            if hasattr(emp, 'taskCapabilities') and emp.taskCapabilities:
                capabilities = emp.taskCapabilities
            elif hasattr(emp.eType, 'taskCapabilities') and emp.eType.taskCapabilities:
                capabilities = emp.eType.taskCapabilities
            
            self._employee_states[emp.employeeId] = EmployeeState(
                employee_id=emp.employeeId,
                role=emp.eType.role,
                certificates=emp.certifications if emp.certifications else (emp.eType.certificates if hasattr(emp.eType, 'certificates') else []),
                capabilities=capabilities,
                working_windows=working_windows,
                current_location=emp.currentLocation,
                available_time=earliest_start   
            )
    
    def _collect_all_tasks(self) -> List[TaskItem]:
        """Collect all tasks from all aircrafts."""
        tasks = []
        
        for aircraft in self.context.aircrafts:
            deadline = parse_time(aircraft.timeWindow.end)
            earliest_start = parse_time(aircraft.timeWindow.start)
            location_id = aircraft.location.locationId
            
            # Init aircraft ready time
            self._aircraft_ready_times[aircraft.aircraftId] = earliest_start
            
            for task in aircraft.requiredTasks:
                priority = self._get_task_priority(task.taskCode)
                tasks.append(TaskItem(
                    task_code=task.taskCode,
                    aircraft_id=aircraft.aircraftId,
                    location_id=location_id,
                    required_certificates=task.requiredCertificates,
                    deadline=deadline,
                    earliest_start=earliest_start,
                    priority=priority
                ))
        
        return tasks
    
    def _get_task_duration(self, task_code: str, role: str, aircraft_id: str) -> int:
        """Get task duration from cache."""
        # Try specific key
        key = (task_code, role, aircraft_id)
        if key in self._task_duration_cache:
            return self._task_duration_cache[key]
            
        # Try generic role (None)
        key_generic = (task_code, None, aircraft_id)
        if key_generic in self._task_duration_cache:
            return self._task_duration_cache[key_generic]
        
        # Fallback: search raw config
        for entry in self.context.matrixConfigs.time_entries:
            if entry.taskCode == task_code:
                return entry.timeProcess
        
        return 1800  # Default 30 min
    
    def _get_travel_time(self, from_loc: Optional[str], to_loc: str) -> int:
        """Get travel time between locations."""
        if from_loc is None or from_loc == to_loc:
            return 0
        
        travel_time = self.context.matrixConfigs.get_travel_time(from_loc, to_loc)
        if travel_time == float('inf'):
            return 0
        return int(travel_time)
    
    def _can_employee_do_task(self, emp_state: EmployeeState, task: TaskItem) -> bool:
        """Check if employee has required capabilities and certificates."""
        if task.task_code not in emp_state.capabilities:
            return False
        
        if task.required_certificates:
            for cert in task.required_certificates:
                if cert == task.task_code:
                    continue
                if cert not in emp_state.certificates:
                    return False
        
        return True
    
    def _calculate_start_time(self, emp_state: EmployeeState, task: TaskItem) -> Optional[int]:
        """Calculate earliest start time for employee to do task."""
        travel_time = self._get_travel_time(emp_state.current_location, task.location_id)
        
        earliest_arrival = emp_state.available_time + travel_time
        
        # KEY CHANGE: Start time limited by Aircraft Ready Time (Sequential)
        aircraft_ready = self._aircraft_ready_times.get(task.aircraft_id, 0)
        
        start_time = max(earliest_arrival, task.earliest_start, aircraft_ready)
        
        duration = self._get_task_duration(task.task_code, emp_state.role, task.aircraft_id)
        end_time = start_time + duration
        
        for (win_start, win_end) in emp_state.working_windows:
            if start_time >= win_start and end_time <= win_end:
                if end_time <= task.deadline:
                    return start_time
        
        # Try next windows? For simplicity, just check current best fit
        # Improvements: Iterate all windows
        return None
    
    def _try_assign_task(self, task: TaskItem, solution: Solution) -> bool:
        """Try to assign task to best available employee."""
        best_employee: Optional[EmployeeState] = None
        best_start_time: Optional[int] = None
        
        for emp_state in self._employee_states.values():
            if not self._can_employee_do_task(emp_state, task):
                continue
            
            start_time = self._calculate_start_time(emp_state, task)
            if start_time is None:
                continue
            
            if best_start_time is None or start_time < best_start_time:
                best_employee = emp_state
                best_start_time = start_time
        
        if best_employee is None or best_start_time is None:
            return False
        
        duration = self._get_task_duration(task.task_code, best_employee.role, task.aircraft_id)
        end_time = best_start_time + duration
        
        if solution.get_employee(best_employee.employee_id) is None:
            solution.add_employee(best_employee.employee_id, best_employee.certificates)
        
        solution.assign_task(
            employee_id=best_employee.employee_id,
            task_code=task.task_code,
            aircraft_id=task.aircraft_id,
            required_certificates=task.required_certificates,
            location_id=task.location_id,
            start_time=timestamp_to_iso(best_start_time),
            end_time=timestamp_to_iso(end_time)
        )
        
        # Update states
        best_employee.available_time = end_time
        best_employee.current_location = task.location_id
        
        # Update Aircraft Ready Time (for sequential tasks)
        self._aircraft_ready_times[task.aircraft_id] = end_time
        
        return True
