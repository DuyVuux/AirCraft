# Aircraft Web Backend

FastAPI backend for Aircraft Web Data Input System.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/upload/employees` - Upload employees CSV/Excel
- `POST /api/upload/aircrafts` - Upload aircrafts CSV/Excel
- `POST /api/upload/hubs` - Upload hubs CSV/Excel
- `POST /api/upload/time-matrix` - Upload time matrix CSV/Excel
- `POST /api/upload/distance-matrix` - Upload distance matrix CSV/Excel
- `POST /api/validate/json` - Validate JSON data
- `GET /api/templates/{type}` - Download template file
- `POST /api/submit` - Submit final JSON data

## Development

API documentation available at: `http://localhost:8000/docs`

