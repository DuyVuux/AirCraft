import json
import logging
import argparse
import multiprocessing
from ortools.sat.python import cp_model
# from fake_input_generator import generate_fake_input  # Not needed
from src.model.time import parse_time, normalize_time, timestamp_to_local_str
from src.strategy.optimization.adapter import OptimizationEngineAdapter
from src.model.context import Context

# --- Constants (Seconds) ---
WEIGHT_UNASSIGNED = 10_000_000
WEIGHT_OVERTIME = 100
WEIGHT_LEVEL = 10
WEIGHT_MAKESPAN = 1

# Alias for backwards compatibility
ts_to_str = timestamp_to_local_str

# --- Data Structures ---
class Task:
    def __init__(self, data, min_global_time):
        self.id = data['id']
        self.aircraft_id = data['aircraft_id']
        self.location = data['location']
        self.task_code = data['task_code']
        self.min_level = data['min_level']
        self.dependencies = data['dependencies']
        # Strict Aircraft Window
        self.window_start = normalize_time(data['window_start'], min_global_time)
        self.window_end = normalize_time(data['window_end'], min_global_time)
        self.required_role = data.get('required_role')

class Employee:
    def __init__(self, data, min_global_time, max_time):
        self.id = data['employeeId']
        self.idx = -1 # Assigned later
        self.role = data.get('eType', {}).get('role', 'UNKNOWN')
        self.level = data.get('eType', {}).get('level', 1)
        
        # Working Time
        if data['workingTimes']:
            wt = data['workingTimes'][0]
            self.work_start = normalize_time(parse_time(wt['start']), min_global_time)
            self.work_end = normalize_time(parse_time(wt['end']), min_global_time)
        else:
            self.work_start = 0
            self.work_end = max_time
            
        # Breaks
        self.breaks = []
        if 'fixedBreakTimes' in data:
            for brk in data['fixedBreakTimes']:
                b_start = normalize_time(parse_time(brk['start']), min_global_time)
                b_end = normalize_time(parse_time(brk['end']), min_global_time)
                self.breaks.append((b_start, b_end))

class AirportScheduler:
    def __init__(self, input_data, efficiency_threshold=2.0, top_k=20):
        self.data = input_data
        self.efficiency_threshold = efficiency_threshold
        self.top_k = top_k
        self.logger = logging.getLogger(__name__)
        
        self.model = None
        self.solver = None
        self.status = None
        
        # Internal Data
        self.tasks = []
        self.employees = []
        self.travel_times = {}
        self.task_durations = {}
        self.min_global_time = 0
        self.max_time = 0
        
        # Variables
        self.task_vars = [] # List of dicts
        self.employee_workloads = []
        self.level_penalty_terms = []
        self.overtime_penalties = []
        self.sum_unassigned = None
        
        self._parse_data()

    def _parse_data(self):
        aircrafts = self.data['aircrafts']
        employees_data = self.data['employees']
        dist_matrix = self.data['matrixConfigs']['distanceMatrix']
        time_matrix = self.data['matrixConfigs']['timeMatrix']
        
        # 1. Helper Maps
        for entry in dist_matrix:
            self.travel_times[(entry['srcCode'], entry['destCode'])] = entry['travelTime']

        for entry in time_matrix:
            # Handle potentially missing keys in legacy timeMatrix structure
            task_code = entry.get('taskCode')
            role = entry.get('role', 'UNKNOWN')
            level = entry.get('level', 1)
            aircraft_id = entry.get('aircraftId')
            
            if task_code and aircraft_id:
                key = (task_code, role, level, aircraft_id)
                self.task_durations[key] = entry.get('timeProcess', 0)
            
        # 2. Global Time & Horizon
        self.min_global_time = float('inf')
        for ac in aircrafts:
            ac_start = parse_time(ac['timeWindow']['start'])
            if ac_start < self.min_global_time: self.min_global_time = ac_start
            
        for emp in employees_data:
            for wt in emp['workingTimes']:
                s = parse_time(wt['start'])
                if s < self.min_global_time: self.min_global_time = s
                
        # Calculate Max Time (Horizon)
        max_window_end = 0
        for ac in aircrafts:
             ac_end = normalize_time(parse_time(ac['timeWindow']['end']), self.min_global_time)
             if ac_end > max_window_end: max_window_end = ac_end
             
        # Add buffer for potential overtime (e.g., 4 hours)
        self.max_time = max_window_end + (4 * 3600)
        
        # 3. Employees
        for idx, emp_data in enumerate(employees_data):
            emp = Employee(emp_data, self.min_global_time, self.max_time)
            emp.idx = idx
            self.employees.append(emp)
            
        # 4. Tasks
        for ac in aircrafts:
            ac_id = ac['aircraftId']
            ac_loc = ac['location']['locationId']
            ac_start = parse_time(ac['timeWindow']['start'])
            ac_end = parse_time(ac['timeWindow']['end'])
            
            for req_task in ac['requiredTasks']:
                task_data = {
                    'id': f"{ac_id}_{req_task['taskCode']}",
                    'aircraft_id': ac_id,
                    'location': ac_loc,
                    'task_code': req_task['taskCode'],
                    'min_level': req_task.get('minLevel', 1),
                    'dependencies': req_task.get('dependencies', []),
                    'window_start': ac_start,
                    'window_end': ac_end,
                    'required_role': req_task.get('requiredRole')
                }
                self.tasks.append(Task(task_data, self.min_global_time))

    def setup_model(self):
        self.model = cp_model.CpModel()

    def create_variables(self):
        # Create Task Variables
        for t_idx, task in enumerate(self.tasks):
            # Strict Domain: [WindowStart, WindowEnd]
            # Task MUST start and end within this window.
            # If not possible -> Unassigned.
            
            start_var = self.model.NewIntVar(task.window_start, task.window_end, f'start_t{t_idx}')
            end_var = self.model.NewIntVar(task.window_start, task.window_end, f'end_t{t_idx}')
            size_var = self.model.NewIntVar(0, self.max_time, f'size_t{t_idx}')
            interval_var = self.model.NewIntervalVar(start_var, size_var, end_var, f'interval_t{t_idx}')
            
            # Unassigned Variable
            unassigned_var = self.model.NewBoolVar(f'unassigned_t{t_idx}')
            
            self.task_vars.append({
                'task': task,
                'start': start_var,
                'end': end_var,
                'size': size_var,
                'interval': interval_var,
                'unassigned_var': unassigned_var,
                'assigned_vars': {} # Map e_idx -> (bool_var, duration, level_diff)
            })
            
        # Create Assignment Variables
        for t_idx, tv in enumerate(self.task_vars):
            task = tv['task']
            candidates = []
            
            for emp in self.employees:
                # Filter 1: Basic Requirements
                if emp.level < task.min_level: continue
                if task.required_role and emp.role != task.required_role: continue
                
                # Filter 2: Duration exists
                dur_key = (task.task_code, emp.role, emp.level, task.aircraft_id)
                if dur_key not in self.task_durations: continue
                
                duration = self.task_durations[dur_key]
                level_diff = emp.level - task.min_level
                candidates.append((emp.idx, duration, level_diff))
                
            # Filter 3: Top-K Efficiency
            if candidates:
                candidates.sort(key=lambda x: x[1]) # Sort by duration
                best_duration = candidates[0][1]
                valid_candidates = [c for c in candidates if c[1] <= best_duration * self.efficiency_threshold]
                final_candidates = valid_candidates[:self.top_k]
                
                for e_idx, duration, level_diff in final_candidates:
                    assign_var = self.model.NewBoolVar(f'assign_t{t_idx}_e{e_idx}')
                    tv['assigned_vars'][e_idx] = (assign_var, duration, level_diff)

    def create_constraints(self):
        # 1. Assignment Constraints
        for tv in self.task_vars:
            assigned_bools = [v[0] for v in tv['assigned_vars'].values()]
            
            if not assigned_bools:
                # No candidates -> Must be unassigned
                self.model.Add(tv['unassigned_var'] == 1)
                self.model.Add(tv['size'] == 0)
            else:
                # sum(assigned) + unassigned == 1
                self.model.Add(sum(assigned_bools) + tv['unassigned_var'] == 1)
                
                # Link duration: size == sum(assigned * duration)
                self.model.Add(tv['size'] == sum(v[0] * v[1] for v in tv['assigned_vars'].values()))

        # 2. Precedence Constraints
        for tv in self.task_vars:
            task = tv['task']
            for dep_code in task.dependencies:
                pred_id = f"{task.aircraft_id}_{dep_code}"
                pred_idx = next((i for i, t in enumerate(self.tasks) if t.id == pred_id), None)
                if pred_idx is not None:
                    # Start >= End_Pred
                    # Only enforce if both are assigned? 
                    # Actually, if unassigned, size=0, start/end are loose but within window.
                    # Standard precedence:
                    self.model.Add(tv['start'] >= self.task_vars[pred_idx]['end'])

        # 3. Employee Constraints (No Overlap, Working Time, Breaks)
        for emp in self.employees:
            emp_intervals = []
            
            for t_idx, tv in enumerate(self.task_vars):
                if emp.idx in tv['assigned_vars']:
                    assign_var, _, _ = tv['assigned_vars'][emp.idx]
                    
                    # No Overlap Interval
                    opt_interval = self.model.NewOptionalIntervalVar(
                        tv['start'], tv['size'], tv['end'], assign_var, f'opt_int_e{emp.idx}_t{t_idx}'
                    )
                    emp_intervals.append(opt_interval)
                    
                    # Working Time (Mixed)
                    # Hard: Start >= WorkStart
                    self.model.Add(tv['start'] >= emp.work_start).OnlyEnforceIf(assign_var)
                    
                    # Soft: End <= WorkEnd (Penalty handled in cost function)
                    # No hard constraint here.
            
            # Breaks (Hard)
            for b_idx, (b_start, b_end) in enumerate(emp.breaks):
                brk_int = self.model.NewIntervalVar(
                    self.model.NewConstant(b_start),
                    self.model.NewConstant(b_end - b_start),
                    self.model.NewConstant(b_end),
                    f'break_e{emp.idx}_{b_idx}_{b_start}'
                )
                emp_intervals.append(brk_int)
                
            if emp_intervals:
                self.model.AddNoOverlap(emp_intervals)

        # 4. Travel Time Constraints (HARD)
        # Iterate all pairs of tasks assigned to the same employee
        # Start_B >= End_A + Travel(Loc_A, Loc_B)
        
        # Optimization: Only consider tasks that *could* overlap or be close
        # But for hard constraints, we need to be careful.
        # Using circuit constraint or pairwise? Pairwise is easier to implement for now.
        
        for emp in self.employees:
            candidate_tasks = []
            for t_idx, tv in enumerate(self.task_vars):
                if emp.idx in tv['assigned_vars']:
                    candidate_tasks.append((t_idx, tv))
            
            # Sort by window start to reduce checks?
            candidate_tasks.sort(key=lambda x: x[1]['task'].window_start)
            
            for i in range(len(candidate_tasks)):
                t1_idx, tv1 = candidate_tasks[i]
                for j in range(i + 1, len(candidate_tasks)):
                    t2_idx, tv2 = candidate_tasks[j]
                    
                    loc1 = tv1['task'].location
                    loc2 = tv2['task'].location
                    if loc1 == loc2: continue
                    
                    travel_time = self.travel_times.get((loc1, loc2), 300)
                    assign1 = tv1['assigned_vars'][emp.idx][0]
                    assign2 = tv2['assigned_vars'][emp.idx][0]
                    
                    # If both assigned to this employee:
                    # Either T1 -> T2 OR T2 -> T1
                    
                    # Logic:
                    # (End1 + Travel <= Start2) OR (End2 + Travel <= Start1)
                    
                    # We can use a boolean to decide order, or infer from time windows
                    # If windows are disjoint, order is fixed.
                    
                    if tv1['task'].window_end + travel_time < tv2['task'].window_start:
                        # T1 -> T2 is the only possibility
                        self.model.Add(tv2['start'] >= tv1['end'] + travel_time).OnlyEnforceIf([assign1, assign2])
                    elif tv2['task'].window_end + travel_time < tv1['task'].window_start:
                        # T2 -> T1 is the only possibility
                        self.model.Add(tv1['start'] >= tv2['end'] + travel_time).OnlyEnforceIf([assign1, assign2])
                    else:
                        # Overlapping windows - need a decision variable
                        # b = 1 implies T1 -> T2
                        b = self.model.NewBoolVar(f'order_{emp.idx}_{t1_idx}_{t2_idx}')
                        
                        self.model.Add(tv2['start'] >= tv1['end'] + travel_time).OnlyEnforceIf([assign1, assign2, b])
                        self.model.Add(tv1['start'] >= tv2['end'] + travel_time).OnlyEnforceIf([assign1, assign2, b.Not()])

    def create_cost_function(self):
        # 1. Unassigned Penalty
        self.sum_unassigned = sum(tv['unassigned_var'] for tv in self.task_vars)
        
        # 2. Overtime Penalty (Soft Employee TW)
        # Penalty = max(0, End - WorkEnd)
        for emp in self.employees:
            for t_idx, tv in enumerate(self.task_vars):
                if emp.idx in tv['assigned_vars']:
                    assign_var, _, _ = tv['assigned_vars'][emp.idx]
                    
                    # If assigned, calculate overtime
                    # ot >= End - WorkEnd
                    ot = self.model.NewIntVar(0, self.max_time, f'ot_e{emp.idx}_t{t_idx}')
                    self.model.Add(ot >= tv['end'] - emp.work_end).OnlyEnforceIf(assign_var)
                    self.model.Add(ot >= 0)
                    self.overtime_penalties.append(ot)
                    
        # 3. Level Mismatch
        for tv in self.task_vars:
            for e_idx, (assign_var, _, level_diff) in tv['assigned_vars'].items():
                self.level_penalty_terms.append(assign_var * level_diff)
                
        # 4. Makespan
        makespan = self.model.NewIntVar(0, self.max_time, 'makespan')
        for tv in self.task_vars:
            self.model.Add(makespan >= tv['end']).OnlyEnforceIf(tv['unassigned_var'].Not())

        # Objective
        objective = self.model.NewIntVar(0, self.max_time * WEIGHT_UNASSIGNED * len(self.task_vars), 'objective')
        
        self.model.Add(objective == 
                       WEIGHT_MAKESPAN * makespan +
                       WEIGHT_UNASSIGNED * self.sum_unassigned +
                       WEIGHT_OVERTIME * sum(self.overtime_penalties) +
                       WEIGHT_LEVEL * sum(self.level_penalty_terms))
                       
        self.model.Minimize(objective)

    def create_hints(self):
        """Greedy heuristic to warm start the solver."""
        # Simple greedy: Assign earliest available employee
        employee_available_time = {e.idx: e.work_start for e in self.employees}
        
        # Sort tasks by window start
        sorted_tasks = sorted(enumerate(self.task_vars), key=lambda x: x[1]['task'].window_start)
        
        for t_idx, tv in sorted_tasks:
            if not tv['assigned_vars']:
                self.model.AddHint(tv['unassigned_var'], 1)
                continue
                
            best_emp = None
            best_start = float('inf')
            
            for e_idx, (assign_var, dur, _) in tv['assigned_vars'].items():
                # Earliest start is max(TaskWindowStart, EmpAvailable)
                start = max(tv['task'].window_start, employee_available_time[e_idx])
                
                # Check if fits in window (Start + Dur <= WindowEnd)
                if start + dur <= tv['task'].window_end:
                    if start < best_start:
                        best_start = start
                        best_emp = e_idx
            
            if best_emp is not None:
                # Hint assignment
                assign_var, dur, _ = tv['assigned_vars'][best_emp]
                self.model.AddHint(assign_var, 1)
                self.model.AddHint(tv['unassigned_var'], 0)
                self.model.AddHint(tv['start'], best_start)
                
                # Update availability (approximate, ignoring travel for hint)
                employee_available_time[best_emp] = best_start + dur
            else:
                self.model.AddHint(tv['unassigned_var'], 1)

    def solve(self, time_limit_seconds=60):
        self.solver = cp_model.CpSolver()
        self.solver.parameters.max_time_in_seconds = time_limit_seconds
        self.solver.parameters.log_search_progress = True
        self.solver.parameters.num_search_workers = max(1, multiprocessing.cpu_count() - 1)
        
        print("Starting Solver...")
        self.status = self.solver.Solve(self.model)
        return self.status

    def extract_solution(self):
        if self.status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return None
            
        solution = {
            'status': self.solver.StatusName(self.status),
            'assignments': [],
            'unassigned': []
        }
        
        for tv in self.task_vars:
            if self.solver.Value(tv['unassigned_var']):
                solution['unassigned'].append(tv['task'].task_code)
                continue
                
            assigned_emp = None
            for e_idx, (var, _, _) in tv['assigned_vars'].items():
                if self.solver.Value(var):
                    assigned_emp = self.employees[e_idx]
                    break
            
            if assigned_emp:
                start_time = self.solver.Value(tv['start']) + self.min_global_time
                end_time = self.solver.Value(tv['end']) + self.min_global_time
                
                solution['assignments'].append({
                    'task_id': tv['task'].id,
                    'task_code': tv['task'].task_code,
                    'aircraft_id': tv['task'].aircraft_id,
                    'location': tv['task'].location,
                    'employee_id': assigned_emp.id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'start_time_str': ts_to_str(start_time),
                    'end_time_str': ts_to_str(end_time)
                })
                
        # Sort by start time
        solution['assignments'].sort(key=lambda x: x['start_time'])
        return solution

    def print_solution(self, solution, output_file=None):
        if not solution:
            msg = "No solution found."
            print(msg)
            if output_file:
                with open(output_file, 'w') as f: f.write(msg)
            return

        lines = []
        lines.append("="*80)
        lines.append(f"SOLUTION STATUS: {solution['status']}")
        lines.append("="*80)
        lines.append(f"Unassigned Tasks: {len(solution['unassigned'])}")
        if solution['unassigned']:
            lines.append(f"  {', '.join(solution['unassigned'])}")
        lines.append("-" * 80)
        lines.append(f"{'Task':<25} {'Aircraft':<10} {'Loc':<10} {'Employee':<10} {'Start':<10} {'End':<10}")
        lines.append("-" * 80)
        
        for item in solution['assignments']:
            lines.append(f"{item['task_code']:<25} {item['aircraft_id']:<10} {item['location']:<10} {item['employee_id']:<10} {item['start_time_str']:<10} {item['end_time_str']:<10}")
        lines.append("="*80 + "\n")
        
        output_text = "\n".join(lines)
        print(output_text)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_text)

# --- Main Execution ---
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='fake_input.json', help='Input JSON file')
    parser.add_argument('--fake', action='store_true', help='Generate fake data')
    parser.add_argument('--time-limit', type=int, default=60, help='Solver time limit')
    parser.add_argument('--output', type=str, default='solution_output.txt', help='Output file')
    parser.add_argument('--strategy', type=str, default='legacy', choices=['legacy', 'lns'], help='Optimization strategy')
    args = parser.parse_args()

    # Load Data
    try:
        with open(args.input, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {args.input} not found.")
        exit(1)

    if args.strategy == 'lns':
        print("Using LNS Optimization Engine (Hexagonal Architecture)...")
        # 1. Parse Context
        ctx = Context.from_dict(data)
        
        # 2. Init and Run Adapter
        adapter = OptimizationEngineAdapter()
        adapter.init(ctx)
        solution = adapter.execute()
        
        # 3. Output
        # Convert to dict for printing consistency
        # Assuming Solution model has to_dict
        # We need to map it to the expected output format of 'print_solution' or just print it custom
        print("="*80)
        print("LNS SOLUTION")
        print("="*80)
        print(f"Assigned Employees: {len(solution.employees)}")
        print(f"Dropped Tasks: {len(solution.droppedTasks)}")
        
        lines = []
        for emp in solution.employees:
            for assign in emp.assignments:
                lines.append(f"{assign.taskCode:<25} {assign.aircraftId:<10} {assign.locationId:<10} {emp.employeeId:<10} {assign.startTime:<25} {assign.endTime:<25}")
        
        print(f"{'Task':<25} {'Aircraft':<10} {'Loc':<10} {'Employee':<10} {'Start':<25} {'End':<25}")
        print("-" * 80)
        print("\n".join(lines))
        
        if args.output:
            with open(args.output, 'w') as f:
                 f.write(f"LNS Solution\nDropped: {len(solution.droppedTasks)}\n\n")
                 f.write("\n".join(lines))
        
    else:
        # Run Legacy Solver
        scheduler = AirportScheduler(data)
        scheduler.setup_model()
        scheduler.create_variables()
        scheduler.create_constraints()
        scheduler.create_cost_function()
        scheduler.create_hints()
        
        status = scheduler.solve(time_limit_seconds=args.time_limit)
        solution = scheduler.extract_solution()
        scheduler.print_solution(solution, output_file=args.output)
