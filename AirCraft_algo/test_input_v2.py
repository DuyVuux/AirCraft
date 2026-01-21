import json
import pytest
from datetime import datetime

def load_v2_data():
    with open('input_complex_v2.json', 'r') as f:
        return json.load(f)

class TestInputV2Structure:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = load_v2_data()
    
    def test_version_field_exists(self):
        assert self.data.get('version') == '2.0'
    
    def test_tracking_id_updated(self):
        assert 'V2' in self.data['trackingId']

class TestEmployeeBreaks:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = load_v2_data()
        self.employees = self.data['employees']
    
    def test_all_employees_have_break_duration(self):
        for emp in self.employees:
            assert 'breakDuration' in emp
            assert emp['breakDuration'] >= 0
    
    def test_long_shift_has_fixed_breaks(self):
        for emp in self.employees:
            if emp['workingTimes']:
                wt = emp['workingTimes'][0]
                start = datetime.fromisoformat(wt['start'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(wt['end'].replace('Z', '+00:00'))
                duration = (end - start).total_seconds()
                
                if duration >= 4 * 3600:
                    assert len(emp['fixedBreakTimes']) > 0, f"{emp['employeeId']} should have fixed breaks"
                    assert emp['breakDuration'] == 1800
    
    def test_employees_have_levels(self):
        for emp in self.employees:
            assert 'level' in emp['eType'], f"{emp['employeeId']} missing level"
            assert emp['eType']['level'] in [1, 2, 3]

class TestTaskDependencies:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = load_v2_data()
        self.aircrafts = self.data['aircrafts']
    
    def test_all_tasks_have_dependencies_field(self):
        for ac in self.aircrafts:
            for task in ac['requiredTasks']:
                assert 'dependencies' in task
    
    def test_all_tasks_have_min_level(self):
        for ac in self.aircrafts:
            for task in ac['requiredTasks']:
                assert 'minLevel' in task
                assert task['minLevel'] >= 1
    
    def test_arr_m_has_no_dependencies(self):
        for ac in self.aircrafts:
            for task in ac['requiredTasks']:
                if task['taskCode'] == 'ARR-M':
                    assert task['dependencies'] == []
    
    def test_dep_m_depends_on_load(self):
        for ac in self.aircrafts:
            for task in ac['requiredTasks']:
                if task['taskCode'] == 'DEP-M':
                    assert 'LOAD' in task['dependencies']
    
    def test_dep_m_requires_level_2(self):
        for ac in self.aircrafts:
            for task in ac['requiredTasks']:
                if task['taskCode'] == 'DEP-M':
                    assert task['minLevel'] >= 2

class TestTimeMatrix:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = load_v2_data()
        self.time_matrix = self.data['matrixConfigs']['timeMatrix']
    
    def test_time_matrix_has_level_entries(self):
        for entry in self.time_matrix:
            assert 'level' in entry
            assert entry['level'] in [1, 2, 3]
    
    def test_higher_level_faster(self):
        task_times = {}
        for entry in self.time_matrix:
            key = (entry['taskCode'], entry['role'])
            if key not in task_times:
                task_times[key] = {}
            task_times[key][entry['level']] = entry['timeProcess']
        
        for key, levels in task_times.items():
            if len(levels) >= 2:
                sorted_levels = sorted(levels.keys())
                for i in range(len(sorted_levels) - 1):
                    l1, l2 = sorted_levels[i], sorted_levels[i+1]
                    assert levels[l1] >= levels[l2], f"{key}: L{l1} should be >= L{l2}"

class TestDistanceMatrix:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = load_v2_data()
        self.dist_matrix = self.data['matrixConfigs']['distanceMatrix']
    
    def test_all_gates_covered(self):
        locations = set()
        for entry in self.dist_matrix:
            locations.add(entry['srcCode'])
            locations.add(entry['destCode'])
        
        for i in range(1, 11):
            gate = f"GATE-{str(i).zfill(2)}"
            assert gate in locations, f"{gate} missing from distance matrix"
    
    def test_self_distance_is_zero(self):
        for entry in self.dist_matrix:
            if entry['srcCode'] == entry['destCode']:
                assert entry['travelTime'] == 0

class TestWalkingDistances:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = load_v2_data()
        self.walking = self.data['matrixConfigs']['walkingDistanceFromLocationToBusStop']
    
    def test_all_gates_have_walking_distances(self):
        covered_gates = set()
        for entry in self.walking:
            if 'GATE' in entry['locationId']:
                covered_gates.add(entry['locationId'])
        
        for i in range(1, 11):
            gate = f"GATE-{str(i).zfill(2)}"
            assert gate in covered_gates, f"{gate} missing walking distance"
    
    def test_each_gate_connects_to_three_stops(self):
        gate_stops = {}
        for entry in self.walking:
            loc = entry['locationId']
            if 'GATE' in loc:
                if loc not in gate_stops:
                    gate_stops[loc] = set()
                gate_stops[loc].add(entry['busStopId'])
        
        for gate, stops in gate_stops.items():
            assert len(stops) == 3, f"{gate} should connect to 3 bus stops"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
