from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.doctors import router as doctors_router
from app.routers.patients import router as patients_router
from app.routers.appointments import router as appointments_router

__all__ = [
    "auth_router",
    "users_router",
    "doctors_router",
    "patients_router",
    "appointments_router",
]
