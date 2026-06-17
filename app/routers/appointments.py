from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.doctor_profile import DoctorProfile
from app.models.patient_profile import PatientProfile
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.dependencies import get_current_active_user, require_patient, require_any_role

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    appointment_in: AppointmentCreate,
    current_patient: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    # 1. Compute end time (default to 30 minutes slot duration)
    try:
        dummy_date = appointment_in.appointment_date
        dummy_start_dt = datetime.combine(dummy_date, appointment_in.start_time)
        dummy_end_dt = dummy_start_dt + timedelta(minutes=30)
        
        # Guard against day roll-over if booked too late
        if dummy_end_dt.date() != dummy_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment slot cannot span across midnight."
            )
        end_time = dummy_end_dt.time()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid appointment date or start time format."
        )

    # Begin transaction lock to prevent race conditions.
    # We query the doctor's profile and lock it. Any concurrent booking attempts for this doctor
    # will wait until this transaction commits or aborts.
    doctor_profile = db.query(DoctorProfile).filter(
        DoctorProfile.id == appointment_in.doctor_id
    ).with_for_update().first()

    if not doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found."
        )

    # 2. Check if booking is within doctor's availability window
    if appointment_in.start_time < doctor_profile.availability_start or end_time > doctor_profile.availability_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested slot {appointment_in.start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} is outside the doctor's available hours ({doctor_profile.availability_start.strftime('%H:%M')} - {doctor_profile.availability_end.strftime('%H:%M')})."
        )

    # 3. Check for Doctor Double-Booking
    # Look for existing scheduled appointments that overlap with the requested slot
    overlapping_doctor_booking = db.query(Appointment).filter(
        Appointment.doctor_id == appointment_in.doctor_id,
        Appointment.appointment_date == appointment_in.appointment_date,
        Appointment.status == "Scheduled",
        Appointment.start_time < end_time,
        Appointment.end_time > appointment_in.start_time
    ).first()

    if overlapping_doctor_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The doctor is already booked during this time slot."
        )

    # 4. Check for Patient Double-Booking
    # Ensure patient is not scheduled for another appointment at the same time
    overlapping_patient_booking = db.query(Appointment).filter(
        Appointment.patient_id == current_patient.id,
        Appointment.appointment_date == appointment_in.appointment_date,
        Appointment.status == "Scheduled",
        Appointment.start_time < end_time,
        Appointment.end_time > appointment_in.start_time
    ).first()

    if overlapping_patient_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an appointment scheduled during this time slot."
        )

    # 5. Save the booking
    new_appointment = Appointment(
        patient_id=current_patient.id,
        doctor_id=appointment_in.doctor_id,
        appointment_date=appointment_in.appointment_date,
        start_time=appointment_in.start_time,
        end_time=end_time,
        notes=appointment_in.notes,
        status="Scheduled"
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Appointment)

    # Enforce RBAC filtering:
    # - Admin can see all appointments
    # - Doctor can see only their own appointments
    # - Patient can see only their own appointments
    if current_user.role == "Doctor":
        query = query.filter(Appointment.doctor_id == current_user.id)
    elif current_user.role == "Patient":
        query = query.filter(Appointment.patient_id == current_user.id)
    
    if status_filter:
        query = query.filter(Appointment.status == status_filter)

    # Order by date and time
    return query.order_by(Appointment.appointment_date.desc(), Appointment.start_time.asc()).all()


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment_status(
    appointment_id: UUID,
    update_in: AppointmentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # RBAC Access Validation:
    # - Admin: Can modify any appointment
    # - Patient: Can cancel their own appointment
    # - Doctor: Can cancel or complete their own appointment
    if current_user.role == "Patient":
        if appointment.patient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to edit this appointment."
            )
        # Patients can only update status to Cancelled
        if update_in.status and update_in.status != "Cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patients are only permitted to cancel their appointments."
            )
            
    elif current_user.role == "Doctor":
        if appointment.doctor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to edit this appointment."
            )
        # Doctors cannot book or change to invalid status
        if update_in.status and update_in.status not in ["Cancelled", "Completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctors can only set appointments to Cancelled or Completed."
            )

    # Perform updates
    if update_in.status is not None:
        appointment.status = update_in.status
    if update_in.notes is not None:
        appointment.notes = update_in.notes

    db.commit()
    db.refresh(appointment)
    return appointment
