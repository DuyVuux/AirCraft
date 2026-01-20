# Problem Formalization: Aircraft Maintenance Scheduling
> **AUTO-KICKSTART**:
> - Role: `project-manager.get_role_prompt("bsa")`
> - Context: `ccpm.context_read()`

## 1. Sets and Indices
- $T$: Set of Tasks, indexed by $i, j \in \{1, \dots, N\}$.
- $E$: Set of Employees, indexed by $k \in \{1, \dots, M\}$.
- $A$: Set of Aircrafts, indexed by $a$.
- $L$: Set of Locations.
- $C$: Set of Certificates/Skills.

## 2. Parameters
- $D_i$: Duration of task $i$.
- $TW_i = [ES_i, LF_i]$: Time Window (Earliest Start, Latest Finish) for task $i$.
- $Loc_i$: Location of task $i$ (Aircraft location).
- $Req_{i}$: Required skill level/certificates for task $i$.
- $Dist(l_1, l_2)$: Travel time between location $l_1$ and $l_2$.
- $Skill_k$: Set of skills/certificates possessed by employee $k$.
- $Work_k = \bigcup [Start_w, End_w]$: Working shifts of employee $k$.

## 3. Decision Variables
- $x_{ik} \in \{0, 1\}$: Binary variable, 1 if employee $k$ is assigned to task $i$.
- $s_i \in \mathbb{Z}_{\ge 0}$: Start time of task $i$.
- $e_i \in \mathbb{Z}_{\ge 0}$: End time of task $i$ ($e_i = s_i + D_i$).
- $y_k \in \{0, 1\}$: Binary variable, 1 if employee $k$ is used at all (has $\ge 1$ task).

## 4. Objective Function
Minimize the Weighted Sum of Costs:
$$ \min Z = W_1 \cdot \sum_{i \in T} (1 - \sum_{k \in E} x_{ik}) + W_2 \cdot \sum_{k \in E} y_k + W_3 \cdot \sum_{i,j,k} x_{ik}x_{jk} \cdot Dist(Loc_i, Loc_j) $$

Where:
- Term 1: **Dropped Tasks Penalty** (Highest Priority, Hard-ish constraint).
- Term 2: **Workforce Size** (Minimize number of active employees).
- Term 3: **Total Travel Time** (Operational efficiency).

## 5. Constraints

### 5.1. Assignment Constraints
Each task must be assigned to at most one employee (or dropped):
$$ \sum_{k \in E} x_{ik} \le 1, \quad \forall i \in T $$

### 5.2. Capability Constraints
Employee must have required skills:
$$ x_{ik} = 1 \implies Req_i \subseteq Skill_k $$

### 5.3. Time Window Constraints
Task must execute within aircraft availability:
$$ s_i \ge ES_i $$
$$ e_i \le LF_i $$

### 5.4. Working Hours Constraints
Task must occur within employee's shift:
$$ x_{ik} = 1 \implies [s_i, e_i] \subseteq Work_k $$

### 5.5. No-Overlap & Travel Time (Sequence Dependent)
If employee $k$ performs task $i$ and then task $j$ ($s_i < s_j$):
$$ x_{ik} = 1 \land x_{jk} = 1 \implies s_j \ge e_i + Dist(Loc_i, Loc_j) $$
*(Note: In CP, this is modeled as `NoOverlap` global constraint with transition matrix).*

### 5.6. Sequential Constraint (Per Aircraft)
If task $i$ and task $j$ are on the same aircraft $a$, and $i$ precedes $j$ in the list:
$$ s_j \ge e_i \quad (\text{If hard sequential constraint applies}) $$

## 6. Optimization Complexity
- **Class**: NP-Hard (Extension of VRPTW - Vehicle Routing Problem with Time Windows and Heterogeneous Fleet).
- **Scale**:
    - $N \approx 500-2000$ tasks.
    - $M \approx 50-200$ employees.
- **Implication**: Exact methods (MIP) will fail to converge quickly. **Meta-heuristics (LNS) or CP-SAT** are required.
