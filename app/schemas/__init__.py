from app.schemas.auth import UserRegister, Token, TokenData
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.doctor import DoctorProfileResponse, DoctorProfileUpdate, DoctorDetailedResponse
from app.schemas.patient import PatientProfileResponse, PatientProfileUpdate, PatientDetailedResponse
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate

__all__ = [
    "UserRegister",
    "Token",
    "TokenData",
    "UserResponse",
    "UserUpdate",
    "DoctorProfileResponse",
    "DoctorProfileUpdate",
    "DoctorDetailedResponse",
    "PatientProfileResponse",
    "PatientProfileUpdate",
    "PatientDetailedResponse",
    "AppointmentCreate",
    "AppointmentResponse",
    "AppointmentUpdate",
]
