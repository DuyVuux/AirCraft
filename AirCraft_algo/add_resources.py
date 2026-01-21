import json
import os

INPUT_FILE = 'data/input/input_complex.json'
OUTPUT_FILE = 'data/input/input_complex.json'

def add_resources():
    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
        
    employees = data.get('employees', [])
    existing_ids = set(e['employeeId'] for e in employees)
    
    new_employees = []
    
    # Add Mechanics 7-10
    for i in range(7, 11):
        eid = f"EMP_MECHANIC_{i}"
        if eid not in existing_ids:
            new_employees.append({
              "employeeId": eid,
              "eType": {
                "role": "MECHANIC",
                "certificates": ["CERT_MECH"]
              },
              "currentLocation": "HUB_01",
              "workingTimes": [
                {
                  "start": "2026-01-02T18:00:00Z",
                  "end": "2026-01-03T00:00:00Z"
                }
              ],
              "taskCapabilities": [],
              "breakDuration": 0,
              "fixedBreakTimes": []
            })
            
    # Add Fuel Agents 4-7
    for i in range(4, 8):
        eid = f"EMP_FUEL_AGENT_{i}"
        if eid not in existing_ids:
            new_employees.append({
              "employeeId": eid,
              "eType": {
                "role": "FUEL_AGENT",
                "certificates": ["CERT_FUEL"]
              },
              "currentLocation": "HUB_01",
              "workingTimes": [
                {
                  "start": "2026-01-02T18:00:00Z",
                  "end": "2026-01-03T00:00:00Z"
                }
              ],
              "taskCapabilities": [],
              "breakDuration": 0,
              "fixedBreakTimes": []
            })
            
    if new_employees:
        employees.extend(new_employees)
        data['employees'] = employees
        print(f"Added {len(new_employees)} new employees.")
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved updated data to {OUTPUT_FILE}")
    else:
        print("No new employees added (already exist).")

if __name__ == '__main__':
    add_resources()
