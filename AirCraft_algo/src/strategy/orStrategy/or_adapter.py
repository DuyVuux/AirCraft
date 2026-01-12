"""
OR-Tools Data Adapter - Convert between domain models and OR-Tools internal structures.
"""
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from src.model.context import Context
from src.model.solution import Solution, TaskAssignment
from src.model.time import parse_time, normalize_time, timestamp_to_iso
from src.strategy.adapters.base import IDataAdapter


class TaskData:
    """Internal representation of a task for OR-Tools."""
    
    def __init__(self, task_id: str, aircraft_id: str, location: str, task_code: str,
                 required_certificates: List[str], dependencies: List[str], window_start: int, window_end: int,
                 required_role: Optional[str] = None):
        self.id = task_id
        self.aircraft_id = aircraft_id
        self.location = location
        self.task_code = task_code
        self.required_certificates = required_certificates
        self.dependencies = dependencies
        self.window_start = window_start
        self.window_end = window_end
        self.required_role = required_role


class EmployeeData:
    """Internal representation of an employee for OR-Tools."""
    
    def __init__(self, emp_id: str, idx: int, role: str, certificates: List[str],
                 work_start: int, work_end: int, breaks: List[Tuple[int, int]],
                 current_location: Optional[str] = None):
        self.id = emp_id
        self.idx = idx
        self.role = role
        self.certificates = certificates
        self.work_start = work_start
        self.work_end = work_end
        self.breaks = breaks  # List of (start, end) tuples
        self.current_location = current_location  # Starting location ID


class OrAdapter(IDataAdapter):
    """
    OR-Tools adapter - converts between domain models and OR-Tools structures.
    """
    
    def adapt_input(self, context: Context) -> Dict[str, Any]:
        """
        Convert Context to OR-Tools internal data.
        
        Returns:
            Dict with tasks, employees, travel_times, task_durations, 
            min_global_time, max_time
        """
        return self._parse_context(context)
    
    def adapt_output(self, internal_result: Any, context: Context) -> Solution:
        """
        Convert OR-Tools solver result to Solution.
        
        Args:
            internal_result: Dict with solver, variables, data
            context: Original context
        """
        return self._extract_solution(internal_result)
    
    def _parse_context(self, context: Context) -> Dict[str, Any]:
        """
        Parse Context into OR-Tools internal data structure.
        
        Returns dict with:
        - tasks: List[TaskData]
        - employees: List[EmployeeData]
        - travel_times: Dict[(src, dest), time]
        - task_durations: Dict[(task_code, role, level, aircraft_id), duration]
        - min_global_time: int (for denormalization)
        - max_time: int (horizon)
        """
        # 1. Extract travel times and task durations
        travel_times = {}
        for entry in context.matrixConfigs.distance_entries:
            travel_times[(entry.srcCode, entry.destCode)] = entry.travelTime
        
        task_durations = defaultdict(list)
        for entry in context.matrixConfigs.time_entries:
            # Key by (task, aircraft) -> list of (role, certs, duration)
            key = (entry.taskCode, entry.aircraftId)
            task_durations[key].append((entry.role, set(entry.certificates), entry.timeProcess))
        
        # Fallback: Ensure all required tasks have at least one duration entry
        for aircraft in context.aircrafts:
            for task in aircraft.requiredTasks:
                key = (task.taskCode, aircraft.aircraftId)
                if key not in task_durations:
                    # Default: 30 min (1800s), no specific role (None), use certificates from task
                    # This allows the solver to proceed even if timeMatrix is empty
                    task_durations[key].append((None, set(task.requiredCertificates), 1800))
        
        # 2. Calculate global min time
        min_global_time = float('inf')
        
        for aircraft in context.aircrafts:
            ac_start = parse_time(aircraft.timeWindow.start)
            min_global_time = min(min_global_time, ac_start)
        
        for employee in context.employees:
            for wt in employee.workingTimes:
                emp_start = parse_time(wt.start)
                min_global_time = min(min_global_time, emp_start)
        
        min_global_time = int(min_global_time)
        
        # 3. Calculate max time (horizon)
        max_window_end = 0
        for aircraft in context.aircrafts:
            ac_end = normalize_time(parse_time(aircraft.timeWindow.end), min_global_time)
            max_window_end = max(max_window_end, ac_end)
        
        # Add buffer for overtime (4 hours)
        max_time = max_window_end + (4 * 3600)
        
        # 4. Parse employees
        employees = []
        for idx, emp in enumerate(context.employees):
            if emp.workingTimes:
                wt = emp.workingTimes[0]
                work_start = normalize_time(parse_time(wt.start), min_global_time)
                work_end = normalize_time(parse_time(wt.end), min_global_time)
            else:
                work_start = 0
                work_end = max_time
            
            # Parse breaks
            breaks = []
            for brk in emp.fixedBreakTimes:
                b_start = normalize_time(parse_time(brk.start), min_global_time)
                b_end = normalize_time(parse_time(brk.end), min_global_time)
                breaks.append((b_start, b_end))
            
            employees.append(EmployeeData(
                emp_id=emp.employeeId,
                idx=idx,
                role=emp.eType.role,
                certificates=emp.eType.certificates,
                work_start=work_start,
                work_end=work_end,
                breaks=breaks,
                current_location=emp.currentLocation  # Parse currentLocation
            ))
        
        # 5. Parse tasks
        tasks = []
        for aircraft in context.aircrafts:
            ac_id = aircraft.aircraftId
            ac_loc = aircraft.location.locationId
            ac_start = parse_time(aircraft.timeWindow.start)
            ac_end = parse_time(aircraft.timeWindow.end)
            
            for req_task in aircraft.requiredTasks:
                task_id = f"{ac_id}_{req_task.taskCode}"
                
                tasks.append(TaskData(
                    task_id=task_id,
                    aircraft_id=ac_id,
                    location=ac_loc,
                    task_code=req_task.taskCode,
                    required_certificates=req_task.requiredCertificates,
                    dependencies=[],  # Dependencies not in current Task model
                    window_start=normalize_time(ac_start, min_global_time),
                    window_end=normalize_time(ac_end, min_global_time),
                    required_role=None  # Required role not in current Task model
                ))
        
        # 6. Parse bus data for BusConstraint
        bus_routes = context.busRoutes if hasattr(context, 'busRoutes') else []
        bus_stops = {stop.busStopId: stop for stop in (context.busStops if hasattr(context, 'busStops') else [])}
        
        # Build walk_to_stop lookup: (location, bus_stop) -> walk_time
        walk_to_stop = {}
        for entry in context.matrixConfigs.walking_distance_entries:
            walk_to_stop[(entry.locationId, entry.busStopId)] = entry.walkTime
        
        # Build bus_transit lookup: (from_stop, to_stop) -> transit_time
        bus_transit = {}
        for entry in context.matrixConfigs.bus_transit_entries:
            bus_transit[(entry.fromBusStopId, entry.toBusStopId)] = entry.transitTime
        
        # Get max walk distance from config (default 1200s = 20 min)
        max_walk_distance = getattr(context.matrixConfigs, 'max_walk_distance', 1200)
        
        # Calculate bus operating start time relative to min_global_time
        bus_operating_start = 0
        if bus_routes:
            first_route = bus_routes[0]
            if hasattr(first_route, 'operatingHours') and first_route.operatingHours:
                op_start = parse_time(first_route.operatingHours.start)
                bus_operating_start = normalize_time(op_start, min_global_time)
        
        return {
            'tasks': tasks,
            'employees': employees,
            'travel_times': travel_times,
            'task_durations': task_durations,
            'min_global_time': min_global_time,
            'max_time': max_time,
            # Bus-related data
            'bus_routes': bus_routes,
            'bus_stops': bus_stops,
            'walk_to_stop': walk_to_stop,
            'bus_transit': bus_transit,
            'max_walk_distance': max_walk_distance,
            'bus_operating_start': bus_operating_start
        }
    
    def _extract_solution(self, internal_result: Any) -> Solution:
        """
        Extract OR-Tools solver result to Solution model.
        
        Args:
            internal_result: Dict with:
                - solver: cp_model.CpSolver
                - variables: Dict with task variables
                - data: Parsed context data
            context: Original context
        """
        from src.model.solution import TravelSegment
        
        solver = internal_result['solver']
        variables = internal_result['variables']
        data = internal_result['data']
        travel_times = data.get('travel_times', {})
        
        solution = Solution.empty()
        
        # Track assignments by employee
        employee_assignments = defaultdict(list)
        
        # Process each task
        for task_var in variables['tasks']:
            task = task_var['task']
            
            if solver.Value(task_var['unassigned_var']):
                # Task is unassigned
                solution.drop_task(
                    aircraft_id=task.aircraft_id,
                    task_code=task.task_code,
                    required_certificates=task.required_certificates
                )
            else:
                # Find assigned employee
                for e_idx, (assign_var, _, _) in task_var['assigned_vars'].items():
                    if solver.Value(assign_var):
                        emp = data['employees'][e_idx]
                        
                        # Denormalize times
                        start_ts = solver.Value(task_var['start']) + data['min_global_time']
                        end_ts = solver.Value(task_var['end']) + data['min_global_time']
                        
                        employee_assignments[emp.id].append({
                            'taskCode': task.task_code,
                            'aircraftId': task.aircraft_id,
                            'requiredCertificates': task.required_certificates,
                            'locationId': task.location,
                            'startTime': timestamp_to_iso(start_ts),
                            'endTime': timestamp_to_iso(end_ts),
                            '_start_ts': start_ts,  # Keep for travel calc
                            '_end_ts': end_ts,
                            '_emp_idx': e_idx
                        })
                        break
        
        # Build employee solutions with travel segments
        for emp in data['employees']:
            emp_solution = solution.add_employee(emp.id, emp.certificates)
            
            if emp.id in employee_assignments:
                # Sort assignments by start time
                assignments = sorted(
                    employee_assignments[emp.id],
                    key=lambda x: x['startTime']
                )
                
                # Add initial travel from currentLocation to first task
                if assignments and emp.current_location:
                    first_task = assignments[0]
                    if emp.current_location != first_task['locationId']:
                        travel_time = travel_times.get(
                            (emp.current_location, first_task['locationId']), 
                            300  # Default 5 min
                        )
                        # Calculate departure time = first task start - travel time
                        departure_ts = first_task['_start_ts'] - travel_time
                        
                        emp_solution.travels.append(TravelSegment(
                            fromLocation=emp.current_location,
                            toLocation=first_task['locationId'],
                            method="WALK",  # Default to walk for now
                            travelTime=travel_time,
                            departureTime=timestamp_to_iso(departure_ts),
                            arrivalTime=timestamp_to_iso(first_task['_start_ts'])
                        ))
                
                # Add travel segments between consecutive tasks
                for i in range(len(assignments) - 1):
                    curr_task = assignments[i]
                    next_task = assignments[i + 1]
                    
                    if curr_task['locationId'] != next_task['locationId']:
                        travel_time = travel_times.get(
                            (curr_task['locationId'], next_task['locationId']), 
                            300  # Default 5 min
                        )
                        
                        # Departure after current task ends
                        departure_ts = curr_task['_end_ts']
                        # Arrival = next task start (or departure + travel)
                        arrival_ts = min(next_task['_start_ts'], departure_ts + travel_time)
                        
                        emp_solution.travels.append(TravelSegment(
                            fromLocation=curr_task['locationId'],
                            toLocation=next_task['locationId'],
                            method="WALK",  # TODO: Check if bus was used
                            travelTime=travel_time,
                            departureTime=timestamp_to_iso(departure_ts),
                            arrivalTime=timestamp_to_iso(arrival_ts)
                        ))
                
                # Add task assignments (remove internal fields)
                for asg in assignments:
                    emp_solution.assignments.append(TaskAssignment(
                        taskCode=asg['taskCode'],
                        aircraftId=asg['aircraftId'],
                        requiredCertificates=asg['requiredCertificates'],
                        locationId=asg['locationId'],
                        startTime=asg['startTime'],
                        endTime=asg['endTime']
                    ))
        
        return solution

