import sys
import os
import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from services.patient_service import PatientService
from services.staff_service import StaffService
from services.surgeon_service import SurgeonService
from services.operating_room_service import OperatingRoomService
from services.surgery_service import SurgeryService
from services.surgery_equipment_service import SurgeryEquipmentService
from services.surgery_equipment_usage_service import SurgeryEquipmentUsageService
from services.surgery_room_assignment_service import SurgeryRoomAssignmentService
from services.appointment_service import AppointmentService
from services.surgery_staff_assignment_service import SurgeryStaffAssignmentService
from models import (
    Base,
    Patient,
    Surgeon,
    OperatingRoom,
    SurgeryEquipment,
    SurgeryStaffAssignment,
    Staff,
)

# Removed: from db_config import get_db # No longer needed as services take db session directly

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)


# Helper function to get the latest ID for a model (Not used currently, but can be useful)
# def get_latest_id(db, model):
#     instance = db.query(model).order_by(model.id.desc()).first()
#     return instance.id if instance else None

# Refactor existing test logic into pytest functions


def test_patient_service(db_session):
    print("\n--- Testing PatientService ---")
    patient_data = {
        "name": "Test Patient",
        "dob": date(1995, 7, 20),
        "contact_info": "555-0000",
        "privacy_consent": True,
    }
    patient_id = PatientService.create_patient(db_session, patient_data)
    assert patient_id is not None

    patient = PatientService.get_patient(db_session, patient_id)
    assert patient is not None
    print("Fetched Patient:", patient)

    update_data = {"contact_info": "555-1111"}
    updated = PatientService.update_patient(db_session, patient_id, update_data)
    assert updated is True
    updated_patient = PatientService.get_patient(db_session, patient_id)
    assert updated_patient.contact_info == "555-1111"

    deleted = PatientService.delete_patient(db_session, patient_id)
    assert deleted is True
    deleted_patient = PatientService.get_patient(db_session, patient_id)
    assert deleted_patient is None


def test_staff_service(db_session):
    print("\n--- Testing StaffService ---")
    staff_data = {
        "name": "Test Staff",
        "role": "Nurse",
        "contact_info": "555-2222",
        "specialization": "General",
        "availability": True,
    }
    staff_id = StaffService.create_staff(db_session, staff_data)
    assert staff_id is not None

    staff = StaffService.get_staff(db_session, staff_id)
    assert staff is not None
    print("Fetched Staff:", staff)

    update_data = {"contact_info": "555-3333"}
    updated = StaffService.update_staff(db_session, staff_id, update_data)
    assert updated is True
    updated_staff = StaffService.get_staff(db_session, staff_id)
    assert updated_staff.contact_info == "555-3333"

    deleted = StaffService.delete_staff(db_session, staff_id)
    assert deleted is True
    deleted_staff = StaffService.get_staff(db_session, staff_id)
    assert deleted_staff is None


def test_surgeon_service(db_session):
    print("\n--- Testing SurgeonService ---")
    surgeon_data = {
        "name": "Test Surgeon",
        "contact_info": "surgeon@example.com",
        "specialization": "Cardiology",
        "credentials": "MD, PhD",
        "availability": True,
    }
    surgeon_id = SurgeonService.create_surgeon(db_session, surgeon_data)
    assert surgeon_id is not None

    surgeon = SurgeonService.get_surgeon(db_session, surgeon_id)
    assert surgeon is not None
    print("Fetched Surgeon:", surgeon)

    update_data = {"contact_info": "surgeon2@example.com"}
    updated = SurgeonService.update_surgeon(db_session, surgeon_id, update_data)
    assert updated is True
    updated_surgeon = SurgeonService.get_surgeon(db_session, surgeon_id)
    assert updated_surgeon.contact_info == "surgeon2@example.com"

    deleted = SurgeonService.delete_surgeon(db_session, surgeon_id)
    assert deleted is True
    deleted_surgeon = SurgeonService.get_surgeon(db_session, surgeon_id)
    assert deleted_surgeon is None


def test_operating_room_service(db_session):
    print("\n--- Testing OperatingRoomService ---")
    room_data = {"location": "Test Room 101"}
    room_id = OperatingRoomService.create_operating_room(db_session, room_data)
    assert room_id is not None

    room = OperatingRoomService.get_operating_room(db_session, room_id)
    assert room is not None
    print("Fetched Room:", room)

    update_data = {"location": "Updated Test Room 101"}
    updated = OperatingRoomService.update_operating_room(
        db_session, room_id, update_data
    )
    assert updated is True
    updated_room = OperatingRoomService.get_operating_room(db_session, room_id)
    assert updated_room.location == "Updated Test Room 101"

    deleted = OperatingRoomService.delete_operating_room(db_session, room_id)
    assert deleted is True
    deleted_room = OperatingRoomService.get_operating_room(db_session, room_id)
    assert deleted_room is None


def test_surgery_service(db_session):
    print("\n--- Testing SurgeryService ---")
    # Create required patient, surgeon, and room
    patient_data = {
        "name": "SurgeryTest Patient",
        "dob": date(1990, 1, 1),
        "contact_info": "555-9999",
        "privacy_consent": True,
    }
    patient_id = PatientService.create_patient(db_session, patient_data)
    assert patient_id is not None

    surgeon_data = {
        "name": "SurgeryTest Surgeon",
        "contact_info": "surgerysurgeon@example.com",
        "specialization": "General",
        "credentials": "MD",
        "availability": True,
    }
    surgeon_id = SurgeonService.create_surgeon(db_session, surgeon_data)
    assert surgeon_id is not None

    room_data = {"location": "SurgeryTest Room"}
    room_id = OperatingRoomService.create_operating_room(db_session, room_data)
    assert room_id is not None

    surgery_data = {
        "patient_id": patient_id,
        "scheduled_date": datetime(2023, 1, 2, 9, 0, 0),
        "surgery_type": "Test Surgery",
        "urgency_level": "High",
        "duration_minutes": 120,
        "status": "Scheduled",
        "surgeon_id": surgeon_id,
        "room_id": room_id,
        "start_time": None,
        "end_time": None,
    }
    created_id = SurgeryService.create_surgery(db_session, surgery_data)
    assert created_id is not None
    print("Created Surgery ID:", created_id)

    surgery = SurgeryService.get_surgery(db_session, created_id)
    assert surgery is not None
    print("Fetched Surgery:", surgery)

    update_data = {"status": "Completed"}
    updated = SurgeryService.update_surgery(db_session, created_id, update_data)
    assert updated is True
    updated_surgery = SurgeryService.get_surgery(db_session, created_id)
    assert updated_surgery.status == "Completed"

    deleted = SurgeryService.delete_surgery(db_session, created_id)
    assert deleted is True
    deleted_surgery = SurgeryService.get_surgery(db_session, created_id)
    assert deleted_surgery is None

    # Clean up test patient, surgeon, and room
    PatientService.delete_patient(db_session, patient_id)
    SurgeonService.delete_surgeon(db_session, surgeon_id)
    OperatingRoomService.delete_operating_room(db_session, room_id)


def test_surgery_equipment_service(db_session):
    print("\n--- Testing SurgeryEquipmentService ---")
    equipment_data = {
        "name": "Test Equipment",
        "type": "Diagnostic",
        "availability": True,
    }
    equipment_id = SurgeryEquipmentService.create_surgery_equipment(
        db_session, equipment_data
    )
    assert equipment_id is not None

    equipment = SurgeryEquipmentService.get_equipment(db_session, equipment_id)
    assert equipment is not None
    print("Fetched Equipment:", equipment)

    updated = SurgeryEquipmentService.update_surgery_equipment(
        db_session, equipment_id, {"availability": False}
    )
    assert updated is True
    updated_equipment = SurgeryEquipmentService.get_equipment(db_session, equipment_id)
    assert updated_equipment.availability is False

    deleted = SurgeryEquipmentService.delete_surgery_equipment(db_session, equipment_id)
    assert deleted is True
    deleted_equipment = SurgeryEquipmentService.get_equipment(db_session, equipment_id)
    assert deleted_equipment is None


def test_surgery_equipment_usage_service(db_session):
    print("\n--- Testing SurgeryEquipmentUsageService ---")
    # Create required surgery and equipment
    patient_data = {
        "name": "UsageTest Patient",
        "dob": date(1985, 5, 15),
        "contact_info": "555-8888",
        "privacy_consent": True,
    }
    patient_id = PatientService.create_patient(db_session, patient_data)
    surgeon_data = {
        "name": "UsageTest Surgeon",
        "contact_info": "usagesurgeon@example.com",
        "specialization": "Ortho",
        "credentials": "MD",
        "availability": True,
    }
    surgeon_id = SurgeonService.create_surgeon(db_session, surgeon_data)
    room_data = {"location": "UsageTest Room"}
    room_id = OperatingRoomService.create_operating_room(db_session, room_data)
    surgery_data = {
        "patient_id": patient_id,
        "scheduled_date": datetime(2023, 2, 1, 10, 0, 0),
        "surgery_type": "Knee Replacement",
        "urgency_level": "Medium",
        "duration_minutes": 180,
        "status": "Scheduled",
        "surgeon_id": surgeon_id,
        "room_id": room_id,
    }
    surgery_id = SurgeryService.create_surgery(db_session, surgery_data)
    assert surgery_id is not None

    equipment_data = {
        "name": "UsageTest Equipment",
        "type": "Surgical",
        "availability": True,
    }
    equipment_id = SurgeryEquipmentService.create_surgery_equipment(
        db_session, equipment_data
    )
    assert equipment_id is not None

    usage_data = {
        "surgery_id": surgery_id,
        "equipment_id": equipment_id,
        "usage_start_time": datetime(2023, 2, 1, 10, 0, 0),
        "usage_end_time": datetime(2023, 2, 1, 13, 0, 0),
    }
    usage_id = SurgeryEquipmentUsageService.create_surgery_equipment_usage(
        db_session, usage_data
    )
    assert usage_id is not None

    usage = SurgeryEquipmentUsageService.get_usage(db_session, usage_id)
    assert usage is not None
    print("Fetched Usage:", usage)

    update_data = {"usage_end_time": datetime(2023, 2, 1, 13, 30, 0)}
    updated = SurgeryEquipmentUsageService.update_surgery_equipment_usage(
        db_session, usage_id, update_data
    )
    assert updated is True
    updated_usage = SurgeryEquipmentUsageService.get_usage(db_session, usage_id)
    assert updated_usage.usage_end_time == datetime(2023, 2, 1, 13, 30, 0)

    deleted = SurgeryEquipmentUsageService.delete_surgery_equipment_usage(
        db_session, usage_id
    )
    assert deleted is True
    deleted_usage = SurgeryEquipmentUsageService.get_usage(db_session, usage_id)
    assert deleted_usage is None

    # Clean up
    SurgeryService.delete_surgery(db_session, surgery_id)
    SurgeryEquipmentService.delete_surgery_equipment(db_session, equipment_id)
    PatientService.delete_patient(db_session, patient_id)
    SurgeonService.delete_surgeon(db_session, surgeon_id)
    OperatingRoomService.delete_operating_room(db_session, room_id)


def test_surgery_room_assignment_service(db_session):
    print("\n--- Testing SurgeryRoomAssignmentService ---")
    # Create required surgery and room
    patient_data = {
        "name": "RoomAssign Patient",
        "dob": date(1980, 3, 10),
        "contact_info": "555-7777",
        "privacy_consent": True,
    }
    patient_id = PatientService.create_patient(db_session, patient_data)
    surgeon_data = {
        "name": "RoomAssign Surgeon",
        "contact_info": "roomassignsurgeon@example.com",
        "specialization": "Neuro",
        "credentials": "MD",
        "availability": True,
    }
    surgeon_id = SurgeonService.create_surgeon(db_session, surgeon_data)
    room_data_s = {"location": "RoomAssign Surgery Room"}
    room_id_s = OperatingRoomService.create_operating_room(db_session, room_data_s)

    surgery_data = {
        "patient_id": patient_id,
        "scheduled_date": datetime(2023, 3, 1, 11, 0, 0),
        "surgery_type": "Brain Tumor Removal",
        "urgency_level": "High",
        "duration_minutes": 240,
        "status": "Scheduled",
        "surgeon_id": surgeon_id,
        "room_id": room_id_s,  # Initial room, can be updated by assignment
    }
    surgery_id = SurgeryService.create_surgery(db_session, surgery_data)
    assert surgery_id is not None

    room_data_or = {"location": "RoomAssign OR 1"}
    or_id = OperatingRoomService.create_operating_room(db_session, room_data_or)
    assert or_id is not None

    assignment_data = {
        "surgery_id": surgery_id,
        "room_id": or_id,
        "assignment_date": date(2023, 3, 1),  # This was the only date field
        "start_time": datetime(2023, 3, 1, 11, 0, 0),  # Added start_time
        "end_time": datetime(
            2023, 3, 1, 15, 0, 0
        ),  # Added end_time (assuming 240 min duration)
    }
    assignment_id = SurgeryRoomAssignmentService.create_surgery_room_assignment(
        db_session, assignment_data
    )
    assert assignment_id is not None

    assignment = SurgeryRoomAssignmentService.get_assignment(db_session, assignment_id)
    assert assignment is not None
    print("Fetched Assignment:", assignment)
    assert assignment.room_id == or_id  # Verify correct room assigned

    # Test update (e.g., change room)
    new_room_data = {"location": "RoomAssign OR 2"}
    new_or_id = OperatingRoomService.create_operating_room(db_session, new_room_data)
    assert new_or_id is not None
    update_data = {"room_id": new_or_id}
    updated = SurgeryRoomAssignmentService.update_surgery_room_assignment(
        db_session, assignment_id, update_data
    )
    assert updated is True
    updated_assignment = SurgeryRoomAssignmentService.get_assignment(
        db_session, assignment_id
    )
    assert updated_assignment.room_id == new_or_id

    deleted = SurgeryRoomAssignmentService.delete_surgery_room_assignment(
        db_session, assignment_id
    )
    assert deleted is True
    deleted_assignment = SurgeryRoomAssignmentService.get_assignment(
        db_session, assignment_id
    )
    assert deleted_assignment is None

    # Clean up
    SurgeryService.delete_surgery(db_session, surgery_id)
    OperatingRoomService.delete_operating_room(db_session, or_id)
    OperatingRoomService.delete_operating_room(db_session, new_or_id)
    OperatingRoomService.delete_operating_room(db_session, room_id_s)
    PatientService.delete_patient(db_session, patient_id)
    SurgeonService.delete_surgeon(db_session, surgeon_id)


def test_appointment_service(db_session):
    print("\n--- Testing AppointmentService ---")
    # Create required surgery
    patient_data = {
        "name": "Appt Patient",
        "dob": date(1975, 8, 25),
        "contact_info": "555-6666",
        "privacy_consent": True,
    }
    patient_id = PatientService.create_patient(db_session, patient_data)
    surgeon_data = {
        "name": "Appt Surgeon",
        "contact_info": "apptsurgeon@example.com",
        "specialization": "General",
        "credentials": "MD",
        "availability": True,
    }
    surgeon_id = SurgeonService.create_surgeon(db_session, surgeon_data)
    room_data = {"location": "Appt Room"}
    room_id = OperatingRoomService.create_operating_room(db_session, room_data)
    surgery_data = {
        "patient_id": patient_id,
        "scheduled_date": datetime(2023, 4, 1, 12, 0, 0),
        "surgery_type": "Appendectomy",
        "urgency_level": "Medium",
        "duration_minutes": 60,
        "status": "Scheduled",
        "surgeon_id": surgeon_id,
        "room_id": room_id,
    }
    surgery_id = SurgeryService.create_surgery(db_session, surgery_data)
    assert surgery_id is not None

    appointment_data = {
        # "surgery_id": surgery_id, # This was incorrect, appointment needs patient, surgeon, room directly
        "patient_id": patient_id,  # Added patient_id
        "surgeon_id": surgeon_id,  # Added surgeon_id
        "room_id": room_id,  # Added room_id
        "appointment_date": datetime(2023, 4, 1, 12, 0, 0),
        "notes": "Pre-op check complete.",
        "status": "Scheduled",  # Added status as it's in the service model
    }
    appointment_id = AppointmentService.create_surgery_appointment(
        db_session, appointment_data
    )
    assert appointment_id is not None

    appointment = AppointmentService.get_appointment(db_session, appointment_id)
    assert appointment is not None
    print("Fetched Appointment:", appointment)

    update_data = {"notes": "Patient fasting since midnight."}
    updated = AppointmentService.update_appointment(
        db_session, appointment_id, update_data
    )
    assert updated is True
    updated_appointment = AppointmentService.get_appointment(db_session, appointment_id)
    assert updated_appointment.notes == "Patient fasting since midnight."

    deleted = AppointmentService.delete_appointment(db_session, appointment_id)
    assert deleted is True
    deleted_appointment = AppointmentService.get_appointment(db_session, appointment_id)
    assert deleted_appointment is None

    # Clean up
    SurgeryService.delete_surgery(db_session, surgery_id)
    PatientService.delete_patient(db_session, patient_id)
    SurgeonService.delete_surgeon(db_session, surgeon_id)
    OperatingRoomService.delete_operating_room(db_session, room_id)


def test_surgery_staff_assignment_service(db_session):
    print("\n--- Testing SurgeryStaffAssignmentService ---")
    # Create required surgery and staff
    patient_data = {
        "name": "StaffAssign Patient",
        "dob": date(1970, 6, 20),
        "contact_info": "555-5555",
        "privacy_consent": True,
    }
    patient_id = PatientService.create_patient(db_session, patient_data)
    surgeon_data = {
        "name": "StaffAssign Surgeon",
        "contact_info": "staffassignsurgeon@example.com",
        "specialization": "Cardio",
        "credentials": "MD",
        "availability": True,
    }
    surgeon_id = SurgeonService.create_surgeon(db_session, surgeon_data)
    room_data = {"location": "StaffAssign Room"}
    room_id = OperatingRoomService.create_operating_room(db_session, room_data)
    surgery_data = {
        "patient_id": patient_id,
        "scheduled_date": datetime(2023, 5, 1, 13, 0, 0),
        "surgery_type": "Heart Bypass",
        "urgency_level": "High",
        "duration_minutes": 300,
        "status": "Scheduled",
        "surgeon_id": surgeon_id,
        "room_id": room_id,
    }
    surgery_id = SurgeryService.create_surgery(db_session, surgery_data)
    assert surgery_id is not None

    staff_data = {
        "name": "StaffAssign Nurse",
        "role": "Surgical Nurse",
        "contact_info": "555-4444",
        "specialization": "OR",
        "availability": True,
    }
    staff_id = StaffService.create_staff(db_session, staff_data)
    assert staff_id is not None

    assignment_data = {
        "surgery_id": surgery_id,
        "staff_id": staff_id,
        "role": "Lead Nurse",
    }
    assignment_id = SurgeryStaffAssignmentService.create_surgery_staff_assignment(
        db_session, assignment_data
    )
    assert assignment_id is not None

    assignment = SurgeryStaffAssignmentService.get_surgery_staff_assignment(
        db_session, assignment_id
    )
    assert assignment is not None
    print("Fetched Staff Assignment:", assignment)
    assert assignment.staff_id == staff_id

    update_data = {"role": "Circulating Nurse"}
    updated = SurgeryStaffAssignmentService.update_surgery_staff_assignment(
        db_session, assignment_id, update_data
    )
    assert updated is True
    updated_assignment = SurgeryStaffAssignmentService.get_surgery_staff_assignment(
        db_session, assignment_id
    )
    assert updated_assignment.role == "Circulating Nurse"

    deleted = SurgeryStaffAssignmentService.delete_surgery_staff_assignment(
        db_session, assignment_id
    )
    assert deleted is True
    deleted_assignment = SurgeryStaffAssignmentService.get_surgery_staff_assignment(
        db_session, assignment_id
    )
    assert deleted_assignment is None

    # Clean up
    SurgeryService.delete_surgery(db_session, surgery_id)
    StaffService.delete_staff(db_session, staff_id)
    PatientService.delete_patient(db_session, patient_id)
    SurgeonService.delete_surgeon(db_session, surgeon_id)
    OperatingRoomService.delete_operating_room(db_session, room_id)


# To run tests, execute: pytest test_services.py
# Ensure your environment is set up with necessary packages (pytest, sqlalchemy, etc.)
