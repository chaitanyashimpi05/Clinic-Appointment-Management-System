from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from uuid import UUID
from typing import Optional, Literal
from app.schemas.user import UserResponse

class PatientProfileBase(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[Literal["Male", "Female", "Other"]] = None
    phone: Optional[str] = None
    medical_history: Optional[str] = None

class PatientProfileResponse(PatientProfileBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

class PatientProfileUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[Literal["Male", "Female", "Other"]] = None
    phone: Optional[str] = None
    medical_history: Optional[str] = None

class PatientDetailedResponse(BaseModel):
    id: UUID
    user: UserResponse
    date_of_birth: Optional[date]
    gender: Optional[str]
    phone: Optional[str]
    medical_history: Optional[str]

    model_config = ConfigDict(from_attributes=True)
