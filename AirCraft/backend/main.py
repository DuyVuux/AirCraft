from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import upload, validate, templates, submit, datasets, airports, map as map_router

app = FastAPI(
    title="Aircraft Web API",
    description="API for Aircraft Ground Staff Scheduling Data Input System",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(validate.router, prefix="/api/validate", tags=["validate"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(submit.router, prefix="/api/submit", tags=["submit"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
app.include_router(airports.router, prefix="/api/airports", tags=["airports"])
app.include_router(map_router.router, prefix="/api/map", tags=["map"])


@app.get("/")
async def root():
    return {"message": "Aircraft Web API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
