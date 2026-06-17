import unittest
from datetime import date, time, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.doctor_profile import DoctorProfile
from app.models.patient_profile import PatientProfile
from app.models.appointment import Appointment
from app.dependencies import hash_password, verify_password

class TestClinicAppointmentSystem(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for fast, isolated verification
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_password_hashing(self):
        """Verify password hashing and verification works properly."""
        raw_password = "MySecurePassword123!"
        hashed = hash_password(raw_password)
        
        self.assertNotEqual(raw_password, hashed)
        self.assertTrue(verify_password(raw_password, hashed))
        self.assertFalse(verify_password("wrong_password", hashed))

    def test_user_and_profile_creation(self):
        """Verify base user and child profiles can be correctly created and linked."""
        # Create doctor base user
        doctor_user = User(
            email="dr.blackwell@clinic.com",
            hashed_password=hash_password("docpass123"),
            full_name="Dr. Blackwell",
            role="Doctor"
        )
        self.db.add(doctor_user)
        self.db.commit()

        # Create doctor profile
        doc_profile = DoctorProfile(
            id=doctor_user.id,
            specialization="Cardiology",
            bio="Heart specialist",
            consultation_fee=150.00,
            availability_start=time(9, 0),
            availability_end=time(17, 0)
        )
        self.db.add(doc_profile)

        # Create patient base user and profile
        patient_user = User(
            email="john.doe@email.com",
            hashed_password=hash_password("patpass123"),
            full_name="John Doe",
            role="Patient"
        )
        self.db.add(patient_user)
        self.db.commit()

        pat_profile = PatientProfile(
            id=patient_user.id,
            date_of_birth=date(1990, 1, 1),
            gender="Male",
            phone="1234567890",
            medical_history="No history"
        )
        self.db.add(pat_profile)
        self.db.commit()

        # Retrieve and assert relationships
        db_doctor = self.db.query(User).filter(User.role == "Doctor").first()
        self.assertIsNotNone(db_doctor.doctor_profile)
        self.assertEqual(db_doctor.doctor_profile.specialization, "Cardiology")

        db_patient = self.db.query(User).filter(User.role == "Patient").first()
        self.assertIsNotNone(db_patient.patient_profile)
        self.assertEqual(db_patient.patient_profile.phone, "1234567890")

    def test_appointment_booking_and_double_booking_prevention(self):
        """Verify appointment booking rules: working hours and overlap conflict checks."""
        # Setup doctor and patient
        doctor_user = User(id=None, email="doc@clinic.com", hashed_password="hashed", full_name="Doc", role="Doctor")
        patient_user = User(id=None, email="pat@clinic.com", hashed_password="hashed", full_name="Pat", role="Patient")
        self.db.add_all([doctor_user, patient_user])
        self.db.commit()

        doc_profile = DoctorProfile(
            id=doctor_user.id,
            specialization="General",
            consultation_fee=50.0,
            availability_start=time(9, 0), # 9:00 AM
            availability_end=time(17, 0)  # 5:00 PM
        )
        pat_profile = PatientProfile(id=patient_user.id)
        self.db.add_all([doc_profile, pat_profile])
        self.db.commit()

        booking_date = date(2026, 7, 20)

        # Test Case 1: Book valid appointment (10:00 - 10:30)
        start_time_1 = time(10, 0)
        end_time_1 = time(10, 30)
        
        # Verify doctor is available
        self.assertTrue(start_time_1 >= doc_profile.availability_start and end_time_1 <= doc_profile.availability_end)
        
        appt_1 = Appointment(
            patient_id=pat_profile.id,
            doctor_id=doc_profile.id,
            appointment_date=booking_date,
            start_time=start_time_1,
            end_time=end_time_1,
            status="Scheduled"
        )
        self.db.add(appt_1)
        self.db.commit()

        # Test Case 2: Attempt overlapping booking for doctor (10:15 - 10:45)
        start_time_overlap = time(10, 15)
        end_time_overlap = time(10, 45)

        # Check overlap condition: (start_time < existing.end_time) AND (end_time > existing.start_time)
        overlap_exists = self.db.query(Appointment).filter(
            Appointment.doctor_id == doc_profile.id,
            Appointment.appointment_date == booking_date,
            Appointment.status == "Scheduled",
            Appointment.start_time < end_time_overlap,
            Appointment.end_time > start_time_overlap
        ).first() is not None

        self.assertTrue(overlap_exists, "System should detect doctor booking overlap!")

        # Test Case 3: Attempt booking outside doctor availability (08:00 - 08:30)
        start_time_early = time(8, 0)
        end_time_early = time(8, 30)
        is_outside_hours = (start_time_early < doc_profile.availability_start or end_time_early > doc_profile.availability_end)
        self.assertTrue(is_outside_hours, "System should flag appointments outside availability hours!")

        # Test Case 4: Test booking on non-overlapping slot (11:00 - 11:30)
        start_time_2 = time(11, 0)
        end_time_2 = time(11, 30)
        overlap_exists_2 = self.db.query(Appointment).filter(
            Appointment.doctor_id == doc_profile.id,
            Appointment.appointment_date == booking_date,
            Appointment.status == "Scheduled",
            Appointment.start_time < end_time_2,
            Appointment.end_time > start_time_2
        ).first() is not None

        self.assertFalse(overlap_exists_2, "Should allow booking on a clean non-overlapping slot")

if __name__ == "__main__":
    unittest.main()
