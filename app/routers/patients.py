from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.patient_profile import PatientProfile
from app.schemas.patient import PatientDetailedResponse, PatientProfileUpdate
from app.dependencies import require_patient, require_admin_or_doctor

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/", response_model=List[PatientDetailedResponse])
def list_patients(
    current_staff: User = Depends(require_admin_or_doctor),
    db: Session = Depends(get_db)
):
    # Retrieve all patient profiles and prefetch base user details
    patients = db.query(PatientProfile).options(joinedload(PatientProfile.user)).all()
    return patients

@router.get("/{patient_id}", response_model=PatientDetailedResponse)
def get_patient_profile(
    patient_id: UUID,
    current_staff: User = Depends(require_admin_or_doctor),
    db: Session = Depends(get_db)
):
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).options(joinedload(PatientProfile.user)).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    return patient

@router.put("/me", response_model=PatientDetailedResponse)
def update_patient_profile(
    profile_update: PatientProfileUpdate,
    current_patient: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    # Fetch patient profile corresponding to the current logged-in user
    patient_profile = db.query(PatientProfile).filter(PatientProfile.id == current_patient.id).first()
    if not patient_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found."
        )

    # Perform updates
    if profile_update.date_of_birth is not None:
        patient_profile.date_of_birth = profile_update.date_of_birth
    if profile_update.gender is not None:
        patient_profile.gender = profile_update.gender
    if profile_update.phone is not None:
        patient_profile.phone = profile_update.phone
    if profile_update.medical_history is not None:
        patient_profile.medical_history = profile_update.medical_history

    db.commit()
    db.refresh(patient_profile)
    return patient_profile
