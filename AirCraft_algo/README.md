# 🧠 AirCraft Optimization Engine

The core algorithmic component of the AirCraftPort system. It uses advanced mathematical optimization to schedule and assign maintenance tasks to ground staff efficiently.

## 🏗️ Architecture overview

The algorithm engine has been completely decoupled from the legacy Flask API and is now executed as a computationally intensive Python module. It is consumed by the main FastAPI backend using `ProcessPoolExecutor`, which allows the CPU-bound solver logic to run asynchronously without blocking the asynchronous event loop of the web server.

## 💡 Core Algorithms

The engine leverages **Google OR-Tools (CP-SAT)** as its primary solver, utilizing a suite of advanced heuristics:

1. **Hybrid LNS (Large Neighborhood Search)**
   - The primary solver loop uses an LNS strategy tailored to vehicle/personnel routing constraints.
   - Modifies existing feasible solutions by destroying parts of the neighborhood and repairing them iteratively.
   - Interacts seamlessly with the CP-SAT engine for sub-problem optimization.

2. **Simulated Annealing (SA) Integration**
   - Incorporated into the LNS accept/reject criteria.
   - Utilizes a *Boltzmann acceptance probability* (`exp(-delta/T)`) with a strict cooling rate (`0.99`).
   - Dynamically evaluates a newly calculated Cost Function that penalizes dropped tasks (100M penalty) and optimizes for overall active employees (10K penalty) and travel time constraints driven by the distance matrix.

3. **Greedy Fallback Strategy**
   - Acts as a fallback and generates initialization state for the LNS solver.
   - Performs topological sorting to ensure task dependencies (Precedences) are naturally respected during initial assignments.
   - Automatically avoids scheduled employee break windows using continuous interval tracking.

## 🔒 Constraints Handled

- **Pairwise Travel Time:** Incorporates the `distance_matrix` directly into the `OptimizationContext` to ensure employees travel realistically between gates.
- **Precedence (Dependencies):** Tasks that must be completed securely before others (e.g., Engine Check -> Oil Refill).
- **Break Time Avoidance:** Enforces `NoOverlap2D` constraints, adjusting greedy scheduling logic (`_adjust_for_breaks()`) so no tasks occur while staff are on mandatory breaks.
- **Certificate Verification:** Employees lacking necessary skill certification levels for particular tasks are forcefully ignored in the assignment scope.

## 🧪 Running Tests

The algorithm suite comes with strict test coverage ensuring zero regressions on the constraints.

```bash
# From the root directory or algorithm directory
pytest tests/
# or specifically for algo:
pytest AirCraft_algo/tests/
```

This verifies:
- CP-SAT model generations.
- Time utility functionalities.
- LNS and Greedy Strategy deterministic outputs.
