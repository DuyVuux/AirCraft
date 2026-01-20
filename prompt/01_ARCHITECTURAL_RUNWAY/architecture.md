# Architecture: Optimization Engine
> **AUTO-KICKSTART**:
> - Role: `project-manager.get_role_prompt("arch")`
> - Workflow: `project-manager.get_workflow_steps("development")`

## 1. System Overview
The **Optimization Engine** is a core component responsible for assigning maintenance tasks to employees to minimize workforce size while satisfying all operational constraints. It follows a **Hexagonal Architecture (Ports & Adapters)** to decouple the core optimization logic from the data sources and external triggers.

## 2. Component Diagram

```mermaid
graph TD
    subgraph "Core Domain"
        Model[Optimization Model]
        Constraints[Constraint Provider]
        Objective[Objective Function]
        Solver[Solver Strategy (LNS/CP)]
    end

    subgraph "Input Port"
        Context[Context Builder]
        Loader[Data Loader]
    end

    subgraph "Output Port"
        Solution[Solution Extractor]
        Metrics[Performance Metrics]
    end

    API[Scheduler API] --> Context
    Context --> Model
    Model --> Solver
    Constraints --> Solver
    Objective --> Solver
    Solver --> Solution
    Solution --> API
```

## 3. Core Components

### 3.1. Context Builder
- **Responsibility**: Converts raw JSON input (`AirCraft`, `Employee`, `MatrixConfig`) into optimized internal data structures.
- **Key Optimization**: Pre-calculation of travel time matrices and capability lookups (Bitmasking for certificates).

### 3.2. Optimization Model
- **Variables**:
    - `X[task, employee]`: Boolean, true if task is assigned to employee.
    - `Start[task]`: Integer, start time of the task.
    - `End[task]`: Integer, end time of the task.
- **State**: Maintains the current state of the solution, including calculating potential violations.

### 3.3. Solver Strategy (Hybrid LNS)
- **Primary Strategy**: **Large Neighborhood Search (LNS)**.
    - Uses a connection to a **CP-SAT Solver** (e.g., Google OR-Tools) for exploring sub-neighborhoods.
    - Uses **Meta-heuristics** (Simulated Annealing) for accepting/rejecting moves.
- **Fallback**: Greedy Construction Heuristic (Enhanced) for initial feasible solution generation.

### 3.4. Constraint Provider
- Encapsulates all Hard and Soft constraints.
- decoupling the "Rules" from the "Solver" logic, allowing dynamic rule configuration.

## 4. Integration Strategy
The engine is designed to be stateless:
1.  **Input**: `OptimizationRequest` (Snapshot of world state).
2.  **Process**: Pure function execution (Deterministic given seed).
3.  **Output**: `OptimizationResponse` (List of assignments and dropped tasks).

## 5. Technology Stack
- **Language**: Python 3.10+ (for rich scientific libraries).
- **Libraries**:
    - `ortools`: For CP-SAT solving capabilities.
    - `numpy`: For fast matrix operations (Time/Distance lookups).
    - `pydantic`: For rigorous data validation.
