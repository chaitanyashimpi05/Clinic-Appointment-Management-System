from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional

class UserBase(BaseModel):
    email: str
    full_name: str
    role: str
    is_active: bool

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    # Pydantic v2 configuration to allow parsing from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2)
    email: Optional[str] = None
