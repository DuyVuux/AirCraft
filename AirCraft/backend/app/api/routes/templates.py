from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "templates"


@router.get("/{template_type}")
async def download_template(template_type: str):
    """Download template file"""
    template_files = {
        "employees": "employees_template.csv",
        "aircrafts": "aircrafts_template.csv",
        "hubs": "hubs_template.csv",
        "bus-stops": "bus_stops_template.csv",
        "bus-routes": "bus_routes_template.csv",
        "time-matrix": "time_matrix_template.csv",
        "distance-matrix": "distance_matrix_template.csv",
    }
    
    if template_type not in template_files:
        return {"error": "Invalid template type"}
    
    file_path = TEMPLATES_DIR / template_files[template_type]
    
    if not file_path.exists():
        return {"error": "Template file not found"}
    
    return FileResponse(
        path=str(file_path),
        filename=template_files[template_type],
        media_type="text/csv"
    )

