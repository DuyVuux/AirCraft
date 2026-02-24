# ✈️ Aircraft Ground Staff Scheduling System

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)

A modern, full-stack web application for managing and inputting scheduling data for airport ground staff operations. This system enables efficient data entry through CSV/Excel file uploads, interactive forms, and a developer-friendly JSON editor.

---

## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Environment & Requirements](#-environment--requirements)
- [Development & Contribution Guidelines](#-development--contribution-guidelines)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Security / Best Practices](#-security--best-practices)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🎯 Project Overview

The **Aircraft Ground Staff Scheduling System** is designed to facilitate data input for airport ground crew scheduling operations. It addresses the complex requirements of managing:

- **Aircrafts** - Aircraft types, locations, time windows, and required maintenance tasks
- **Employees** - Ground staff with roles, levels, working times, and break schedules
- **Hubs** - Rest areas and central locations for staff
- **Bus Routes & Stops** - Internal airport transportation logistics
- **Distance/Time Matrices** - Travel times and task processing durations

### Target Users

- Airport Operations Managers
- Ground Crew Schedulers
- Data Entry Operators
- System Developers and Integrators

### Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, TypeScript, Vite, Material-UI (MUI) |
| **Backend** | FastAPI, Pydantic, Uvicorn |
| **Data Processing** | Pandas, PapaParse, XLSX |
| **Maps & Visualization** | React Leaflet, Turf.js |
| **Code Editor** | Monaco Editor |
| **Form Validation** | Zod, React Hook Form |

---

## ✨ Features

### Data Input Methods

- **📤 File Upload** - Support for CSV and Excel (.xlsx) files with automatic validation
- **✍️ Manual Input** - Interactive forms for each data category
- **🔧 Developer Mode** - JSON editor with syntax highlighting and schema validation

### Core Functionality

| Feature | Description |
|---------|-------------|
| **Template Management** | Download pre-configured templates for data entry |
| **Real-time Validation** | Instant feedback on data quality and format |
| **Data Preview** | Visual preview before submission |
| **Map Visualization** | Interactive maps for GPS coordinate management |
| **History Tracking** | Track and manage submitted datasets |
| **Multi-format Export** | Export data as JSON, CSV, or Excel |

### Editor Components

- **Roles & Tasks Editor** - Define employee roles and task mappings
- **Aircraft Editor** - Manage aircraft fleet and required tasks
- **Hub Management** - Configure rest areas and staff hubs
- **Employee Management** - Staff profiles with working schedules
- **Time Matrix Editor** - Task duration by role and skill level
- **Distance Matrix Editor** - Location-to-location travel times

---

## 📁 Project Structure

```
AirCraft/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/        # API endpoints
│   │   │       ├── upload.py      # File upload handling
│   │   │       ├── validate.py    # Data validation
│   │   │       ├── templates.py   # Template management
│   │   │       ├── submit.py      # Data submission
│   │   │       ├── datasets.py    # Dataset operations
│   │   │       ├── airports.py    # Airport data
│   │   │       └── map.py         # Map/GIS operations
│   │   └── services/          # Business logic
│   ├── data/                  # Stored data files
│   ├── main.py               # FastAPI application entry
│   └── requirements.txt      # Python dependencies
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── common/          # Shared UI components
│   │   │   ├── developer/       # JSON editor components
│   │   │   ├── editor/          # Data editor forms
│   │   │   ├── layout/          # Layout components
│   │   │   ├── scheduler/       # Scheduling views
│   │   │   ├── tabs/            # Tab components
│   │   │   └── upload/          # File upload components
│   │   ├── contexts/         # React Context providers
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Page components
│   │   │   ├── HomePage.tsx
│   │   │   ├── DeveloperPage.tsx
│   │   │   ├── ManualInputPage.tsx
│   │   │   ├── MapEditorPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   ├── ProductPage.tsx
│   │   │   └── SchedulerPage.tsx
│   │   ├── services/         # API service layer
│   │   ├── types/            # TypeScript definitions
│   │   ├── utils/            # Utility functions
│   │   └── styles/           # Global styles
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                      # Documentation
│   ├── USER_GUIDE.md
│   └── DEVELOPMENT_GUIDE.md
│
├── sample/                    # Sample data files
│   ├── input_sample.json         # Complete input example
│   ├── output_sample.json        # Expected output format
│   ├── flights.csv
│   ├── employees.csv
│   └── tasks.csv
│
├── templates/                 # CSV Templates
│   ├── aircrafts_template.csv
│   ├── employees_template.csv
│   ├── hubs_template.csv
│   ├── time_matrix_template.csv
│   ├── distance_matrix_template.csv
│   ├── bus_routes_template.csv
│   └── bus_stops_template.csv
│
├── start-all.sh              # Linux/Mac startup script
├── start-all.bat             # Windows startup script
├── requirements.txt          # Root Python dependencies
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- **Node.js** 18.0 or higher
- **npm** 9.0+ or **yarn** 1.22+
- **Python** 3.9 or higher
- **Git**

### Quick Start

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd AirCraft
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

#### 4. Start the Application

**Option A: Using startup scripts**

```bash
# Linux/Mac
chmod +x start-all.sh
./start-all.sh

# Windows
start-all.bat
```

**Option B: Manual startup**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8002
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

#### 5. Access the Application

- **Frontend**: http://localhost:5173 (or http://localhost:3000)
- **Backend API**: http://localhost:8002
- **API Documentation**: http://localhost:8002/docs

---

## ⚙️ Configuration

### Backend Configuration

The backend uses FastAPI with the following default settings:

| Setting | Default | Description |
|---------|---------|-------------|
| Host | `0.0.0.0` | Server bind address |
| Port | `8002` | Server port |
| Reload | `true` | Auto-reload on changes |
| CORS Origins | `localhost:3000`, `localhost:5173` | Allowed frontend origins |

### Frontend Configuration

Modify `frontend/vite.config.ts` for custom settings:

```typescript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8002'
    }
  }
})
```

### Environment Variables

Create `.env` files for environment-specific configuration:

```bash
# backend/.env
API_HOST=0.0.0.0
API_PORT=8002
DEBUG=true

# frontend/.env
VITE_API_BASE_URL=http://localhost:8002
```

---

## 📖 Usage

### File Upload Workflow

1. **Download Template** - Select data type and download CSV template
2. **Fill Data** - Enter data following the template format
3. **Upload File** - Drag & drop or select the file
4. **Validate** - System automatically validates data
5. **Preview** - Review the parsed data
6. **Confirm** - Submit to save data

### Manual Input

Navigate to **Manual Input** to access editors for:

- Roles & Tasks Mapping
- Aircraft Fleet Management
- Hub Configuration
- Employee Profiles
- Time/Distance Matrices

### Developer Mode (JSON Editor)

Access **Developer Mode** to:

- Paste or upload JSON data
- Edit with Monaco Editor (full IDE features)
- Validate against schema
- Load data into forms
- Export as JSON file

### Sample JSON Structure

```json
{
  "trackingId": "PLAN-2024-12-05-001",
  "aircrafts": [
    {
      "aircraftId": "VN-A320",
      "aType": { "id": "A320", "desc": "Airbus A320" },
      "location": {
        "locationId": "GATE-01",
        "locationType": "GATE",
        "longitude": 106.6588,
        "latitude": 10.8185
      },
      "timeWindow": {
        "start": "2024-12-05T08:00:00Z",
        "end": "2024-12-07T12:00:00Z"
      },
      "requiredTasks": [
        { "taskCode": "TASK_TIRE_CHECK", "minLevel": 1 }
      ]
    }
  ],
  "employees": [...],
  "hubs": [...],
  "busStops": [...],
  "busRoutes": [...],
  "matrixConfigs": {
    "distanceMatrix": [...],
    "timeMatrix": [...],
    "busTransitMatrix": [...],
    "walkingDistanceFromLocationToBusStop": [...]
  }
}
```

---

## 💻 Environment & Requirements

### Backend Requirements

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.104.1 | Web framework |
| uvicorn | 0.24.0 | ASGI server |
| pydantic | 2.5.0 | Data validation |
| pandas | 2.1.3 | Data processing |
| python-multipart | 0.0.6 | File uploads |
| openpyxl | 3.1.2 | Excel file handling |
| python-dateutil | 2.8.2 | Date parsing |

### Frontend Requirements

| Package | Version | Purpose |
|---------|---------|---------|
| react | 18.2.x | UI framework |
| typescript | 5.2.x | Type safety |
| vite | 5.0.x | Build tool |
| @mui/material | 5.14.x | UI components |
| react-leaflet | 4.2.x | Map visualization |
| @monaco-editor/react | 4.7.x | Code editor |
| zod | 3.22.x | Schema validation |
| react-hook-form | 7.48.x | Form management |

---

## 🤝 Development & Contribution Guidelines

### Code Standards

- **TypeScript**: Strict mode enabled, no `any` types
- **React**: Functional components with hooks
- **Python**: PEP 8 compliant, type hints

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `AircraftEditor.tsx` |
| Hooks | camelCase + `use` prefix | `useEmployeeData.ts` |
| Utils | camelCase | `formatDate.ts` |
| API Routes | snake_case | `upload_file` |

### Contribution Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes following code standards
4. Write or update tests
5. Commit with clear message (`git commit -m 'feat: add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Commit Message Format

```
<type>: <description>

[optional body]

Types: feat, fix, docs, style, refactor, test, chore
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest

# With coverage
python -m pytest --cov=app
```

### Frontend Tests

```bash
cd frontend

# Unit tests
npm run test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e
```

### API Testing

```bash
# Validate upload endpoint
python backend/test_upload_data.py

# Validate structure
python backend/validate_structure.py
```

---

## 🚀 Deployment

### Production Build

#### Frontend

```bash
cd frontend
npm run build
# Output: frontend/dist/
```

#### Backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8002 --workers 4
```

### Docker Deployment

```dockerfile
# Dockerfile.backend
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
```

### Recommended Production Stack

- **Reverse Proxy**: Nginx
- **Process Manager**: PM2 (frontend), Gunicorn (backend)
- **Container**: Docker + Docker Compose
- **CI/CD**: GitHub Actions / GitLab CI

---

## 🔒 Security / Best Practices

### Input Validation

- All file uploads are validated for type and size
- JSON schema validation using Pydantic and Zod
- CSV/Excel data sanitization before processing

### API Security

- CORS configured for specific origins only
- Input sanitization on all endpoints
- Rate limiting recommended for production

### Data Handling

- GPS coordinates validated within valid ranges
- Time formats enforce ISO 8601 standard
- IDs must be unique within their categories

### Recommendations

- [ ] Enable HTTPS in production
- [ ] Implement authentication (JWT/OAuth)
- [ ] Add request rate limiting
- [ ] Configure proper logging
- [ ] Set up monitoring and alerts

---

## ❓ Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| File format not valid | Wrong file extension | Use CSV (.csv) or Excel (.xlsx) only |
| Missing required column | Template mismatch | Download and use the latest template |
| ID already exists | Duplicate entry | Use unique IDs or delete existing entry |
| Invalid time format | Wrong format | Use ISO 8601 (e.g., `2024-12-05T08:00:00Z`) |
| GPS coordinates invalid | Out of range | Longitude: -180 to 180, Latitude: -90 to 90 |
| CORS error | Origin not allowed | Add frontend URL to backend CORS origins |
| JSON validation fails | Schema mismatch | Check `src/utils/jsonValidator.ts` for schema |

### Debug Tips

- **Frontend**: Use React DevTools and browser console
- **Backend**: Check FastAPI auto-reload logs
- **API Issues**: Test endpoints at http://localhost:8002/docs

---

## 🛣️ Roadmap

- [ ] **v1.1** - User authentication and authorization
- [ ] **v1.2** - Real-time collaborative editing
- [ ] **v1.3** - Scheduling algorithm integration
- [ ] **v2.0** - Multi-airport support
- [ ] **v2.1** - Mobile-responsive interface
- [ ] **v2.2** - Advanced reporting and analytics
- [ ] **v3.0** - Machine learning for schedule optimization

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For support, please contact:

- **Email**: support@example.com
- **Documentation**: [User Guide](docs/USER_GUIDE.md) | [Development Guide](docs/DEVELOPMENT_GUIDE.md)

---

<p align="center">
  Built with ❤️ for efficient airport operations
</p>
