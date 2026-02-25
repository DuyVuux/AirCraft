# ✈️ AirCraft: Core App & Frontend

This directory contains the central **Data Management** and **User Interface** layers for the AirCraft Ground Staff Scheduling System. 

It is divided into two primary submodules:
1. `backend/`: A highly concurrent Python FastAPI application managing Database connections and User Authentication.
2. `frontend/`: A dynamic React application built with Vite and TypeScript.

---

## ⚙️ Backend (FastAPI)

The backend acts as the unified gatekeeper for all data mutations and system authentication.

### Key Features
- **JWT & Roles**: Implements access tokens and refresh tokens. Routes are secured via `require_role(["admin", "operator", "viewer"])`.
- **Relational Integrity**: Uses SQLAlchemy with `sqlite` (or Postgres in production). Database schemas are handled iteratively via Alembic Migrations.
- **Security Hardened**: Inbuilt CORS protections via Environment Variables, Rate Limiting (`slowapi`), and Payload Limits to defend against DDoS behaviors.

### Local Setup

```bash
cd backend

# Setup Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup Environment Configuration
cat <<EOF > .env
API_HOST=0.0.0.0
API_PORT=8002
JWT_SECRET_KEY=yoursecretkeythatisatleast32characterslong123
REFRESH_SECRET_KEY=yourrefreshsecretkeythatisatleast32chars123
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
DATABASE_URL=sqlite:///./aircraft.db
EOF

# Ensure the database schemas are up to date
alembic upgrade head

# Run the server
uvicorn main:app --env-file .env --reload --port 8002
```

Navigate to [http://localhost:8002/docs](http://localhost:8002/docs) to view the Swagger API Specification.

---

## 🖥️ Frontend (React & Vite)

The frontend provides real-time validation, Data uploading mechanics (CSV/Excel), map integrations, and interactive dashboards.

### Local Setup

Requires **Node.js 18+**.

```bash
cd frontend

# Tell the frontend where the FastAPI backend lives
echo "VITE_API_BASE_URL=http://localhost:8002" > .env

# Install Node modules
npm install

# Start the Hot-Module-Replacement Development server
npm run dev
```

Navigate to [http://localhost:5173](http://localhost:5173) to access the application.

---

## Testing

Backend unit tests can be executed sequentially:
```bash
cd backend
pytest tests/
```
