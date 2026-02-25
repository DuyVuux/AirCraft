import json
from datetime import datetime

with open('solution_test.json', 'r') as f:
    solution = json.load(f)

with open('data/input/input_complex_v2.json', 'r') as f:
    input_data = json.load(f)

employees = {emp['employeeId']: emp for emp in input_data['employees']}
aircrafts = {ac['aircraftId']: ac for ac in input_data['aircrafts']}

dropped_task_id = "VN-102"
task_code = "LOAD"

print(f"Checking Feasibility for {dropped_task_id} {task_code}")
ac = aircrafts[dropped_task_id]
ac_task = next((t for t in ac['requiredTasks'] if t['taskCode'] == task_code), None)
if not ac_task:
    print("NO LOAD TASK")
    exit()

req_certs = ac_task['requiredCertificates']
min_lvl = ac_task['minLevel']
duration = 1800 
matrix = input_data['matrixConfigs']['timeMatrix']
durs = [m['timeProcess'] for m in matrix if m['aircraftId'] in [dropped_task_id, 'ANY'] and m['taskCode'] == task_code and m.get('level', 1) == 1]
if durs:
    duration = min(durs)
print(f"Duration: {duration}s")

dep_end_max = 0
for emp_sol in solution.get('solution', []):
    for assign in emp_sol.get('assignment', []):
        if assign['task']['aircraftId'] == dropped_task_id and assign['task']['taskCode'] in ac_task.get('dependencies', []):
            et = datetime.strptime(assign['endTime'], "%Y-%m-%dT%H:%M:%SZ").timestamp()
            if et > dep_end_max:
                dep_end_max = et
                
print(f"Dependencies end at: {datetime.utcfromtimestamp(dep_end_max) if dep_end_max > 0 else 'N/A'}")

deadline = datetime.strptime(ac['timeWindow']['end'], "%Y-%m-%dT%H:%M:%SZ").timestamp()
print(f"Deadline: {datetime.utcfromtimestamp(deadline)}")

if dep_end_max > 0 and dep_end_max + duration > deadline:
    print("IMPOSSIBLE to schedule: Dependencies finish too late, not enough time left before deadline!")
else:
    if dep_end_max > 0:
        print(f"Buffer left before deadline: {deadline - (dep_end_max + duration)}s")
