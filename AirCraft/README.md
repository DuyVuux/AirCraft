# ✈️ Aircraft App (Backend & Frontend)

This directory contains the modernized, consolidated Web Application stack for the AirCraft System. 

## 🌐 System Interface Overview

The interface consists of a dynamic React/Vite Frontend paired with a robust FastAPI Backend. The recent Architecture Consolidation relocated scheduling duties completely into FastAPI, eliminating the need for a separate Flask application. The backend handles HTTP requests, authentication, data persistence via SQLAlchemy, and seamlessly dispatches CPU-bound algorithmic tasks.

---

## ⚙️ Backend (FastAPI)

Built for high concurrency, robust security, and developer joy.

### Key Capabilities
- **JWT Auth & Token Refresh**: Stateful login providing short-lived `access_token` and resilient 7-day `refresh_token` flows via `/api/auth/refresh`. Requires strictly enforced secrets (>32 characters).
- **Role-Based Access Control (RBAC)**: Handled seamlessly using the `require_role()` dependency decorator. Protects routes ensuring only active `Admin`, `Operator`, or `Viewer` statuses can perform state-mutating requests.
- **Secure by Default**: Integrates CORS configuration driven by Environment variables, `slowapi` rate limiting (e.g., max 5 login attempts / minute), and strict payload validation capping request bounds to 10MB to deflect DDoS behaviors.

### Database & Migrations
The app replaces raw JSON mutability with a transactional **SQLAlchemy** mapping, managing schemas for `Aircraft`, `Employee`, `MaintenanceTask`, and `ScheduleJob`. 

Database schema changes are governed strictly through **Alembic** migrations.
```bash
# To apply the latest schema state:
alembic upgrade head
```

### 🛣️ Important API Endpoints

| Method | Endpoint | Description |
|:---:|---|---|
| POST | `/api/auth/login` | Authenticate and retrieve JWT tokens. |
| POST | `/api/auth/refresh` | Obtain a new access token via Refresh Token. |
| POST | `/api/scheduler/run` | Main dispatch endpoint. Returns immediately while the `ProcessPoolExecutor` processes the LNS algorithmic resolution asynchronously. |
| GET | `/api/scheduler/status/{job_id}` | Poll the execution lifecycle (`PENDING` -> `RUNNING` -> `COMPLETED`/`FAILED`) for a dispatched task. |
| GET | `/api/scheduler/algorithms` | Retrieve available Optimization strategies available on the server. |

---

## 🖥️ Frontend (React & Vite)

### Technologies
- React 18 & TypeScript
- Vite Build Engine
- Standard JWT HTTP interceptors adding the `Authorization: Bearer <token>` to outbound requests consistently.

### Running the Frontend

Ensure `Node.js` (≥18) is installed.

```bash
cd frontend

# Install dependencies (populates node_modules)
npm install

# Start the Vite Hot-Module Replacement server
npm run dev
```

The app natively connects to the FastAPI backend running typically on port `8002`. Ensure your backend's `.env` specifically allows your frontend origin via `ALLOWED_ORIGINS` to satisfy CORS compliance.
