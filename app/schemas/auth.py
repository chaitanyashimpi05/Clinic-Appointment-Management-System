from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from uuid import UUID

class UserRegister(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")
    full_name: str = Field(..., min_length=2, description="User's full name")
    role: Literal["Admin", "Doctor", "Patient"] = Field(..., description="Role must be Admin, Doctor, or Patient")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        # Simple email validation regex to avoid extra package dependencies
        import re
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, value):
            raise ValueError("Invalid email address format")
        return value.lower()

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    role: Optional[str] = None
