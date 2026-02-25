import json
from datetime import datetime

with open('data/input/input_complex_v2.json', 'r') as f:
    input_data = json.load(f)

with open('solution_test.json', 'r') as f:
    solution = json.load(f)

employees = {emp['employeeId']: emp for emp in input_data['employees']}

def parse_time(time_str):
    return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ").timestamp()

print("--- Checking Work Time and Fixed Break Time Restrictions ---")
overlap_count = 0
out_of_bounds_count = 0

for emp_sol in solution.get('solution', []):
    emp_id = emp_sol['employeeId']
    emp_input = employees[emp_id]
    assignments = emp_sol.get('assignment', [])
    fixed_breaks = emp_input.get('fixedBreakTimes', [])
    working_times = emp_input.get('workingTimes', [])
    
    for assign in assignments:
        a_start = parse_time(assign['startTime'])
        a_end = parse_time(assign['endTime'])
        
        # Check against fixedBreakTimes
        for brk in fixed_breaks:
            b_start = parse_time(brk['start'])
            b_end = parse_time(brk['end'])
            if a_start < b_end and a_end > b_start:
                print(f"BREAK OVERLAP: Emp {emp_id}, Task {assign['task']['taskCode']} for {assign['task']['aircraftId']}, TaskTime {assign['startTime']} to {assign['endTime']}, BreakTime {brk['start']} to {brk['end']}")
                overlap_count += 1
                
        # Check against workingTimes (must be inside working times)
        inside = False
        for wt in working_times:
            w_start = parse_time(wt['start'])
            w_end = parse_time(wt['end'])
            if a_start >= w_start and a_end <= w_end:
                inside = True
        
        if not inside:
            print(f"OUT OF WORKING HOURS: Emp {emp_id}, Task {assign['task']['taskCode']} for {assign['task']['aircraftId']}, TaskTime {assign['startTime']} to {assign['endTime']}")
            out_of_bounds_count += 1

print(f"Total overlapping tasks: {overlap_count}")
print(f"Total out of bounds tasks: {out_of_bounds_count}")
