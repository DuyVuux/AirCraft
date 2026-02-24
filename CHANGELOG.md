# Changelog

All notable changes from the Audit Remediation effort.

## [1.0.0-beta] - 2026-02-24

### Security (EPIC 01)
- JWT secret validation: RuntimeError if missing or < 32 chars
- Refresh token (7-day expiry) + `/api/auth/refresh` endpoint
- RBAC with `require_role()` decorator (admin/operator/viewer)
- Rate limiting: slowapi (FastAPI) + flask-limiter (Flask)
- Input validation: Pydantic models + 10MB payload limit
- CORS hardened: explicit methods, headers, env-configurable origins

### Algorithm (EPIC 02, 03)
- Pairwise travel time constraints (3-case window logic)
- Distance matrix integration via OptimizationContext
- Objective function: `dropped×100M + active_employees×10K`
- Break interval name collision fix
- LNS consolidation: deleted duplicate, kept LNSSolver
- Simulated Annealing enabled (Boltzmann acceptance, cooling=0.99)
- Cost function with travel time from distance_matrix
- Greedy strategy: topological sort for dependencies + break times

### Dependencies (EPIC 04)
- requirements.txt for both backends (version pinned)
- Enhanced .env.example files
- Frontend package.json: engines ≥18, @types to devDependencies

### Database (EPIC 05)
- Alembic migration tool for both FastAPI and Flask backends
- PostgreSQL-ready: pool_size, max_overflow, pool_pre_ping
- Indexes on task_code and status columns
- Job lifecycle: PENDING → RUNNING → COMPLETED/FAILED
- CRUD flush pattern (caller controls transaction)

### API Consolidation (EPIC 06)
- FastAPI scheduler router (POST /run, GET /status/{id}, GET /algorithms)
- ScheduleJob model added to backend
- ProcessPoolExecutor for CPU-bound solver (4 workers)
- Unified exception handlers (422/400/500 JSON format)
- Frontend JWT auth headers on all API calls

### Code Quality (EPIC 07)
- Archived dead code: legacy solver, scripts, unused frontend pages
- Replaced all print() with structured logging (logger.py)
- pyproject.toml with Ruff and MyPy configuration

### Testing (EPIC 08)
- Organized test structure: unit/ integration/ fixtures/
- conftest.py with factory fixtures
- CP-SAT constraint tests, LNS solver tests, time utils tests
- Backend scheduler API tests
- 58 total tests passing
