import os

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field

from src import models, crud
from src.database import engine, get_db
from src.auth_utils import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
    get_password_hash,
    require_role,
    ALGORITHM,
    SECRET_KEY,
)
from app.api.routes import upload, validate, templates, submit, datasets, airports, map as map_router
from app.api import scheduler as scheduler_router
from app.exception_handlers import (
    validation_exception_handler,
    value_error_handler,
    generic_exception_handler,
)
from pydantic import ValidationError as PydanticValidationError

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Aircraft Web API",
    description="API for Aircraft Ground Staff Scheduling Data Input System",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(PydanticValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    allowed_origins_list = [origin.strip() for origin in allowed_origins_env.split(",")]
else:
    allowed_origins_list = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role: str = Field(pattern=r"^(admin|operator|viewer)$")


@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/api/auth/refresh")
@limiter.limit("10/minute")
async def refresh_token(request: Request, body: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_refresh_token(body.refresh_token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    new_access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": new_access_token, "token_type": "bearer"}


@app.post("/api/auth/register")
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    admin_check = require_role(["admin"])
    admin_check(current_user)

    existing = db.query(models.User).filter(models.User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    hashed = get_password_hash(body.password)
    new_user = models.User(
        username=body.username,
        hashed_password=hashed,
        role=body.role,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "role": new_user.role}


def require_operator():
    return require_role(["admin", "operator"])


def require_viewer():
    return require_role(["admin", "operator", "viewer"])


app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(validate.router, prefix="/api/validate", tags=["validate"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(
    submit.router,
    prefix="/api/submit",
    tags=["submit"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
app.include_router(airports.router, prefix="/api/airports", tags=["airports"])
app.include_router(map_router.router, prefix="/api/map", tags=["map"])
app.include_router(scheduler_router.router, prefix="/api/scheduler", tags=["scheduler"])


@app.get("/api/aircrafts/{aircraft_id}")
async def read_aircraft(
    aircraft_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    viewer_check = require_role(["admin", "operator", "viewer"])
    viewer_check(current_user)
    aircraft = crud.get_aircraft(db, aircraft_id)
    if not aircraft:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    return aircraft


@app.get("/")
async def root():
    return {"message": "Aircraft Web API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
