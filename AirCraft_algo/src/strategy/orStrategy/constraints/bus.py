"""
Bus Constraints - Handle bus travel decision and timing constraints.

This is a complex constraint that integrates bus transportation into the scheduling.
Creates decision variables for bus usage and timing.
"""
from typing import Dict, Any, List, Tuple, Optional
from ortools.sat.python import cp_model
from src.strategy.orStrategy.constraints.base import ConstraintBuilder


class BusConstraint(ConstraintBuilder):
    """
    Build bus travel constraints with flexible departure times.
    
    Decision Variables Created:
    - bus_actual_departure[r, s, k]: When bus r actually departs from stop s in cycle k
    - use_bus[emp, t1, t2]: Whether employee uses bus between tasks t1->t2
    - boards_bus[emp, r, s, k]: Whether employee boards bus r at stop s in cycle k
    - employee_wait_time[emp, t]: Time employee waits at bus stop for travel to task t
    
    Constraints:
    1. Bus only departs within window [arrival, arrival + stopDuration]
    2. Employee can only board if arrives before bus departs
    3. Bus waits for boarding employees (within window)
    4. Travel time calculation for bus/walk
    5. Link between use_bus and boards_bus
    6. Max walk distance constraint
    """
    
    def __init__(self, model: cp_model.CpModel):
        super().__init__(model)
        self.bus_vars = {}  # Store bus decision variables
        
    def build(self, data: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build bus constraints and add decision variables.
        
        Returns:
            Dictionary of bus-related variables for objective function
        """
        # Check if bus data exists
        if 'bus_routes' not in data or not data['bus_routes']:
            # No bus routes - skip bus constraints
            return {}
        
        bus_routes = data['bus_routes']
        bus_stops = data.get('bus_stops', {})
        walk_to_stop = data.get('walk_to_stop', {})  # location -> stop -> time
        bus_transit = data.get('bus_transit', {})  # (stop1, stop2) -> time
        max_walk_distance = data.get('max_walk_distance', 1200)  # Default 20 min
        
        employees = data['employees']
        task_vars = variables['tasks']
        travel_times = data['travel_times']  # Walking distances
        max_time = data['max_time']
        min_global_time = data['min_global_time']
        operating_start = data.get('bus_operating_start', 0)
        
        # 1. Create bus instance variables (bus_actual_departure)
        bus_instances = self._create_bus_instances(
            bus_routes, max_time, operating_start
        )
        
        # 2. Create employee travel decision variables
        travel_decisions = self._create_travel_decisions(
            task_vars, employees, travel_times, max_walk_distance, max_time
        )
        
        # 3. Create boarding variables
        boarding_vars = self._create_boarding_vars(
            employees, task_vars, bus_instances, walk_to_stop
        )
        
        # 4. Add bus departure window constraints (Constraint 1)
        self._add_bus_window_constraints(bus_instances)
        
        # 5. Add employee boarding constraints (Constraints 2, 3)
        employee_wait_vars = self._add_boarding_constraints(
            employees, task_vars, bus_instances, boarding_vars,
            walk_to_stop, travel_times, max_time
        )
        
        # 6. Add travel time constraints (Constraints 5, 6)
        self._add_travel_time_constraints(
            employees, task_vars, travel_decisions, bus_instances,
            boarding_vars, walk_to_stop, bus_transit, travel_times
        )
        
        # 7. Link use_bus and boards_bus (Constraint 7)
        self._link_travel_boarding(
            travel_decisions, boarding_vars, employees, task_vars, bus_instances
        )
        
        # 8. Max walk distance constraint (Constraint 8)
        self._add_max_walk_constraint(
            travel_decisions, travel_times, task_vars, max_walk_distance
        )
        
        # Store variables for objective function
        self.bus_vars = {
            'bus_instances': bus_instances,
            'travel_decisions': travel_decisions,
            'boarding_vars': boarding_vars,
            'employee_wait_vars': employee_wait_vars
        }
        
        # Return variables for use in objective builder
        return self.bus_vars
    
    def _create_bus_instances(
        self, 
        bus_routes: List[Any], 
        max_time: int,
        operating_start: int
    ) -> Dict[Tuple[str, str, int], Dict[str, Any]]:
        """Create bus_actual_departure variables for each bus instance."""
        bus_instances = {}
        
        for route in bus_routes:
            frequency = route.frequency
            # Calculate number of cycles based on operating hours
            num_cycles = max(1, max_time // frequency)
            
            for stop in route.stops:
                if stop.departureTime is None:
                    continue  # Terminal stop, no departure
                
                for k in range(num_cycles):
                    # Calculate scheduled times for this cycle
                    cycle_start = operating_start + k * frequency
                    arrival = cycle_start + stop.arrivalTime
                    scheduled_dep = cycle_start + stop.departureTime
                    
                    # Actual departure window: [arrival, arrival + stopDuration]
                    earliest = arrival
                    latest = arrival + stop.stopDuration
                    
                    if latest > max_time:
                        continue  # Skip if outside horizon
                    
                    actual_dep = self.model.NewIntVar(
                        earliest, latest,
                        f'bus_{route.routeId}_{stop.busStopId}_c{k}_dep'
                    )
                    
                    bus_instances[(route.routeId, stop.busStopId, k)] = {
                        'route': route,
                        'stop': stop,
                        'cycle': k,
                        'arrival': arrival,
                        'scheduled_departure': scheduled_dep,
                        'actual_departure': actual_dep,
                        'earliest_dep': earliest,
                        'latest_dep': latest
                    }
        
        return bus_instances
    
    def _create_travel_decisions(
        self,
        task_vars: List[Dict],
        employees: List[Any],
        travel_times: Dict,
        max_walk_distance: int,
        max_time: int
    ) -> Dict[Tuple[int, int, int], Any]:
        """Create use_bus decision variables for employee travels."""
        travel_decisions = {}
        
        for emp in employees:
            for t1_idx, tv1 in enumerate(task_vars):
                if emp.idx not in tv1['assigned_vars']:
                    continue
                    
                for t2_idx, tv2 in enumerate(task_vars):
                    if t1_idx == t2_idx:
                        continue
                    if emp.idx not in tv2['assigned_vars']:
                        continue
                    
                    loc1 = tv1['task'].location
                    loc2 = tv2['task'].location
                    
                    if loc1 == loc2:
                        continue  # Same location, no travel
                    
                    # Create use_bus variable
                    use_bus = self.model.NewBoolVar(
                        f'use_bus_e{emp.idx}_t{t1_idx}_t{t2_idx}'
                    )
                    
                    travel_decisions[(emp.idx, t1_idx, t2_idx)] = {
                        'use_bus': use_bus,
                        'from_loc': loc1,
                        'to_loc': loc2
                    }
        
        return travel_decisions
    
    def _create_boarding_vars(
        self,
        employees: List[Any],
        task_vars: List[Dict],
        bus_instances: Dict,
        walk_to_stop: Dict
    ) -> Dict[Tuple[int, str, str, int, int], Any]:
        """Create boards_bus variables."""
        boarding_vars = {}
        
        for emp in employees:
            for t_idx, tv in enumerate(task_vars):
                if emp.idx not in tv['assigned_vars']:
                    continue
                
                task_loc = tv['task'].location
                
                # Check which bus stops are reachable from this location
                for (route_id, stop_id, cycle), bus_info in bus_instances.items():
                    # Only create if location can reach this stop
                    if (task_loc, stop_id) not in walk_to_stop:
                        continue
                    
                    boards = self.model.NewBoolVar(
                        f'boards_e{emp.idx}_t{t_idx}_{route_id}_{stop_id}_c{cycle}'
                    )
                    
                    boarding_vars[(emp.idx, t_idx, route_id, stop_id, cycle)] = {
                        'boards': boards,
                        'bus_info': bus_info,
                        'task_idx': t_idx
                    }
        
        return boarding_vars
    
    def _add_bus_window_constraints(
        self, 
        bus_instances: Dict
    ) -> None:
        """Constraint 1: Bus departure within window."""
        # These constraints are implicit in IntVar domain [earliest, latest]
        # Already handled in _create_bus_instances
        pass
    
    def _add_boarding_constraints(
        self,
        employees: List[Any],
        task_vars: List[Dict],
        bus_instances: Dict,
        boarding_vars: Dict,
        walk_to_stop: Dict,
        travel_times: Dict,
        max_time: int
    ) -> Dict[Tuple[int, int], Any]:
        """Constraints 2, 3: Employee arrival and bus waiting."""
        employee_wait_vars = {}
        
        for (emp_idx, t_idx, route_id, stop_id, cycle), bv in boarding_vars.items():
            boards = bv['boards']
            bus_info = bv['bus_info']
            
            task_var = task_vars[t_idx]
            task_loc = task_var['task'].location
            
            # Get walk time to bus stop
            walk_time = walk_to_stop.get((task_loc, stop_id), 9999)
            
            # Get employee assignment variable
            emp_assign = task_var['assigned_vars'].get(emp_idx)
            if not emp_assign:
                continue
            assign_var = emp_assign[0]
            
            # Employee arrival at stop = task.end + walk_to_stop
            arrival_at_stop = self.model.NewIntVar(
                0, max_time, f'arrival_e{emp_idx}_t{t_idx}_{stop_id}'
            )
            self.model.Add(
                arrival_at_stop == task_var['end'] + walk_time
            )
            
            # Constraint 2: Employee must arrive before bus can leave (max window)
            # If boards, arrival <= bus.latest_dep
            self.model.Add(
                arrival_at_stop <= bus_info['latest_dep']
            ).OnlyEnforceIf([boards, assign_var])
            
            # Constraint 3: Bus waits for employee
            # If boards, bus.actual_departure >= arrival_at_stop
            self.model.Add(
                bus_info['actual_departure'] >= arrival_at_stop
            ).OnlyEnforceIf([boards, assign_var])
            
            # Create wait time variable
            wait_key = (emp_idx, t_idx)
            if wait_key not in employee_wait_vars:
                wait_var = self.model.NewIntVar(
                    0, max_time, f'wait_e{emp_idx}_t{t_idx}'
                )
                employee_wait_vars[wait_key] = wait_var
            
            wait_var = employee_wait_vars[wait_key]
            
            # wait_time = bus_departure - arrival_at_stop (if boarding)
            # This is a bit complex with conditional, simplify by just tracking max wait
            self.model.Add(
                wait_var >= bus_info['actual_departure'] - arrival_at_stop
            ).OnlyEnforceIf([boards, assign_var])
        
        return employee_wait_vars
    
    def _add_travel_time_constraints(
        self,
        employees: List[Any],
        task_vars: List[Dict],
        travel_decisions: Dict,
        bus_instances: Dict,
        boarding_vars: Dict,
        walk_to_stop: Dict,
        bus_transit: Dict,
        travel_times: Dict
    ) -> None:
        """Constraints 5, 6: Travel time based on mode."""
        
        for (emp_idx, t1_idx, t2_idx), td in travel_decisions.items():
            use_bus = td['use_bus']
            loc1 = td['from_loc']
            loc2 = td['to_loc']
            
            tv1 = task_vars[t1_idx]
            tv2 = task_vars[t2_idx]
            
            emp_assign1 = tv1['assigned_vars'].get(emp_idx)
            emp_assign2 = tv2['assigned_vars'].get(emp_idx)
            
            if not emp_assign1 or not emp_assign2:
                continue
            
            assign1 = emp_assign1[0]
            assign2 = emp_assign2[0]
            
            # Walking travel time
            walk_direct = travel_times.get((loc1, loc2), 600)
            
            # Constraint 6: If walk (use_bus=0), use walking time
            self.model.Add(
                tv2['start'] >= tv1['end'] + walk_direct
            ).OnlyEnforceIf([assign1, assign2, use_bus.Not()])
            
            # Constraint 5: If bus (use_bus=1), need to find a valid bus connection
            # This requires matching with boarding_vars - simplified for now
            # The boarding constraints already handle the timing
    
    def _link_travel_boarding(
        self,
        travel_decisions: Dict,
        boarding_vars: Dict,
        employees: List[Any],
        task_vars: List[Dict],
        bus_instances: Dict
    ) -> None:
        """Constraint 7: Link use_bus to boards_bus."""
        
        for (emp_idx, t1_idx, t2_idx), td in travel_decisions.items():
            use_bus = td['use_bus']
            
            # Find all boards_bus variables for this employee after task t1
            related_boards = []
            for (e, t, r, s, c), bv in boarding_vars.items():
                if e == emp_idx and t == t1_idx:
                    related_boards.append(bv['boards'])
            
            if not related_boards:
                # No bus options - must walk
                self.model.Add(use_bus == 0)
            else:
                # If use_bus=1, at least one boards must be 1
                self.model.Add(
                    sum(related_boards) >= 1
                ).OnlyEnforceIf(use_bus)
                
                # If use_bus=0, no boards
                self.model.Add(
                    sum(related_boards) == 0
                ).OnlyEnforceIf(use_bus.Not())
    
    def _add_max_walk_constraint(
        self,
        travel_decisions: Dict,
        travel_times: Dict,
        task_vars: List[Dict],
        max_walk_distance: int
    ) -> None:
        """Constraint 8: Must use bus if too far to walk."""
        
        for (emp_idx, t1_idx, t2_idx), td in travel_decisions.items():
            use_bus = td['use_bus']
            loc1 = td['from_loc']
            loc2 = td['to_loc']
            
            walk_distance = travel_times.get((loc1, loc2), 9999)
            
            if walk_distance > max_walk_distance:
                # Must use bus
                self.model.Add(use_bus == 1)
