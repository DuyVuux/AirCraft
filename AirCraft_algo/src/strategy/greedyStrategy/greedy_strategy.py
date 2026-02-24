from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from src.strategy.base import IStrategy
from src.model.context import Context
from src.model.solution import Solution, TaskAssignment
from src.model.time import parse_time, timestamp_to_iso


@dataclass
class TaskItem:
    task_code: str
    aircraft_id: str
    location_id: str
    required_certificates: List[str]
    deadline: int
    earliest_start: int
    priority: int = 2
    dependencies: List[str] = field(default_factory=list)


@dataclass
class EmployeeState:
    employee_id: str
    role: str
    certificates: List[str]
    capabilities: List[str]
    working_windows: List[Tuple[int, int]]
    current_location: Optional[str]
    available_time: int = 0
    assigned_tasks: List[TaskAssignment] = field(default_factory=list)
    break_times: List[Tuple[int, int]] = field(default_factory=list)


class GreedyStrategy(IStrategy):
    def __init__(self):
        super().__init__()
        self._task_duration_cache: Dict[str, int] = {}
        self._employee_states: Dict[str, EmployeeState] = {}
        self._aircraft_ready_times: Dict[str, int] = {}
        self._task_end_times: Dict[str, int] = {}

    def execute(self) -> Solution:
        if self.context is None:
            return Solution.empty()

        self._build_task_duration_cache()
        self._init_employee_states()
        self._aircraft_ready_times.clear()
        self._task_end_times.clear()

        tasks = self._collect_all_tasks()
        sorted_tasks = self._topological_sort(tasks)

        solution = Solution.empty()

        for task in sorted_tasks:
            assigned = self._try_assign_task(task, solution)
            if not assigned:
                solution.drop_task(
                    task.aircraft_id,
                    task.task_code,
                    task.required_certificates
                )

        return solution

    def _topological_sort(self, tasks: List[TaskItem]) -> List[TaskItem]:
        task_map: Dict[str, TaskItem] = {}
        for t in tasks:
            key = f"{t.aircraft_id}_{t.task_code}"
            task_map[key] = t

        in_degree: Dict[str, int] = defaultdict(int)
        adj: Dict[str, List[str]] = defaultdict(list)

        for t in tasks:
            key = f"{t.aircraft_id}_{t.task_code}"
            if key not in in_degree:
                in_degree[key] = 0
            for dep in t.dependencies:
                dep_key = f"{t.aircraft_id}_{dep}"
                adj[dep_key].append(key)
                in_degree[key] += 1

        queue = deque()
        zero_deg = [k for k in in_degree if in_degree[k] == 0]
        zero_deg.sort(key=lambda k: (task_map[k].deadline, task_map[k].priority) if k in task_map else (0, 0))
        queue.extend(zero_deg)

        result = []
        while queue:
            key = queue.popleft()
            if key in task_map:
                result.append(task_map[key])
            for neighbor in adj[key]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        scheduled_keys = {f"{t.aircraft_id}_{t.task_code}" for t in result}
        for t in tasks:
            key = f"{t.aircraft_id}_{t.task_code}"
            if key not in scheduled_keys:
                result.append(t)

        return result

    def _get_task_priority(self, task_code: str) -> int:
        code = task_code.upper()
        if 'ARR' in code: return 0
        if 'TOW' in code: return 1
        if 'DEP' in code: return 3
        return 2

    def _build_task_duration_cache(self):
        self._task_duration_cache.clear()
        for entry in self.context.matrixConfigs.time_entries:
            key = (entry.taskCode, entry.role, entry.aircraftId)
            self._task_duration_cache[key] = entry.timeProcess

    def _init_employee_states(self):
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

            break_times = []
            if hasattr(emp, 'fixedBreakTimes') and emp.fixedBreakTimes:
                for brk in emp.fixedBreakTimes:
                    b_start = parse_time(brk.start)
                    b_end = parse_time(brk.end)
                    break_times.append((b_start, b_end))
            break_times.sort(key=lambda x: x[0])

            self._employee_states[emp.employeeId] = EmployeeState(
                employee_id=emp.employeeId,
                role=emp.eType.role,
                certificates=emp.certifications if emp.certifications else (emp.eType.certificates if hasattr(emp.eType, 'certificates') else []),
                capabilities=capabilities,
                working_windows=working_windows,
                current_location=emp.currentLocation,
                available_time=earliest_start,
                break_times=break_times,
            )

    def _collect_all_tasks(self) -> List[TaskItem]:
        tasks = []

        for aircraft in self.context.aircrafts:
            deadline = parse_time(aircraft.timeWindow.end)
            earliest_start = parse_time(aircraft.timeWindow.start)
            location_id = aircraft.location.locationId

            self._aircraft_ready_times[aircraft.aircraftId] = earliest_start

            for task in aircraft.requiredTasks:
                priority = self._get_task_priority(task.taskCode)
                deps = task.dependencies if hasattr(task, 'dependencies') and task.dependencies else []
                tasks.append(TaskItem(
                    task_code=task.taskCode,
                    aircraft_id=aircraft.aircraftId,
                    location_id=location_id,
                    required_certificates=task.requiredCertificates,
                    deadline=deadline,
                    earliest_start=earliest_start,
                    priority=priority,
                    dependencies=deps,
                ))

        return tasks

    def _get_task_duration(self, task_code: str, role: str, aircraft_id: str) -> int:
        key = (task_code, role, aircraft_id)
        if key in self._task_duration_cache:
            return self._task_duration_cache[key]

        key_generic = (task_code, None, aircraft_id)
        if key_generic in self._task_duration_cache:
            return self._task_duration_cache[key_generic]

        for entry in self.context.matrixConfigs.time_entries:
            if entry.taskCode == task_code:
                return entry.timeProcess

        return 1800

    def _get_travel_time(self, from_loc: Optional[str], to_loc: str) -> int:
        if from_loc is None or from_loc == to_loc:
            return 0

        travel_time = self.context.matrixConfigs.get_travel_time(from_loc, to_loc)
        if travel_time == float('inf'):
            return 0
        return int(travel_time)

    def _can_employee_do_task(self, emp_state: EmployeeState, task: TaskItem) -> bool:
        if emp_state.capabilities and task.task_code not in emp_state.capabilities:
            return False

        if task.required_certificates:
            for cert in task.required_certificates:
                if cert == task.task_code:
                    continue
                if cert not in emp_state.certificates:
                    return False

        return True

    def _adjust_for_breaks(self, start_time: int, duration: int, breaks: List[Tuple[int, int]]) -> int:
        adjusted_start = start_time
        for b_start, b_end in breaks:
            task_end = adjusted_start + duration
            if adjusted_start < b_end and task_end > b_start:
                adjusted_start = b_end
        return adjusted_start

    def _calculate_start_time(self, emp_state: EmployeeState, task: TaskItem) -> Optional[int]:
        travel_time = self._get_travel_time(emp_state.current_location, task.location_id)

        earliest_arrival = emp_state.available_time + travel_time

        aircraft_ready = self._aircraft_ready_times.get(task.aircraft_id, 0)

        dep_min_start = 0
        for dep_code in task.dependencies:
            dep_key = f"{task.aircraft_id}_{dep_code}"
            if dep_key in self._task_end_times:
                dep_min_start = max(dep_min_start, self._task_end_times[dep_key])

        min_start_time = max(earliest_arrival, task.earliest_start, aircraft_ready, dep_min_start)
        duration = self._get_task_duration(task.task_code, emp_state.role, task.aircraft_id)

        for (win_start, win_end) in emp_state.working_windows:
            actual_start = max(min_start_time, win_start)
            actual_start = self._adjust_for_breaks(actual_start, duration, emp_state.break_times)
            actual_end = actual_start + duration

            if actual_end <= win_end:
                if actual_end <= task.deadline:
                    return actual_start

        return None

    def _try_assign_task(self, task: TaskItem, solution: Solution) -> bool:
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

        best_employee.available_time = end_time
        best_employee.current_location = task.location_id

        self._aircraft_ready_times[task.aircraft_id] = end_time
        task_key = f"{task.aircraft_id}_{task.task_code}"
        self._task_end_times[task_key] = end_time

        return True
