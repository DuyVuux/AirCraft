import pytest
import datetime
from src.model.context import Context
from src.strategy.optimization.adapter import OptimizationEngineAdapter

def test_optimization_engine_end_to_end():
    # 1. Mock Data w/ Latitude/Longitude
    mock_data = {
        "trackingId": "TEST-001",
        "aircrafts": [
            {
                "aircraftId": "A1",
                "aType": {"id": "B737", "desc": "Boeing 737"},
                "location": {"locationId": "LOC1", "latitude": 0.0, "longitude": 0.0},
                "timeWindow": {"start": "2024-01-01T08:00:00Z", "end": "2024-01-01T12:00:00Z"},
                "requiredTasks": [
                    {"taskCode": "CHK1", "requiredCertificates": ["C1"]}
                ]
            }
        ],
        "hubs": [],
        "employees": [
            {
                "employeeId": "E1",
                "eType": {"role": "MECH", "certificates": ["C1"]},
                "workingTimes": [{"start": "2024-01-01T07:00:00Z", "end": "2024-01-01T15:00:00Z"}],
                "currentLocation": "LOC1",
                "certifications": ["C1"]
            }
        ],
        "busStops": [],
        "busRoutes": [],
        "matrixConfigs": {
            "distanceMatrix": [
                {"srcCode": "LOC1", "destCode": "LOC1", "travelTime": 0}
            ],
            "timeMatrix": [],
            "busTransitMatrix": [],
            "walkingDistanceFromLocationToBusStop": []
        }
    }
    
    # 2. Build Context
    ctx = Context.from_dict(mock_data)
    
    # 3. Init Engine
    engine = OptimizationEngineAdapter()
    engine.init(ctx)
    
    # 4. Execute
    solution = engine.execute()
    
    # 5. Verify
    assert solution is not None
    # We expect E1 to be assigned task CHK1 on A1
    assigned_count = 0
    assigned_tasks = []
    
    for emp in solution.employees:
        assigned_count += len(emp.assignments)
        for assign in emp.assignments:
            print(f"Assigned: {assign}")
            assigned_tasks.append(assign.taskCode)
            assert assign.taskCode == "CHK1"
            assert assign.aircraftId == "A1"
    
    # Check dropped tasks if assignment failed
    for d in solution.droppedTasks:
        print(f"Dropped: {d}")
    
    assert assigned_count == 1, f"Expected 1 assignment, got {assigned_count}. Dropped: {len(solution.droppedTasks)}"
