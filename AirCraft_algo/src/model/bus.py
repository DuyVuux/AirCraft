from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.model.location import Location
from src.model.time import TimeWindow

@dataclass
class BusType:
    """Type information for bus stop"""
    id: str
    desc: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusType':
        return cls(
            id=data['id'],
            desc=data['desc']
        )

@dataclass
class BusStop:
    """Bus stop location"""
    busStopId: str
    bType: BusType
    location: Location
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusStop':
        return cls(
            busStopId=data['busStopId'],
            bType=BusType.from_dict(data['bType']),
            location=Location.from_dict(data['location'])
        )

@dataclass
class BusRouteStop:
    """Individual stop within a bus route"""
    busStopId: str
    arrivalTime: int  # seconds from route start
    departureTime: Optional[int]  # None if terminal stop
    stopDuration: int  # seconds
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusRouteStop':
        return cls(
            busStopId=data['busStopId'],
            arrivalTime=data['arrivalTime'],
            departureTime=data.get('departureTime'),
            stopDuration=data['stopDuration']
        )

@dataclass
class BusRoute:
    """Bus route with schedule"""
    routeId: str
    routeName: str
    stops: List[BusRouteStop]
    cycleTime: int  # seconds for one complete cycle
    frequency: int  # seconds between departures
    operatingHours: TimeWindow
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusRoute':
        return cls(
            routeId=data['routeId'],
            routeName=data['routeName'],
            stops=[BusRouteStop.from_dict(s) for s in data['stops']],
            cycleTime=data['cycleTime'],
            frequency=data['frequency'],
            operatingHours=TimeWindow.from_dict(data['operatingHours'])
        )
