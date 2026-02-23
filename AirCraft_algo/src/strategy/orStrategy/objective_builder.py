"""
Objective Builder - Build cost function with weighted components.
"""
from typing import Dict, Any, List
from ortools.sat.python import cp_model


# Penalty Constants với tên mô tả
PENALTY_TASK_DROP = 100_000_000       # Penalty cho mỗi task không assign được
PENALTY_AIRCRAFT_LATE = 1_000        # Penalty/giây khi task trễ aircraft deadline
PENALTY_OVERTIME = 100               # Penalty/giây cho overtime (quá giờ tan ca)
PENALTY_TOTAL_EFFORT = 100           # Penalty/giây cho tổng work+travel time
PENALTY_EMPLOYEE_WAIT = 10           # Penalty/giây cho thời gian chờ bus
PENALTY_BUS_DELAY = 5                # Penalty/giây cho bus delay
PENALTY_MAKESPAN = 1                 # Penalty cho makespan (hoàn thành sớm)

# Keep old names for backward compatibility
WEIGHT_UNASSIGNED = PENALTY_TASK_DROP
WEIGHT_TARDINESS = PENALTY_AIRCRAFT_LATE
WEIGHT_OVERTIME = 100  # Legacy
WEIGHT_MAKESPAN = 1    # Legacy


class ObjectiveBuilder:
    """
    Build multi-objective cost function for OR-Tools.
    
    Components (in priority order):
    1. PENALTY_TASK_DROP: Unassigned tasks penalty (highest weight)
    2. PENALTY_AIRCRAFT_LATE: Tardiness penalty (task ends after aircraft deadline)
    3. PENALTY_TOTAL_EFFORT: Total employee work+travel time
    4. PENALTY_EMPLOYEE_WAIT: Employee waiting time at bus stops
    5. PENALTY_BUS_DELAY: Bus delay from scheduled departure
    """
    
    def __init__(self, model: cp_model.CpModel):
        self.model = model
        # Store penalty variables for later inspection
        self.penalty_vars = {}
    
    def build(self, data: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build and set objective function.
        
        Expects:
            variables['tardiness_vars'] from AircraftTimeWindowConstraint
            variables['bus_vars'] from BusConstraint (optional)
        
        Returns:
            Dictionary of penalty variables for post-solve analysis
        """
        task_vars = variables['tasks']
        max_time = data['max_time']
        
        # 1. PENALTY_TASK_DROP: Unassigned tasks
        unassigned_vars = [tv['unassigned_var'] for tv in task_vars]
        
        # 2. PENALTY_AIRCRAFT_LATE: Tardiness - from AircraftTimeWindowConstraint
        tardiness_info = variables.get('tardiness_vars', [])
        tardiness_vars = [t[0] for t in tardiness_info]
        
        # 3. PENALTY_TOTAL_EFFORT: Total employee work+travel time
        # Calculate from task durations and travel times
        total_effort = self.model.NewIntVar(0, max_time * len(data['employees']), 'total_effort')
        # For now, use sum of task durations as proxy (full calculation in BusConstraint)
        task_durations_sum = []
        for tv in task_vars:
            # Add duration if assigned
            for emp_idx, (assign_var, duration, _) in tv['assigned_vars'].items():
                dur_contrib = self.model.NewIntVar(0, max_time, f'dur_{tv["task"].id}_{emp_idx}')
                self.model.Add(dur_contrib == duration).OnlyEnforceIf(assign_var)
                self.model.Add(dur_contrib == 0).OnlyEnforceIf(assign_var.Not())
                task_durations_sum.append(dur_contrib)
        
        if task_durations_sum:
            self.model.Add(total_effort == sum(task_durations_sum))
        else:
            self.model.Add(total_effort == 0)
        
        # 4. PENALTY_OVERTIME: From EmployeeConstraint
        overtime_info = variables.get('overtime_vars', [])
        overtime_vars = [ot[0] for ot in overtime_info]
        
        # 5. PENALTY_MAKESPAN: Per-employee makespan
        employees = data['employees']
        makespan_vars = []
        
        for emp in employees:
            makespan_e = self.model.NewIntVar(0, max_time, f'makespan_e{emp.idx}')
            
            # Collect end times of tasks assigned to this employee
            emp_end_times = [
                task_var['end']
                for task_var in task_vars
                if emp.idx in task_var['assigned_vars']
            ]
            
            if emp_end_times:
                self.model.AddMaxEquality(makespan_e, emp_end_times)
            else:
                self.model.Add(makespan_e == 0)
            
            makespan_vars.append(makespan_e)
        
        # 6. PENALTY_EMPLOYEE_WAIT & 7. PENALTY_BUS_DELAY: From BusConstraint
        bus_vars = variables.get('bus_vars', {})
        total_wait = self.model.NewIntVar(0, max_time * len(data['employees']), 'total_wait')
        total_bus_delay = self.model.NewIntVar(-max_time, max_time, 'total_bus_delay')
        
        if bus_vars:
            # Sum employee wait times
            wait_vars = list(bus_vars.get('employee_wait_vars', {}).values())
            if wait_vars:
                self.model.Add(total_wait == sum(wait_vars))
            else:
                self.model.Add(total_wait == 0)
            
            # Sum bus delays (absolute value: penalize both early and late)
            bus_instances = bus_vars.get('bus_instances', {})
            abs_delay_vars = []
            for key, info in bus_instances.items():
                # Delay = actual - scheduled (can be negative)
                delay = self.model.NewIntVar(
                    -info.get('stop', {}).stopDuration if 'stop' in info else -300, 
                    max_time, 
                    f'delay_{key}'
                )
                self.model.Add(delay == info['actual_departure'] - info['scheduled_departure'])
                
                # Absolute delay
                abs_delay = self.model.NewIntVar(0, max_time, f'abs_delay_{key}')
                self.model.AddAbsEquality(abs_delay, delay)
                abs_delay_vars.append(abs_delay)
            
            if abs_delay_vars:
                self.model.Add(total_bus_delay == sum(abs_delay_vars))
            else:
                self.model.Add(total_bus_delay == 0)
        else:
            self.model.Add(total_wait == 0)
            self.model.Add(total_bus_delay == 0)
        
        # Build objective with new penalties
        objective_var = self.model.NewIntVar(
            0,  # Now non-negative since bus delay uses absolute value
            max_time * PENALTY_TASK_DROP * len(task_vars), 
            'objective'
        )
        
        self.model.Add(
            objective_var ==
            PENALTY_TASK_DROP * sum(unassigned_vars) +
            PENALTY_AIRCRAFT_LATE * sum(tardiness_vars) +
            PENALTY_OVERTIME * sum(overtime_vars) +
            PENALTY_TOTAL_EFFORT * total_effort +
            PENALTY_EMPLOYEE_WAIT * total_wait +
            PENALTY_BUS_DELAY * total_bus_delay +
            PENALTY_MAKESPAN * sum(makespan_vars)
        )
        
        self.model.Minimize(objective_var)
        
        # Store for later
        self.penalty_vars = {
            'unassigned': unassigned_vars,
            'tardiness': tardiness_info,
            'overtime': overtime_info,
            'makespan': makespan_vars,
            'total_effort': total_effort,
            'total_wait': total_wait,
            'bus_delay': total_bus_delay
        }
        
        return self.penalty_vars
    
    def get_penalty_breakdown(self, solver: cp_model.CpSolver) -> Dict[str, Any]:
        """
        Get detailed penalty breakdown after solving.
        
        Args:
            solver: Solved CpSolver instance
            
        Returns:
            Breakdown of each penalty component
        """
        breakdown = {
            'unassigned': {'count': 0, 'penalty': 0, 'tasks': []},
            'tardiness': {'total_seconds': 0, 'penalty': 0, 'tasks': []},
            'overtime': {'total_seconds': 0, 'penalty': 0, 'tasks': []},
            'makespan': {'total_seconds': 0, 'penalty': 0, 'by_employee': []},
            'total_effort': {'value': 0, 'penalty': 0},
            'total_wait': {'value': 0, 'penalty': 0},
            'bus_delay': {'value': 0, 'penalty': 0}
        }
        
        # Unassigned
        for i, uv in enumerate(self.penalty_vars['unassigned']):
            if solver.Value(uv) == 1:
                breakdown['unassigned']['count'] += 1
                breakdown['unassigned']['tasks'].append(i)
        breakdown['unassigned']['penalty'] = breakdown['unassigned']['count'] * PENALTY_TASK_DROP
        
        # Tardiness (aircraft deadline violations)
        breakdown['debug_tasks'] = []  # Debug info for all tasks
        for tard_var, task_info, window_end, end_var in self.penalty_vars['tardiness']:
            tard_val = solver.Value(tard_var)
            end_val = solver.Value(end_var)
            breakdown['debug_tasks'].append(f"{task_info}: end={end_val}, deadline={window_end}, tard={tard_val}")
            if tard_val > 0:
                breakdown['tardiness']['total_seconds'] += tard_val
                breakdown['tardiness']['tasks'].append((task_info, tard_val, end_val, window_end))
        breakdown['tardiness']['penalty'] = breakdown['tardiness']['total_seconds'] * PENALTY_AIRCRAFT_LATE
        
        # Overtime
        for ot_var, assign_var, emp_id, t_idx, work_end, end_var in self.penalty_vars['overtime']:
            ot_val = solver.Value(ot_var)
            if ot_val > 0:
                breakdown['overtime']['total_seconds'] += ot_val
                breakdown['overtime']['tasks'].append((emp_id, t_idx, ot_val, work_end))
        breakdown['overtime']['penalty'] = breakdown['overtime']['total_seconds'] * PENALTY_OVERTIME
        
        # Makespan
        for i, makespan_var in enumerate(self.penalty_vars['makespan']):
            makespan_val = solver.Value(makespan_var)
            breakdown['makespan']['total_seconds'] += makespan_val
            breakdown['makespan']['by_employee'].append((i, makespan_val))
        breakdown['makespan']['penalty'] = breakdown['makespan']['total_seconds'] * PENALTY_MAKESPAN
        
        # Total effort (work + travel time)
        effort_val = solver.Value(self.penalty_vars['total_effort'])
        breakdown['total_effort']['value'] = effort_val
        breakdown['total_effort']['penalty'] = effort_val * PENALTY_TOTAL_EFFORT
        
        # Total wait (employee wait at bus stop)
        wait_val = solver.Value(self.penalty_vars['total_wait'])
        breakdown['total_wait']['value'] = wait_val
        breakdown['total_wait']['penalty'] = wait_val * PENALTY_EMPLOYEE_WAIT
        
        # Bus delay
        delay_val = solver.Value(self.penalty_vars['bus_delay'])
        breakdown['bus_delay']['value'] = delay_val
        breakdown['bus_delay']['penalty'] = delay_val * PENALTY_BUS_DELAY
        
        # Total
        breakdown['total'] = sum([
            breakdown['unassigned']['penalty'],
            breakdown['tardiness']['penalty'],
            breakdown['overtime']['penalty'],
            breakdown['makespan']['penalty'],
            breakdown['total_effort']['penalty'],
            breakdown['total_wait']['penalty'],
            breakdown['bus_delay']['penalty']
        ])
        
        return breakdown


def format_seconds(seconds: int) -> str:
    """Format seconds to human readable."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m{seconds % 60}s"
    else:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h}h{m}m"


def print_penalty_breakdown(breakdown: Dict[str, Any]) -> None:
    """Print penalty breakdown in readable format."""
    print("\n[Penalty Breakdown]")
    print("-" * 60)
    
    # Unassigned
    count = breakdown['unassigned']['count']
    penalty = breakdown['unassigned']['penalty']
    print(f"  DROPPED TASKS:  {count} tasks, penalty: {penalty:,}")
    if count > 0:
        for t_idx in breakdown['unassigned']['tasks']:
            print(f"                  - Task #{t_idx}")
    
    # Tardiness (Aircraft deadline violations)
    total_sec = breakdown['tardiness']['total_seconds']
    penalty = breakdown['tardiness']['penalty']
    print(f"  AIRCRAFT LATE:  {format_seconds(total_sec)}, penalty: {penalty:,}")
    if total_sec > 0:
        for task_info, seconds, end_val, window_end in breakdown['tardiness']['tasks']:
            print(f"                  - {task_info}: +{format_seconds(seconds)}")
    
    # Overtime
    overtime_sec = breakdown['overtime']['total_seconds']
    overtime_penalty = breakdown['overtime']['penalty']
    print(f"  OVERTIME:       {format_seconds(overtime_sec)}, penalty: {overtime_penalty:,}")
    if overtime_sec > 0:
        for emp_id, t_idx, ot_val, work_end in breakdown['overtime']['tasks']:
            print(f"                  - Employee {emp_id}, Task #{t_idx}: +{format_seconds(ot_val)}")
    
    # Makespan
    makespan_total = breakdown['makespan']['total_seconds']
    makespan_penalty = breakdown['makespan']['penalty']
    print(f"  MAKESPAN:       {format_seconds(makespan_total)}, penalty: {makespan_penalty:,}")
    if makespan_total > 0:
        for emp_idx, val in breakdown['makespan']['by_employee']:
            if val > 0:
                print(f"                  - Employee #{emp_idx}: {format_seconds(val)}")
    
    # Total Effort (work + travel time)
    effort_val = breakdown['total_effort']['value']
    effort_penalty = breakdown['total_effort']['penalty']
    print(f"  TOTAL EFFORT:   {format_seconds(effort_val)}, penalty: {effort_penalty:,}")
    
    # Total Wait (employee wait at bus stop)
    wait_val = breakdown['total_wait']['value']
    wait_penalty = breakdown['total_wait']['penalty']
    print(f"  BUS WAIT:       {format_seconds(wait_val)}, penalty: {wait_penalty:,}")
    
    # Bus Delay
    delay_val = breakdown['bus_delay']['value']
    delay_penalty = breakdown['bus_delay']['penalty']
    print(f"  BUS DELAY:      {delay_val}s, penalty: {delay_penalty:,}")
    
    print("-" * 60)
    print(f"  TOTAL PENALTY:  {breakdown['total']:,}")
    print()
    
    # DEBUG: Show all task end times vs deadlines
    if 'debug_tasks' in breakdown:
        print("[DEBUG] Task end times:")
        for info in breakdown['debug_tasks']:
            print(f"  {info}")
        print()
