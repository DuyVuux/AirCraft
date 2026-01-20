import json
import random
from datetime import datetime, timedelta

TEMPLATE_FILE = 'input_sample.json'
OUTPUT_FILE = 'input_complex.json'

BASE_DATE = datetime(2026, 1, 2, 18, 0, 0) # Peak start

# Helper to format time
def fmt_time(dt):
    return dt.isoformat() + "Z"

def main():
    # 1. Load Template for Matrices/Hubs
    with open(TEMPLATE_FILE, 'r') as f:
        data = json.load(f)
    
    # 2. Clear Lists
    data['aircrafts'] = []
    data['employees'] = []
    
    # 3. Generate Aircrafts (200 flights)
    # Staggered every 5-10 minutes
    current_time = BASE_DATE
    
    tasks_def = [
        {"code": "ARR-M", "dur": 30, "certs": ["CERT_MECH"], "role": "MECHANIC"},
        {"code": "UNLOAD", "dur": 45, "certs": ["CERT_GND"], "role": "GROUND_HANDLING"},
        {"code": "CLEAN", "dur": 40, "certs": ["CERT_CLN"], "role": "CLEANER"},
        {"code": "FUEL", "dur": 30, "certs": ["CERT_FUEL"], "role": "FUEL_AGENT"},
        {"code": "LOAD", "dur": 45, "certs": ["CERT_GND"], "role": "GROUND_HANDLING"},
        {"code": "DEP-M", "dur": 30, "certs": ["CERT_MECH"], "role": "MECHANIC"}
    ]
    
    for i in range(1, 21):
        # Arrival Time
        arr_time = current_time + timedelta(minutes=random.randint(0, 15))
        current_time = arr_time # Sequential arrivals
        
        # Turnaround Time (3 hours)
        dep_time = arr_time + timedelta(minutes=180)
        
        ac_tasks = []
        # Create Task Chain
        # Start times are "Earliest Start" (Ready Times)
        # ARR-M starts at Arrival
        t_start = arr_time
        
        for t_def in tasks_def:
            ac_tasks.append({
                "taskCode": t_def["code"],
                "requiredCertificates": t_def["certs"]
            })
            # Assume next task ready after previous ideal duration
            t_start += timedelta(minutes=t_def["dur"])

        ac = {
            "aircraftId": f"VN-{100+i}",
            "aType": {"id": "A321", "desc": "Airbus A321"},
            "location": {
                "locationId": f"GATE-{1+(i%10):02d}", # 10 Gates
                "locationType": "GATE",
                "longitude": 106.0, "latitude": 10.0
            },
            "timeWindow": {
                "start": fmt_time(arr_time),
                "end": fmt_time(dep_time)
            },
            "requiredTasks": ac_tasks
        }
        data['aircrafts'].append(ac)

    # 4. Generate Employees
    # Limited Pool to force contention
    # 5 Mechanics, 8 Ground, 4 Cleaners, 3 Fuel
    
    def create_emps(role, count, certs):
        for j in range(count):
            eid = f"EMP_{role}_{j+1}"
            emp = {
                "employeeId": eid,
                "eType": {"role": role, "certificates": certs},
                "currentLocation": "HUB_01",
                "workingTimes": [{"start": fmt_time(BASE_DATE), "end": fmt_time(BASE_DATE + timedelta(hours=6))}],
                "taskCapabilities": [], # Greedy fix handles this
                "breakDuration": 0,
                "fixedBreakTimes": []
            }
            data['employees'].append(emp)

    create_emps("MECHANIC", 6, ["CERT_MECH"])       # Increased slightly
    create_emps("GROUND_HANDLING", 8, ["CERT_GND"])
    create_emps("CLEANER", 5, ["CERT_CLN"])
    create_emps("FUEL_AGENT", 3, ["CERT_FUEL"])
    
    # 5. Update Matrix Config (Add new task codes if needed)
    # Start with simple fixed durations in cache logic (greedy uses cache or fallback)
    # We rely on fallback 1800s if not found, but let's add them to be safe
    
    data['matrixConfigs']['timeMatrix'] = []
    for t in tasks_def:
        data['matrixConfigs']['timeMatrix'].append({
            "taskCode": t["code"],
            "role": t["role"],
            "certificates": t["certs"],
            "aircraftId": "ANY",
            "timeProcess": t["dur"] * 60
        })

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data['aircrafts'])} aircrafts, {len(data['employees'])} employees.")

if __name__ == "__main__":
    main()
