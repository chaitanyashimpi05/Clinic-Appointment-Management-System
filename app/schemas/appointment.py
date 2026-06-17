from pydantic import BaseModel, ConfigDict, Field, FieldSerializationInfo, field_serializer
from datetime import date, time, datetime
from uuid import UUID
from typing import Optional, Literal

class AppointmentCreate(BaseModel):
    doctor_id: UUID = Field(..., description="ID of the doctor to book with")
    appointment_date: date = Field(..., description="Date of the appointment (YYYY-MM-DD)")
    start_time: time = Field(..., description="Start time of the appointment (HH:MM:SS)")
    notes: Optional[str] = Field(None, description="Optional brief symptoms/notes for the doctor")

class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    appointment_date: date
    start_time: time
    end_time: time
    status: str
    notes: Optional[str]
    created_at: datetime

    # Custom serializer to convert time to string format (HH:MM:SS) in responses
    @field_serializer("start_time", "end_time")
    def serialize_time(self, dt_time: time, _info: FieldSerializationInfo) -> str:
        return dt_time.strftime("%H:%M:%S")

    model_config = ConfigDict(from_attributes=True)

class AppointmentUpdate(BaseModel):
    status: Optional[Literal["Scheduled", "Completed", "Cancelled"]] = None
    notes: Optional[str] = None
