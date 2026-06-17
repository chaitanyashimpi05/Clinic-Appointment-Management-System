from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.doctor_profile import DoctorProfile
from app.schemas.doctor import DoctorDetailedResponse, DoctorProfileUpdate
from app.dependencies import get_current_active_user, require_doctor

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get("/", response_model=List[DoctorDetailedResponse])
def list_doctors(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Retrieve all doctor profiles and prefetch user details to avoid N+1 queries
    doctors = db.query(DoctorProfile).options(joinedload(DoctorProfile.user)).all()
    return doctors

@router.get("/{doctor_id}", response_model=DoctorDetailedResponse)
def get_doctor_profile(
    doctor_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).options(joinedload(DoctorProfile.user)).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    return doctor

@router.put("/me", response_model=DoctorDetailedResponse)
def update_doctor_profile(
    profile_update: DoctorProfileUpdate,
    current_doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    # Fetch doctor profile corresponding to the current logged-in doctor
    doctor_profile = db.query(DoctorProfile).filter(DoctorProfile.id == current_doctor.id).first()
    if not doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found."
        )

    # Perform updates
    if profile_update.specialization is not None:
        doctor_profile.specialization = profile_update.specialization
    if profile_update.bio is not None:
        doctor_profile.bio = profile_update.bio
    if profile_update.consultation_fee is not None:
        doctor_profile.consultation_fee = profile_update.consultation_fee
    if profile_update.availability_start is not None:
        doctor_profile.availability_start = profile_update.availability_start
    if profile_update.availability_end is not None:
        doctor_profile.availability_end = profile_update.availability_end

    db.commit()
    db.refresh(doctor_profile)
    return doctor_profile
