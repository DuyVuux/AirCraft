from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from src.model.aircraft import Aircraft
from src.model.hub import Hub
from src.model.employee import Employee
from src.model.time import TimeEntry
from src.model.bus import BusStop, BusRoute

@dataclass
class DistanceEntry:
    srcCode: str
    destCode: str
    travelTime: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DistanceEntry':
        try:
            return cls(
                srcCode=data['srcCode'],
                destCode=data['destCode'],
                travelTime=data['travelTime']
            )
        except KeyError as e:
            print(f"[ERROR] DistanceEntry missing field {e}")
            print(f"[ERROR] Received data: {data}")
            raise ValueError(f"DistanceEntry missing required field: {e}. Got: {list(data.keys())}")

@dataclass
class BusTransitEntry:
    """Entry in bus transit matrix"""
    fromBusStopId: str
    toBusStopId: str
    routeId: str
    transitTime: int  # actual transit time
    averageWaitTime: int  # frequency / 2
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusTransitEntry':
        return cls(
            fromBusStopId=data['fromBusStopId'],
            toBusStopId=data['toBusStopId'],
            routeId=data['routeId'],
            transitTime=data['transitTime'],
            averageWaitTime=data['averageWaitTime']
        )

@dataclass
class WalkingDistanceEntry:
    """Walking distance from location to bus stop"""
    locationId: str
    busStopId: str
    walkTime: int  # seconds
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WalkingDistanceEntry':
        return cls(
            locationId=data['locationId'],
            busStopId=data['busStopId'],
            walkTime=data['walkTime']
        )

@dataclass
class MatrixConfigs:
    # Raw data entries
    distance_entries: List[DistanceEntry] = field(default_factory=list)
    time_entries: List[TimeEntry] = field(default_factory=list)
    bus_transit_entries: List[BusTransitEntry] = field(default_factory=list)
    walking_distance_entries: List[WalkingDistanceEntry] = field(default_factory=list)
    
    # NumPy matrices
    distance_matrix: Optional[np.ndarray] = None  # 2D: [src_idx, dest_idx] -> travel_time
    time_matrix: Optional[np.ndarray] = None      # 2D: [task_idx, employee_level] -> time_process
    bus_transit_matrix: Optional[np.ndarray] = None  # 2D: [from_stop_idx, to_stop_idx] -> transit_time
    bus_wait_matrix: Optional[np.ndarray] = None     # 2D: [from_stop_idx, to_stop_idx] -> avg_wait_time
    walk_to_bus_matrix: Optional[np.ndarray] = None  # 2D: [location_idx, bus_stop_idx] -> walk_time
    
    # Index mappings
    location_to_idx: Dict[str, int] = field(default_factory=dict)
    idx_to_location: Dict[int, str] = field(default_factory=dict)
    
    task_to_idx: Dict[str, int] = field(default_factory=dict)
    idx_to_task: Dict[int, str] = field(default_factory=dict)
    
    bus_stop_to_idx: Dict[str, int] = field(default_factory=dict)
    idx_to_bus_stop: Dict[int, str] = field(default_factory=dict)
    
    # Lookup: (taskCode, aircraftId, level) -> timeProcess
    time_lookup: Dict[Tuple[str, str, int], int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MatrixConfigs':
        distance_entries = [DistanceEntry.from_dict(d) for d in data.get('distanceMatrix', [])]
        time_entries = [TimeEntry.from_dict(t) for t in data.get('timeMatrix', [])]
        bus_transit_entries = [BusTransitEntry.from_dict(b) for b in data.get('busTransitMatrix', [])]
        walking_distance_entries = [WalkingDistanceEntry.from_dict(w) for w in data.get('walkingDistanceFromLocationToBusStop', [])]
        
        config = cls(
            distance_entries=distance_entries,
            time_entries=time_entries,
            bus_transit_entries=bus_transit_entries,
            walking_distance_entries=walking_distance_entries
        )
        config._build_distance_matrix()
        config._build_time_matrix()
        config._build_bus_matrices()
        
        return config
    
    def _build_distance_matrix(self):
        """Build numpy distance matrix from entries."""
        # Collect unique locations
        locations = set()
        for entry in self.distance_entries:
            locations.add(entry.srcCode)
            locations.add(entry.destCode)
        
        # Create index mappings
        sorted_locations = sorted(locations)
        self.location_to_idx = {loc: idx for idx, loc in enumerate(sorted_locations)}
        self.idx_to_location = {idx: loc for loc, idx in self.location_to_idx.items()}
        
        # Build matrix (initialize with infinity for unreachable)
        n = len(sorted_locations)
        self.distance_matrix = np.full((n, n), np.inf)
        np.fill_diagonal(self.distance_matrix, 0)  # Self-distance is 0
        
        for entry in self.distance_entries:
            src_idx = self.location_to_idx[entry.srcCode]
            dest_idx = self.location_to_idx[entry.destCode]
            self.distance_matrix[src_idx, dest_idx] = entry.travelTime
    
    def _build_time_matrix(self):
        """Build time lookup map from entries."""
        # Reset lookup
        self.time_lookup = {}
        
        # Populate lookup map: (taskCode, aircraftId, level) -> timeProcess
        for entry in self.time_entries:
            key = (entry.taskCode, entry.aircraftId, entry.level)
            # If multiple entries exist, keep the minimum time (most optimistic)
            # or keep latest. Assuming min time for now as it's efficient.
            if key not in self.time_lookup or entry.timeProcess < self.time_lookup[key]:
                self.time_lookup[key] = entry.timeProcess
        
        # Collect unique task codes
        tasks = set()
        for entry in self.time_entries:
            tasks.add(entry.taskCode)
        
        # Create task index mappings
        sorted_tasks = sorted(tasks)
        self.task_to_idx = {task: idx for idx, task in enumerate(sorted_tasks)}
        self.idx_to_task = {idx: task for task, idx in self.task_to_idx.items()}
        
        self.time_matrix = None  # Disabled - using time_lookup
    
    def get_travel_time(self, src: str, dest: str) -> float:
        """Get travel time between two locations."""
        src_idx = self.location_to_idx.get(src)
        dest_idx = self.location_to_idx.get(dest)
        if src_idx is None or dest_idx is None:
            return np.inf
        return self.distance_matrix[src_idx, dest_idx]
    
    def get_process_time(self, task_code: str, aircraft_id: str, level: int) -> float:
        """Get process time for a task based on aircraft and employee level."""
        key = (task_code, aircraft_id, level)
        if key in self.time_lookup:
            return self.time_lookup[key]
        
        # Fallback 1: Try level 1 if requested level not found
        if level > 1:
            fallback_key = (task_code, aircraft_id, 1)
            if fallback_key in self.time_lookup:
                return self.time_lookup[fallback_key]
        
        # Fallback 2: Return default 30 mins
        return 1800.0
    
    def _build_bus_matrices(self):
        """Build bus transit and walking matrices"""
        if not self.bus_transit_entries:
            return
        
        # Collect unique bus stops
        bus_stops = set()
        for entry in self.bus_transit_entries:
            bus_stops.add(entry.fromBusStopId)
            bus_stops.add(entry.toBusStopId)
        
        # Build bus stop index mapping
        sorted_stops = sorted(bus_stops)
        self.bus_stop_to_idx = {stop: idx for idx, stop in enumerate(sorted_stops)}
        self.idx_to_bus_stop = {idx: stop for stop, idx in self.bus_stop_to_idx.items()}
        
        # Initialize matrices
        n_stops = len(sorted_stops)
        self.bus_transit_matrix = np.full((n_stops, n_stops), np.inf)
        self.bus_wait_matrix = np.full((n_stops, n_stops), np.inf)
        
        # Fill matrices
        for entry in self.bus_transit_entries:
            from_idx = self.bus_stop_to_idx[entry.fromBusStopId]
            to_idx = self.bus_stop_to_idx[entry.toBusStopId]
            self.bus_transit_matrix[from_idx, to_idx] = entry.transitTime
            self.bus_wait_matrix[from_idx, to_idx] = entry.averageWaitTime
        
        # Build walking distance matrix
        if self.walking_distance_entries and self.location_to_idx:
            n_locations = len(self.location_to_idx)
            self.walk_to_bus_matrix = np.full((n_locations, n_stops), np.inf)
            
            for entry in self.walking_distance_entries:
                if entry.locationId in self.location_to_idx and entry.busStopId in self.bus_stop_to_idx:
                    loc_idx = self.location_to_idx[entry.locationId]
                    stop_idx = self.bus_stop_to_idx[entry.busStopId]
                    self.walk_to_bus_matrix[loc_idx, stop_idx] = entry.walkTime
    
    def get_bus_transit_time(self, from_stop: str, to_stop: str) -> Tuple[float, float]:
        """Get bus transit time and wait time between stops
        Returns: (transit_time, wait_time)
        """
        if self.bus_transit_matrix is None:
            return (np.inf, np.inf)
        
        from_idx = self.bus_stop_to_idx.get(from_stop)
        to_idx = self.bus_stop_to_idx.get(to_stop)
        
        if from_idx is None or to_idx is None:
            return (np.inf, np.inf)
        
        transit_time = self.bus_transit_matrix[from_idx, to_idx]
        wait_time = self.bus_wait_matrix[from_idx, to_idx]
        
        return (transit_time, wait_time)
    
    def get_walk_to_bus_time(self, location: str, bus_stop: str) -> float:
        """Get walking time from location to bus stop"""
        if self.walk_to_bus_matrix is None:
            return np.inf
        
        loc_idx = self.location_to_idx.get(location)
        stop_idx = self.bus_stop_to_idx.get(bus_stop)
        
        if loc_idx is None or stop_idx is None:
            return np.inf
        
        return self.walk_to_bus_matrix[loc_idx, stop_idx]

@dataclass
class Context:
    trackingId: str
    aircrafts: List[Aircraft]
    hubs: List[Hub]
    employees: List[Employee]
    busStops: List[BusStop]
    busRoutes: List[BusRoute]
    matrixConfigs: MatrixConfigs

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        return cls(
            trackingId=data['trackingId'],
            aircrafts=[Aircraft.from_dict(a) for a in data.get('aircrafts', [])],
            hubs=[Hub.from_dict(h) for h in data.get('hubs', [])],
            employees=[Employee.from_dict(e) for e in data.get('employees', [])],
            busStops=[BusStop.from_dict(b) for b in data.get('busStops', [])],
            busRoutes=[BusRoute.from_dict(r) for r in data.get('busRoutes', [])],
            matrixConfigs=MatrixConfigs.from_dict(data['matrixConfigs'])
        )

