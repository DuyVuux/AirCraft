"""
Solution Model - Output structure for aircraft maintenance scheduling.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class TimeSlot:
    """Time slot with start and end time."""
    startTime: str
    endTime: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {"startTime": self.startTime, "endTime": self.endTime}


@dataclass
class TaskAssignment:
    """Task assigned to an employee."""
    taskCode: str
    aircraftId: str
    requiredCertificates: List[str]
    locationId: str
    startTime: str
    endTime: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": {
                "taskCode": self.taskCode,
                "aircraftId": self.aircraftId,
                "requiredCertificates": self.requiredCertificates
            },
            "locationId": self.locationId,
            "startTime": self.startTime,
            "endTime": self.endTime
        }


@dataclass
class TravelSegment:
    """Travel segment between tasks or from starting location."""
    fromLocation: str           # Starting location ID
    toLocation: str             # Destination location ID
    method: str                 # "WALK" or "BUS"
    travelTime: int             # Duration in seconds
    departureTime: str          # ISO timestamp when leaving
    arrivalTime: str            # ISO timestamp when arriving
    busRouteId: Optional[str] = None    # Bus route ID if method is BUS
    waitTime: Optional[int] = None      # Wait time at bus stop in seconds
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "fromLocation": self.fromLocation,
            "toLocation": self.toLocation,
            "method": self.method,
            "travelTime": self.travelTime,
            "departureTime": self.departureTime,
            "arrivalTime": self.arrivalTime
        }
        if self.busRouteId:
            result["busRouteId"] = self.busRouteId
        if self.waitTime is not None:
            result["waitTime"] = self.waitTime
        return result


@dataclass
class EmployeeSolution:
    """Solution for a single employee."""
    employeeId: str
    certificates: List[str]
    assignments: List[TaskAssignment] = field(default_factory=list)
    travels: List[TravelSegment] = field(default_factory=list)  # NEW: Travel segments
    breakTimes: List[TimeSlot] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "employeeId": self.employeeId,
            "certificates": self.certificates,
            "assignment": [a.to_dict() for a in self.assignments],
            "travels": [t.to_dict() for t in self.travels],  # NEW
            "breakTimes": [b.to_dict() for b in self.breakTimes]
        }


@dataclass
class DroppedTask:
    """Task that could not be assigned."""
    taskCode: str
    aircraftId: str
    requiredCertificates: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "taskCode": self.taskCode,
            "aircraftId": self.aircraftId,
            "requiredCertificates": self.requiredCertificates
        }


@dataclass
class DroppedAircraft:
    """Aircraft with dropped tasks."""
    aircraftId: str
    tasks: List[DroppedTask] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "aircraftId": self.aircraftId,
            "tasks": [t.to_dict() for t in self.tasks]
        }


@dataclass
class Solution:
    """Complete solution for the scheduling problem."""
    employees: List[EmployeeSolution] = field(default_factory=list)
    droppedTasks: List[DroppedAircraft] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "solution": [e.to_dict() for e in self.employees],
            "droppedTasks": [d.to_dict() for d in self.droppedTasks]
        }
    
    @classmethod
    def empty(cls) -> 'Solution':
        """Create an empty solution."""
        return cls()
    
    def add_employee(self, employee_id: str, certificates: List[str]) -> EmployeeSolution:
        """Add an employee to the solution."""
        emp = EmployeeSolution(employeeId=employee_id, certificates=certificates)
        self.employees.append(emp)
        return emp
    
    def get_employee(self, employee_id: str) -> EmployeeSolution:
        """Get employee solution by ID."""
        for emp in self.employees:
            if emp.employeeId == employee_id:
                return emp
        return None
    
    def assign_task(self, employee_id: str, task_code: str, aircraft_id: str, 
                    required_certificates: List[str], location_id: str, start_time: str, end_time: str):
        """Assign a task to an employee."""
        emp = self.get_employee(employee_id)
        if emp is None:
            raise ValueError(f"Employee {employee_id} not in solution")
        
        emp.assignments.append(TaskAssignment(
            taskCode=task_code,
            aircraftId=aircraft_id,
            requiredCertificates=required_certificates,
            locationId=location_id,
            startTime=start_time,
            endTime=end_time
        ))
    
    def add_break(self, employee_id: str, start_time: str, end_time: str):
        """Add a break time for an employee."""
        emp = self.get_employee(employee_id)
        if emp is None:
            raise ValueError(f"Employee {employee_id} not in solution")
        emp.breakTimes.append(TimeSlot(startTime=start_time, endTime=end_time))
    
    def drop_task(self, aircraft_id: str, task_code: str, required_certificates: List[str]):
        """Mark a task as dropped."""
        aircraft = None
        for d in self.droppedTasks:
            if d.aircraftId == aircraft_id:
                aircraft = d
                break
        
        if aircraft is None:
            aircraft = DroppedAircraft(aircraftId=aircraft_id)
            self.droppedTasks.append(aircraft)
        
        aircraft.tasks.append(DroppedTask(
            taskCode=task_code,
            aircraftId=aircraft_id,
            requiredCertificates=required_certificates
        ))
