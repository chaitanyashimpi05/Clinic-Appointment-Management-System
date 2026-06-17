from sqlalchemy import Column, Date, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    # Primary key that references the base users table
    id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True) # 'Male', 'Female', 'Other'
    phone = Column(String, nullable=True)
    medical_history = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
