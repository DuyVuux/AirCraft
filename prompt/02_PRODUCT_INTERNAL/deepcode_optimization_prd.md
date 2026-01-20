# PRD: DeepCode Optimization Technical Package
> **AUTO-KICKSTART**:
> - Role: `project-manager.get_role_prompt("rte")`
> - Template: `project-manager.get_artifact_template("user_story")`

## 1. Goal
Prepare a COMPLETE, PRECISE, and RESEARCH-GRADE technical package that enables DeepCode to analyze, improve, and outperform the greedy baseline algorithm for Aircraft Maintenance Scheduling.

## 2. Scope
1.  **Problem Formalization**: Define decision variables, objective function, and constraints.
2.  **Input/Output Specification**: Define data formats and assumptions.
3.  **Baseline Greedy Algorithm**: Describe the current algorithm, complexity, and weaknesses.
4.  **Search Space Analysis**: Characterize the solution landscape and neighborhood moves.
5.  **Improvement Strategies**: Propose optimization strategies (Local Search, Metaheuristics, etc.).
6.  **Evaluation Protocol**: Define metrics and benchmarks.
7.  **DeepCode Context**: Generate a self-contained summary for DeepCode.

## 3. Success Criteria
-   A complete technical package is generated in `prompt/`.
-   The context is sufficient for DeepCode to understand and improve the algorithm.
-   The proposed algorithm (LNS) is mathematically sound and addresses the greedy weaknesses.

## 4. Technical Requirements
-   **Algorithm**: Hybrid Large Neighborhood Search (LNS).
-   **Solver**: Google OR-Tools (CP-SAT) for repair operators.
-   **Language**: Python 3.10+.
-   **Architecture**: Hexagonal (clean separation of Model, Solver, and Context).

## 5. Deliverables
-   `prompt/01_ARCHITECTURAL_RUNWAY/architecture.md`
-   `prompt/03_BUSINESS_DOMAIN/problem_formalization.md`
-   `prompt/04_ALGORITHM_DESIGN/baseline_analysis.md`
-   `prompt/04_ALGORITHM_DESIGN/optimization_strategy.md`
