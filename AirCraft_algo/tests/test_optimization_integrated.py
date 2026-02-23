import pytest
from src.model.context import Context, MatrixConfigs, TimeEntry
from src.model.employee import Employee, EmployeeType
from src.model.time import TimeWindow
from src.strategy.optimization.adapter import OptimizationEngineAdapter

class TestOptimizationIntegrated:
    def test_level_duration_assignment(self):
        """
        Scenario:
        Task T1 on A1.
        Time Window: [0, 6000] (Start 0, End 6000)
        
        Duration Config:
        - Level 1: 10000 (Cannot fit in 6000)
        - Level 2: 3000 (Fits)
        
        Employees:
        - E1 (Level 1)
        - E2 (Level 2)
        
        Expectation:
        - E1 cannot be assigned.
        - E2 must be assigned.
        """
        
        # 1. Setup Data
        time_entries = [
            TimeEntry(taskCode="T1", role="R1", aircraftId="A1", certificates=[], timeProcess=10000, level=1),
            TimeEntry(taskCode="T1", role="R1", aircraftId="A1", certificates=[], timeProcess=3000, level=2),
        ]
        
        # Dummy objects
        # We need mock objects that look like Context objects
        # Or construct real ones using pydantic/dataclasses if they are simple
        
        # Mocking Aircraft
        class MockLoc:
            locationId = "LOC1"
        
        class MockTask:
            taskCode = "T1"
            requiredCertificates = []
            minLevel = 1
            dependencies = []
            
        class MockAircraft:
            aircraftId = "A1"
            location = MockLoc()
            requiredTasks = [MockTask()]
            # Window 0 to 6000. ISO strings.
            # 2024-01-01T00:00:00Z to ...01:40:00Z
            timeWindow = TimeWindow(start="2024-01-01T00:00:00Z", end="2024-01-01T01:40:00Z")
            
        # Mocking Employees
        e1 = Employee(
            employeeId="E1",
            eType=EmployeeType(role="R1", certificates=[], level=1),
            workingTimes=[TimeWindow(start="2024-01-01T00:00:00Z", end="2024-01-01T10:00:00Z")],
            breakDuration=0, fixedBreakTimes=[],
            currentLocation="LOC1"
        )
        
        e2 = Employee(
            employeeId="E2",
            eType=EmployeeType(role="R1", certificates=[], level=2),
            workingTimes=[TimeWindow(start="2024-01-01T00:00:00Z", end="2024-01-01T10:00:00Z")],
            breakDuration=0, fixedBreakTimes=[],
            currentLocation="LOC1"
        )
        
        mc = MatrixConfigs(time_entries=time_entries)
        mc.location_to_idx = {"LOC1": 0}
        import numpy as np
        mc.distance_matrix = np.zeros((1,1))
        
        ctx = Context(
            trackingId="test",
            aircrafts=[MockAircraft()],
            hubs=[],
            employees=[e1, e2],
            busStops=[], busRoutes=[],
            matrixConfigs=mc
        )
        ctx.matrixConfigs = mc # Ensure binding
        
        # 2. Execute Adapter
        # Use pure_cp_mode=True to ensure we get optimal solution (or feasible) from solver directly
        adapter = OptimizationEngineAdapter(pure_cp_mode=True, time_limit_seconds=5)
        adapter.init(ctx)
        
        solution = adapter.execute()
        
        # 3. Assertions
        # T1 should be assigned to E2 (Level 2) because E1 (Level 1) is too slow (10000 > 6000 window)
        
        # Check assignments
        assigned_emp = None
        # We need to find assignment for T1. 
        # Solution object structure:
        # solution.allocations ? Or how do we query?
        # Adapter returns 'Solution' object.
        
        # Let's see assign_task usage in Adapter:
        # solution.assign_task(...) adds to internal list?
        # Checking Solution class definition might be needed.
        # Assuming we can inspect solution.
        
        # For now, let's just print solution details if we can't inspect easily
        # But we want automated assert.
        
        # Check if E2 is assigned task T1
        e2_sol = solution.get_employee("E2")
        assert e2_sol is not None
        
        # E2 should have 1 task
        assert len(e2_sol.assignments) == 1
        assert e2_sol.assignments[0].taskCode == "T1"
        
        # E1 should have 0 tasks
        e1_sol = solution.get_employee("E1")
        assert len(e1_sol.assignments) == 0

