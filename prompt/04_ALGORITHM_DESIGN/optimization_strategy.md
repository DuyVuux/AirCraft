# Optimization Strategy: Hybrid Large Neighborhood Search (LNS)
> **AUTO-KICKSTART**:
> - Role: `project-manager.get_role_prompt("arch")`
> - Library: `context7.resolve-library-id("ortools/sat/python")`

## 1. Core Concept
To balance scalability and optimality, we design a **Hybrid Meta-heuristic**:
- **Global Search**: Large Neighborhood Search (LNS) framework.
- **Local Search/Repair**: Constraint Programming (CP-SAT) sub-solver.

The intuition is to "destroy" (unassign) a part of the schedule that looks suboptimal (or random), and "repair" (re-assign) it using an exact solver which can find the optimal arrangement for that smaller subset.

## 2. Algorithm Pseudocode

```python
def optimize(context):
    # Phase 1: Construction
    current_solution = GreedyStrategy(context).execute()
    best_solution = current_solution
    
    # Phase 2: LNS Loop
    temperature = INITIAL_TEMP
    
    while not stop_condition():
        # 1. Destroy
        destroyed_tasks, partial_solution = destroy_operator(current_solution)
        
        # 2. Repair (using CP-SAT or Regret Heuristic)
        new_solution = repair_operator(partial_solution, destroyed_tasks)
        
        # 3. Acceptance (Simulated Annealing)
        if accept(new_solution, current_solution, temperature):
            current_solution = new_solution
            if cost(new_solution) < cost(best_solution):
                best_solution = new_solution
                
        temperature *= COOLING_RATE
        
    return best_solution
```

## 3. Operators Design

### 3.1. Destroy Operators (removal strategies)
1.  **Random Ruin**: Randomly remove $k$ tasks. Good for diversification.
2.  **Worst Employment Ruin**: Remove tasks from employees with very low utilization (trying to eliminate that employee).
3.  **Related Ruin**: Remove a task and others "related" to it (same location, overlapping time window).
4.  **Long Travel Ruin**: Remove tasks that involve the longest travel times.

### 3.2. Repair Operators (re-insertion strategies)
1.  **Regret-k Insertion**: A greedy heuristic that prioritizes tasks that are "hard" to place (high difference between best and 2nd best option). Fast reconstruction.
2.  **CP-SAT Sub-solver**: Formulate the removed tasks and relevant employees as a small CSP problem and solve exactly.
    - *Constraint*: Fixed assignments in `partial_solution` are immutable.
    - *Variable*: Only `destroyed_tasks`.
    - *Timeout*: Strict scheduling limits (e.g., 500ms).

## 4. CP-SAT Model Design (OR-Tools)
Used within the Repair operator.

### Variables
- `IntervalVar[task]`: Start, Size, End.
- `Boolean[task, employee]`: Assignment matrix.

### Constraints
1.  **Alternative**: Each task performed by exactly one (or zero) employee.
    ```python
    model.Add(sum(is_assigned[t, e]) <= 1)
    ```
2.  **No Overlap**: Employee tasks cannot overlap (considering travel time).
    ```python
    model.AddNoOverlap(intervals_for_employee_e)
    ```
3.  **Route/Sequence cost**:
    - Modeled using `Circuit` constraint or simplified transition times if $N$ is small.

## 5. Parameter Tuning
- **Destroy Size**: 10-20% of tasks.
- **Time Limit**: 5 minutes total.
- **Weights**:
    - $W_{drop} = 1,000,000$ (Must serve).
    - $W_{staff} = 10,000$ (Minimize staff).
    - $W_{travel} = 1$ (Minimize travel).
