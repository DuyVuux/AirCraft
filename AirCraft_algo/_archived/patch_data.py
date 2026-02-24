import json
import os

INPUT_FILE = 'data/input/input_complex.json'
OUTPUT_FILE = 'data/input/input_complex.json' # Overwrite

def patch_data():
    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
        
    config = data.setdefault('matrixConfigs', {})
    dist_entries = config.setdefault('distanceMatrix', [])
    time_entries = config.setdefault('timeMatrix', [])
    
    # --- 1. Fix Locations ---
    existing_locs = set()
    for entry in dist_entries:
        existing_locs.add(entry['srcCode'])
        existing_locs.add(entry['destCode'])
        
    required_locs = set()
    for ac in data.get('aircrafts', []):
        loc = ac.get('location', {}).get('locationId')
        if loc: required_locs.add(loc)
        
    for emp in data.get('employees', []):
        loc = emp.get('currentLocation')
        if loc: required_locs.add(loc)
        
    missing_locs = required_locs - existing_locs
    print(f"Found {len(missing_locs)} missing locations: {missing_locs}")
    
    # Add simple star topology connections from a known hub (GATE-01) to missing locs
    # If GATE-01 doesn't exist, pick the first one from existing
    hub = 'GATE-01' 
    if hub not in existing_locs and existing_locs:
        hub = list(existing_locs)[0]
    elif not existing_locs:
        hub = list(required_locs)[0] if required_locs else 'HUB'

    for loc in missing_locs:
        # Hub <-> Loc
        dist_entries.append({
            "srcCode": hub, "destCode": loc, "travelTime": 600
        })
        dist_entries.append({
            "srcCode": loc, "destCode": hub, "travelTime": 600
        })
        # Loc <-> Loc (optional, but let's just rely on hub for now or add self loop)
        dist_entries.append({
            "srcCode": loc, "destCode": loc, "travelTime": 0
        })
        
        # Also connect missing to missing? 
        # For robustness, let's just assume hub connectivity is enough for the solver's graph
        # But to be safe, let's add connection to ALL other existing locations to avoid partitioned graph if code requires direct link
        # Actually context_builder just builds a matrix. 
    
    # --- 2. Fix Time Definitions ---
    existing_times = set()
    for entry in time_entries:
        # TimeEntry key is effectively (aircraftId, taskCode) or generic
        # Our context builder uses (aircraftId, taskCode) as primary key
        key = (entry.get('aircraftId'), entry.get('taskCode'))
        existing_times.add(key)
        
    # Default durations
    DURATION_MAP = {
        'ARR-M': 1800,
        'DEP-M': 1800,
        'LOAD': 2400,
        'UNLOAD': 2400,
        'CLEAN': 2700,
        'FUEL': 2100,
        'CATERING': 1800
    }
    
    added_times = 0
    for ac in data.get('aircrafts', []):
        aid = ac.get('aircraftId')
        for t in ac.get('requiredTasks', []):
            tcode = t.get('taskCode')
            key = (aid, tcode)
            
            if key not in existing_times:
                duration = DURATION_MAP.get(tcode, 3600)
                # Create entry
                new_entry = {
                    "taskCode": tcode,
                    "role": "ANY", # Solver logic might need this
                    "aircraftId": aid,
                    "timeProcess": duration,
                    "certificates": t.get('requiredCertificates', [])
                }
                time_entries.append(new_entry)
                existing_times.add(key)
                added_times += 1
                
    print(f"Added {added_times} missing time entries.")
    
    # Save
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Patched data saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    patch_data()
