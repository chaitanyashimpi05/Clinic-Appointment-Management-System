from pydantic import BaseModel, ConfigDict, Field, FieldSerializationInfo, field_serializer
from datetime import time
from uuid import UUID
from typing import Optional
from app.schemas.user import UserResponse

class DoctorProfileBase(BaseModel):
    specialization: str = Field(..., min_length=2)
    bio: Optional[str] = None
    consultation_fee: float = Field(..., ge=0)
    availability_start: time = Field(default="09:00:00")
    availability_end: time = Field(default="17:00:00")

class DoctorProfileResponse(DoctorProfileBase):
    id: UUID

    # Custom serializer to convert time to string format (HH:MM:SS) in responses
    @field_serializer("availability_start", "availability_end")
    def serialize_time(self, dt_time: time, _info: FieldSerializationInfo) -> str:
        return dt_time.strftime("%H:%M:%S")

    model_config = ConfigDict(from_attributes=True)

class DoctorProfileUpdate(BaseModel):
    specialization: Optional[str] = Field(None, min_length=2)
    bio: Optional[str] = None
    consultation_fee: Optional[float] = Field(None, ge=0)
    availability_start: Optional[time] = None
    availability_end: Optional[time] = None

class DoctorDetailedResponse(BaseModel):
    id: UUID
    user: UserResponse
    specialization: str
    bio: Optional[str]
    consultation_fee: float
    availability_start: time
    availability_end: time

    @field_serializer("availability_start", "availability_end")
    def serialize_time(self, dt_time: time, _info: FieldSerializationInfo) -> str:
        return dt_time.strftime("%H:%M:%S")

    model_config = ConfigDict(from_attributes=True)
