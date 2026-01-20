import json
import sys
from collections import defaultdict

def validate_data(filepath):
    print(f"Validating {filepath}...")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found.")
        return

    issues = []
    
    # 1. Gather Definitions
    defined_locs = set()
    if 'matrixConfigs' in data:
        # From distance matrix entries
        for entry in data['matrixConfigs'].get('distanceMatrix', []):
            defined_locs.add(entry.get('srcCode'))
            defined_locs.add(entry.get('destCode'))
        # From explicit map if exists (not standard in input json usually, but let's check keys)
        
    print(f"Found {len(defined_locs)} defined locations in Matrix.")

    defined_time_entries = set() # (aircraftId, taskCode) - wait, timeEntry usually has 'aircraftId' and 'taskCode'
    # Actually timeEntry might be generic. Let's check format.
    # checking src/model/context.py: TimeEntry has aircraftId, taskCode.
    for entry in data.get('matrixConfigs', {}).get('timeMatrix', []):
        defined_time_entries.add((entry.get('aircraftId'), entry.get('taskCode')))

    print(f"Found {len(defined_time_entries)} defined time entries.")

    # 2. Check Aircraft
    orphan_locs = set()
    missing_times = set()
    
    for ac in data.get('aircrafts', []):
        aid = ac.get('aircraftId')
        
        # Check Location
        loc = ac.get('location', {}).get('locationId')
        if loc and loc not in defined_locs:
            orphan_locs.add(loc)
        
        # Check Tasks
        for t in ac.get('requiredTasks', []):
            tcode = t.get('taskCode')
            # Logic: Input might imply pattern matching (e.g. by type), but strict checking:
            if (aid, tcode) not in defined_time_entries:
                # Try finding if there is a generic one? Current model is specific.
                missing_times.add(f"{aid}::{tcode}")

    # 3. Check Employees
    for emp in data.get('employees', []):
        loc = emp.get('currentLocation')
        if loc and loc not in defined_locs:
            orphan_locs.add(loc)

    # Report
    print("\n--- VALIDATION REPORT ---")
    
    if orphan_locs:
        print(f"\n[CRITICAL] Found {len(orphan_locs)} ORPHAN LOCATIONS (referenced but not in Distance Matrix):")
        print(f"Suggest adding these to 'matrixConfigs.distanceMatrix' with valid distances.")
        for l in sorted(list(orphan_locs))[:10]:
            print(f" - {l}")
        if len(orphan_locs) > 10: print(" ... and more.")
    else:
        print("\n[OK] All locations are defined.")

    if missing_times:
        print(f"\n[WARNING] Found {len(missing_times)} MISSING TIME ENTRIES:")
        print(f"Solver will default these to 3600s, which may be inaccurate.")
        for mt in sorted(list(missing_times))[:10]:
            print(f" - {mt}")
        if len(missing_times) > 10: print(" ... and more.")
    else:
        print("\n[OK] All task times are defined.")

if __name__ == "__main__":
    import sys
    file = sys.argv[1] if len(sys.argv) > 1 else 'data/input/input_complex.json'
    validate_data(file)
