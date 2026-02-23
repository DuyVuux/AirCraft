from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.model.time import TimeWindow

@dataclass
class EmployeeType:
    role: str
    certificates: List[str]
    level: int = 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmployeeType':
        return cls(
            role=data['role'],
            certificates=data.get('certificates', []),
            level=data.get('level', 1)
        )


@dataclass
class Employee:
    employeeId: str
    eType: EmployeeType
    workingTimes: List[TimeWindow]
    breakDuration: int
    fixedBreakTimes: List[TimeWindow]
    currentLocation: Optional[str] = None
    taskCapabilities: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Employee':
        return cls(
            employeeId=data['employeeId'],
            eType=EmployeeType.from_dict(data['eType']),
            currentLocation=data.get('currentLocation'),
            workingTimes=[TimeWindow.from_dict(t) for t in data.get('workingTimes', [])],
            breakDuration=data.get('breakDuration', 0),
            fixedBreakTimes=[TimeWindow.from_dict(t) for t in data.get('fixedBreakTimes', [])],
            certifications=data.get('certifications', [])
        )

    @property
    def level(self) -> int:
        """Get employee level from EmployeeType."""
        return self.eType.level

