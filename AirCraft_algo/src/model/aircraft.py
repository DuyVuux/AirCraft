from dataclasses import dataclass
from typing import List, Dict, Any
from src.model.location import Location
from src.model.time import TimeWindow
from src.model.task import Task

@dataclass
class AircraftType:
    id: str
    desc: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AircraftType':
        return cls(
            id=data['id'],
            desc=data['desc']
        )

@dataclass
class Aircraft:
    aircraftId: str
    aType: AircraftType
    location: Location
    timeWindow: TimeWindow
    requiredTasks: List[Task]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Aircraft':
        return cls(
            aircraftId=data['aircraftId'],
            aType=AircraftType.from_dict(data['aType']),
            location=Location.from_dict(data['location']),
            timeWindow=TimeWindow.from_dict(data['timeWindow']),
            requiredTasks=[Task.from_dict(t) for t in data.get('requiredTasks', [])]
        )
