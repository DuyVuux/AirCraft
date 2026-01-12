"""
Instance Generator - Generate test instances for benchmarking.
"""
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.model.context import Context


# Instance size configurations
INSTANCE_CONFIGS = {
    'small': {
        'num_aircrafts': 3,
        'tasks_per_aircraft': 3,
        'num_employees': 5
    },
    'medium': {
        'num_aircrafts': 10,
        'tasks_per_aircraft': 5,
        'num_employees': 20
    },
    'large': {
        'num_aircrafts': 20,
        'tasks_per_aircraft': 5,
        'num_employees': 40
    }
}

# Task codes
TASK_CODES = [
    'FUEL_CHECK', 'OIL_CHECK', 'TIRE_INSPECT', 'BRAKE_CHECK',
    'CABIN_CLEAN', 'CARGO_INSPECT', 'WING_INSPECT', 'ENGINE_CHECK',
    'HYDRAULIC_CHECK', 'ELECTRICAL_CHECK'
]

# Roles and levels
ROLES = ['MECHANIC', 'ENGINEER', 'TECHNICIAN']
LEVELS = [1, 2, 3]


class InstanceGenerator:
    """Generate test instances for benchmarking."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
    
    def generate(self, size: str = 'small', instance_id: int = 0) -> Dict[str, Any]:
        """
        Generate a test instance.
        
        Args:
            size: 'small', 'medium', or 'large'
            instance_id: Unique identifier for this instance
            
        Returns:
            Dict that can be used with Context.from_dict()
        """
        if size not in INSTANCE_CONFIGS:
            raise ValueError(f"Unknown size: {size}. Use 'small', 'medium', or 'large'")
        
        config = INSTANCE_CONFIGS[size]
        
        # Reset seed for reproducibility
        random.seed(self.seed + instance_id)
        
        # Base time (today at 8:00 AM UTC)
        base_time = datetime.utcnow().replace(
            hour=8, minute=0, second=0, microsecond=0
        )
        
        # Generate locations
        locations = self._generate_locations(config['num_aircrafts'])
        
        # Generate distance matrix
        distance_matrix = self._generate_distance_matrix(locations)
        
        # Generate employees
        employees = self._generate_employees(
            config['num_employees'], base_time
        )
        
        # Generate aircrafts with tasks
        aircrafts = self._generate_aircrafts(
            config['num_aircrafts'],
            config['tasks_per_aircraft'],
            locations,
            base_time
        )
        
        # Generate time matrix
        time_matrix = self._generate_time_matrix(aircrafts, employees)
        
        return {
            'trackingId': f'benchmark_{size}_{instance_id}',
            'aircrafts': aircrafts,
            'employees': employees,
            'hubs': [],
            'matrixConfigs': {
                'distanceMatrix': distance_matrix,
                'timeMatrix': time_matrix
            }
        }
    
    def generate_context(self, size: str = 'small', instance_id: int = 0) -> Context:
        """Generate a Context object directly."""
        data = self.generate(size, instance_id)
        return Context.from_dict(data)
    
    def _generate_locations(self, num_locations: int) -> List[Dict]:
        locations = []
        for i in range(num_locations):
            locations.append({
                'locationId': f'GATE_{i+1}',
                'locationType': 'GATE',
                'longitude': -122.4 + random.uniform(-0.1, 0.1),
                'latitude': 37.8 + random.uniform(-0.1, 0.1)
            })
        return locations
    
    def _generate_distance_matrix(self, locations: List[Dict]) -> List[Dict]:
        matrix = []
        for i, loc1 in enumerate(locations):
            for j, loc2 in enumerate(locations):
                if i != j:
                    # Random travel time 2-10 minutes
                    travel_time = random.randint(120, 600)
                    matrix.append({
                        'srcCode': loc1['locationId'],
                        'destCode': loc2['locationId'],
                        'travelTime': travel_time
                    })
        return matrix
    
    def _generate_employees(self, num_employees: int, 
                           base_time: datetime) -> List[Dict]:
        employees = []
        for i in range(num_employees):
            role = random.choice(ROLES)
            level = random.choice(LEVELS)
            
            # Working time: 8 hours starting from base_time
            work_start = base_time
            work_end = base_time + timedelta(hours=8)
            
            # Break: 30 min lunch around noon
            break_start = base_time + timedelta(hours=4)
            break_end = break_start + timedelta(minutes=30)
            
            employees.append({
                'employeeId': f'EMP_{i+1:03d}',
                'eType': {
                    'role': role,
                    'level': level
                },
                'workingTimes': [{
                    'start': work_start.isoformat() + 'Z',
                    'end': work_end.isoformat() + 'Z'
                }],
                'breakDuration': 1800,
                'fixedBreakTimes': [{
                    'start': break_start.isoformat() + 'Z',
                    'end': break_end.isoformat() + 'Z'
                }]
            })
        return employees
    
    def _generate_aircrafts(self, num_aircrafts: int,
                           tasks_per_aircraft: int,
                           locations: List[Dict],
                           base_time: datetime) -> List[Dict]:
        aircrafts = []
        for i in range(num_aircrafts):
            # Time window: 2-6 hours
            window_duration = random.randint(2, 6)
            window_start = base_time + timedelta(minutes=random.randint(0, 60))
            window_end = window_start + timedelta(hours=window_duration)
            
            # Random tasks
            task_codes = random.sample(
                TASK_CODES,
                min(tasks_per_aircraft, len(TASK_CODES))
            )
            
            required_tasks = []
            for task_code in task_codes:
                required_tasks.append({
                    'taskCode': task_code,
                    'minLevel': random.randint(1, 2)
                })
            
            aircrafts.append({
                'aircraftId': f'AC_{i+1:03d}',
                'aType': {
                    'id': 'A320',
                    'desc': 'Airbus A320'
                },
                'location': locations[i % len(locations)],
                'timeWindow': {
                    'start': window_start.isoformat() + 'Z',
                    'end': window_end.isoformat() + 'Z'
                },
                'requiredTasks': required_tasks
            })
        return aircrafts
    
    def _generate_time_matrix(self, aircrafts: List[Dict],
                              employees: List[Dict]) -> List[Dict]:
        """Generate task processing times for all combinations."""
        time_matrix = []
        
        for aircraft in aircrafts:
            aircraft_id = aircraft['aircraftId']
            for task in aircraft['requiredTasks']:
                task_code = task['taskCode']
                
                for emp in employees:
                    role = emp['eType']['role']
                    level = emp['eType']['level']
                    
                    # Base time 10-30 minutes, faster for higher levels
                    base_duration = random.randint(600, 1800)
                    duration = int(base_duration / (1 + 0.2 * level))
                    
                    time_matrix.append({
                        'taskCode': task_code,
                        'role': role,
                        'level': level,
                        'aircraftId': aircraft_id,
                        'timeProcess': duration
                    })
        
        return time_matrix
