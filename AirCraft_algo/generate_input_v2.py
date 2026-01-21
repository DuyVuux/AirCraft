import json
from datetime import datetime, timedelta

def parse_iso_time(time_str):
    return datetime.fromisoformat(time_str.replace('Z', '+00:00'))

def format_iso_time(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

LEVEL_DISTRIBUTION = {
    "MECHANIC": [2, 3, 1, 2, 2, 1],
    "GROUND_HANDLING": [1, 2, 1, 2, 3, 1, 2, 1],
    "CLEANER": [1, 2, 1, 2, 1],
    "FUEL_AGENT": [2, 1, 3]
}

TASK_DEPENDENCIES = {
    "ARR-M": [],
    "UNLOAD": ["ARR-M"],
    "CLEAN": ["UNLOAD"],
    "FUEL": ["CLEAN"],
    "LOAD": ["CLEAN", "FUEL"],
    "DEP-M": ["LOAD"]
}

MIN_LEVELS = {
    "ARR-M": 1,
    "UNLOAD": 1,
    "CLEAN": 1,
    "FUEL": 1,
    "LOAD": 1,
    "DEP-M": 2
}

TIME_PROCESS_BY_LEVEL = {
    "ARR-M": {1: 2100, 2: 1800, 3: 1500},
    "UNLOAD": {1: 3000, 2: 2700, 3: 2400},
    "CLEAN": {1: 2700, 2: 2400, 3: 2100},
    "FUEL": {1: 2100, 2: 1800, 3: 1500},
    "LOAD": {1: 3000, 2: 2700, 3: 2400},
    "DEP-M": {1: 2100, 2: 1800, 3: 1500}
}

GATE_LOCATIONS = [f"GATE-{str(i).zfill(2)}" for i in range(1, 11)]

def upgrade_employee(emp, role_counters):
    role = emp['eType']['role']
    idx = role_counters.get(role, 0)
    role_counters[role] = idx + 1
    
    levels = LEVEL_DISTRIBUTION.get(role, [1])
    level = levels[idx % len(levels)]
    
    emp['eType']['level'] = level
    
    if emp['workingTimes']:
        wt = emp['workingTimes'][0]
        start = parse_iso_time(wt['start'])
        end = parse_iso_time(wt['end'])
        duration = (end - start).total_seconds()
        
        if duration >= 4 * 3600:
            mid_point = start + (end - start) / 2
            emp['breakDuration'] = 1800
            emp['fixedBreakTimes'] = [{
                "start": format_iso_time(mid_point),
                "end": format_iso_time(mid_point + timedelta(minutes=30))
            }]
        else:
            emp['breakDuration'] = 900
            emp['fixedBreakTimes'] = []
    
    return emp

def upgrade_required_tasks(tasks):
    upgraded = []
    for task in tasks:
        task_code = task['taskCode']
        task['dependencies'] = TASK_DEPENDENCIES.get(task_code, [])
        task['minLevel'] = MIN_LEVELS.get(task_code, 1)
        upgraded.append(task)
    return upgraded

def generate_time_matrix_with_levels(original_time_matrix):
    new_matrix = []
    seen = set()
    
    for entry in original_time_matrix:
        task_code = entry['taskCode']
        role = entry['role']
        certs = entry.get('certificates', [])
        aircraft_id = entry.get('aircraftId', 'ANY')
        
        for level in [1, 2, 3]:
            key = (task_code, role, level, aircraft_id)
            if key in seen:
                continue
            seen.add(key)
            
            base_time = TIME_PROCESS_BY_LEVEL.get(task_code, {}).get(level, entry['timeProcess'])
            
            new_entry = {
                "taskCode": task_code,
                "role": role,
                "level": level,
                "certificates": certs,
                "aircraftId": aircraft_id,
                "timeProcess": base_time
            }
            new_matrix.append(new_entry)
    
    return new_matrix

def generate_walking_distances(bus_stops):
    walking_entries = []
    walk_times = {
        "BS_TERMINAL": 120,
        "BS_HANGAR": 180,
        "BS_REST_AREA": 150
    }
    
    for gate in GATE_LOCATIONS:
        for stop_id, base_time in walk_times.items():
            gate_num = int(gate.split('-')[1])
            walk_time = base_time + (gate_num * 10)
            
            walking_entries.append({
                "locationId": gate,
                "busStopId": stop_id,
                "walkTime": walk_time
            })
    
    walking_entries.append({"locationId": "HANGAR-02", "busStopId": "BS_HANGAR", "walkTime": 90})
    walking_entries.append({"locationId": "APRON-03", "busStopId": "BS_HANGAR", "walkTime": 120})
    walking_entries.append({"locationId": "REST_AREA_A", "busStopId": "BS_REST_AREA", "walkTime": 60})
    
    return walking_entries

def generate_distance_matrix_complete(existing_entries):
    locations = set()
    existing = {}
    
    for entry in existing_entries:
        locations.add(entry['srcCode'])
        locations.add(entry['destCode'])
        existing[(entry['srcCode'], entry['destCode'])] = entry['travelTime']
    
    for gate in GATE_LOCATIONS:
        locations.add(gate)
    
    new_entries = list(existing_entries)
    
    for src in locations:
        for dest in locations:
            if (src, dest) not in existing:
                if src == dest:
                    travel = 0
                elif 'GATE' in src and 'GATE' in dest:
                    s_num = int(src.split('-')[1])
                    d_num = int(dest.split('-')[1])
                    travel = abs(s_num - d_num) * 60
                else:
                    travel = 300
                
                new_entries.append({
                    "srcCode": src,
                    "destCode": dest,
                    "travelTime": travel
                })
                existing[(src, dest)] = travel
    
    return new_entries

def main():
    with open('input_complex.json', 'r') as f:
        data = json.load(f)
    
    role_counters = {}
    data['employees'] = [upgrade_employee(emp, role_counters) for emp in data['employees']]
    
    for aircraft in data['aircrafts']:
        aircraft['requiredTasks'] = upgrade_required_tasks(aircraft['requiredTasks'])
    
    data['matrixConfigs']['timeMatrix'] = generate_time_matrix_with_levels(
        data['matrixConfigs']['timeMatrix']
    )
    
    data['matrixConfigs']['walkingDistanceFromLocationToBusStop'] = generate_walking_distances(
        data.get('busStops', [])
    )
    
    data['matrixConfigs']['distanceMatrix'] = generate_distance_matrix_complete(
        data['matrixConfigs']['distanceMatrix']
    )
    
    data['version'] = "2.0"
    data['trackingId'] = "PLAN-2024-12-05-001-V2"
    
    with open('input_complex_v2.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("Created input_complex_v2.json successfully!")
    print(f"- Employees with levels and breaks: {len(data['employees'])}")
    print(f"- Aircrafts with task dependencies: {len(data['aircrafts'])}")
    print(f"- Time matrix entries with levels: {len(data['matrixConfigs']['timeMatrix'])}")
    print(f"- Walking distance entries: {len(data['matrixConfigs']['walkingDistanceFromLocationToBusStop'])}")
    print(f"- Distance matrix entries: {len(data['matrixConfigs']['distanceMatrix'])}")

if __name__ == "__main__":
    main()
