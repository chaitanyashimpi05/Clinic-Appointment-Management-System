from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
# Import models package to register them with SQLAlchemy Base metadata prior to table creation
from app import models
from app.routers import (
    auth_router,
    users_router,
    doctors_router,
    patients_router,
    appointments_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on server startup
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup operations (if any) can go here on shutdown

# Instantiate FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend service for managing doctor schedules, patient profiles, and clinic appointment bookings with conflict prevention.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to trusted client domain URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(doctors_router)
app.include_router(patients_router)
app.include_router(appointments_router)

# Healthcheck root endpoint
@app.get("/")
def read_root():
    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "api_version": "1.0.0",
        "docs_url": "/docs"
    }
