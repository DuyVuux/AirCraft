# Baseline Analysis: Greedy Strategy (EDF)
> **AUTO-KICKSTART**:
> - Role: `project-manager.get_role_prompt("be")`
> - Agent: `ccpm.read_ccpm_agent("code-analyzer")`

## 1. Algorithm Overview
The current baseline uses a **Greedy Constructive Heuristic** based on **Earliest Deadline First (EDF)**.

### Logic Flow
1.  **Sorting**: Sort all tasks by `Deadline ASC` (Primary) and `Priority ASC` (Secondary).
2.  **Assignment**: detailed in `_try_assign_task`.
    - Iterate through the sorted task list.
    - For each task, check all employees.
    - Filter capable employees (`_can_employee_do_task`).
    - Calculate earliest possible start time ($S_{earliest} = \max(T_{avail}, T_{travel}, T_{ready})$).
    - Assign to the employee who can start *earliest*.

## 2. Weakness Analysis

### 2.1. Critical Flaw: No Backtracking (Myopic)
- **Problem**: Once a task is assigned, it is never moved.
- **Scenario**:
    - Task A (Deadline 10:00) is assigned to Employee E1 (Best Fit).
    - Task B (Deadline 10:00, requires E1 strictly) comes next.
    - E1 is busy with A. Task B is **DROPPED**.
- **Optimization**: A non-greedy approach would realize E2 could have done Task A (even if starting slightly later), leaving E1 free for Task B.

### 2.2. Workload Balancing & Staff Minimization
- **Problem**: The greedy 'Earliest Start' rule tends to spread tasks across *all* available employees immediately to get them done ASAP.
- **Impact**: This contradicts the objective of **Minimizing Workforce**.
- **Better Approach**: We should try to "pack" tasks onto the *minimum* number of employees (Bin Packing problem equivalent) before activating a new employee.

### 2.3. Travel Time Inefficiency
- **Problem**: The heuristic picks the employee who can arrive *earliest*, which implicitly minimizes travel time locally, but not globally. It does not chain tasks based on location clusters.

## 3. Performance Complexity
- **Time Complexity**: $O(N \cdot M)$, where $N$ is tasks, $M$ is employees.
    - Very fast, suitable for real-time dispatching but poor for planning.
- **Quality**: Can easily miss the optimum by 20-30% in terms of dropped tasks and workforce usage.

## 4. Conclusion
The Greedy strategy serves as a good **Initial Solution Generator** but is insufficient for the optimization goals. It must be wrapped in a Local Search framework (LNS) to improve the solution quality iteratively.
