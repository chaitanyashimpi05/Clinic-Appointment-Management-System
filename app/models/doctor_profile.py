from sqlalchemy import Column, String, Text, Numeric, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    # Primary key that references the base users table
    id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    specialization = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    consultation_fee = Column(Numeric(10, 2), nullable=False)
    
    # Store daily slot boundaries as Time objects
    availability_start = Column(Time, nullable=False, default="09:00:00")
    availability_end = Column(Time, nullable=False, default="17:00:00")

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
