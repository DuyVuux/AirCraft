import pytest
from src.model.context import Context, MatrixConfigs, TimeEntry
from src.model.employee import Employee, EmployeeType
from src.strategy.orStrategy.or_adapter import OrAdapter

class TestLevelDuration:
    def test_context_time_lookup(self):
        # Setup
        time_entries = [
            TimeEntry(taskCode="T1", role="R1", aircraftId="A1", certificates=[], timeProcess=3600, level=1),
            TimeEntry(taskCode="T1", role="R1", aircraftId="A1", certificates=[], timeProcess=1800, level=2),
        ]
        
        # Test direct lookup
        matrix_configs = MatrixConfigs(time_entries=time_entries)
        matrix_configs._build_time_matrix()
        
        assert matrix_configs.get_process_time("T1", "A1", 1) == 3600
        assert matrix_configs.get_process_time("T1", "A1", 2) == 1800
        
        # Test fallback (Level 3 -> Level 1? No, fallback logic was: try requested -> try level 1)
        # My implementation: if key match: return. Else try key with level=1.
        # So get_process_time("T1", "A1", 3) -> should return level 1 time (3600)
        assert matrix_configs.get_process_time("T1", "A1", 3) == 3600
        
        # Test default fallback
        assert matrix_configs.get_process_time("TX", "A1", 1) == 1800.0

    def test_or_adapter_durations(self):
        # Setup Context with minimal data
        time_entries = [
            TimeEntry(taskCode="T1", role="R1", aircraftId="A1", certificates=[], timeProcess=60, level=1),
            TimeEntry(taskCode="T1", role="R1", aircraftId="A1", certificates=[], timeProcess=30, level=2),
        ]
        from src.model.time import TimeWindow
        ctx = Context(
            trackingId="test", aircrafts=[], hubs=[], 
            employees=[
                Employee(
                    employeeId="E1", eType=EmployeeType("R1", [], 1), 
                    workingTimes=[TimeWindow("2024-01-01T08:00:00Z", "2024-01-01T17:00:00Z")],
                    breakDuration=0, fixedBreakTimes=[]
                )
            ],
            busStops=[], busRoutes=[],
            matrixConfigs=MatrixConfigs(time_entries=time_entries)
        )
        ctx.matrixConfigs._build_time_matrix()

        # Run Adapter
        adapter = OrAdapter()
        data = adapter._parse_context(ctx)
        
        task_durations = data['task_durations']
        key = ("T1", "A1")
        assert key in task_durations
        entries = task_durations[key]
        
        # Expecting tuples: (role, certs, level, duration)
        entry1 = next(e for e in entries if e[2] == 1)
        assert entry1[3] == 60
        
        entry2 = next(e for e in entries if e[2] == 2)
        assert entry2[3] == 30
