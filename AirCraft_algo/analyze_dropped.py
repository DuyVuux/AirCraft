import json
from datetime import datetime

with open('solution_test.json', 'r') as f:
    solution = json.load(f)

print("Ground Handling Employee Schedules:")
employees_work = {}
for emp_sol in solution.get('solution', []):
    emp_id = emp_sol['employeeId']
    if 'GROUND' not in emp_id:
        continue
    
    tasks = []
    for assign in emp_sol.get('assignment', []):
        tasks.append((assign['startTime'], assign['endTime'], assign['task']['taskCode'], assign['task']['aircraftId']))
        
    tasks.sort()
    print(f"\n{emp_id} schedule:")
    for st, et, tc, ac in tasks:
        print(f"  {st} to {et} : {tc} for {ac}")

