"""
Tests for the API models.

This module provides tests for the API models used for request and response validation.
"""

import os
import sys
import pytest
from datetime import datetime, date
from pydantic import ValidationError

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.models import (
    SurgeryStatus,
    AppointmentStatus,
    UrgencyLevel,
    PatientBase,
    SurgeonBase,
    StaffBase,
    OperatingRoomBase,
    SurgeryBase,
    SurgeryTypeBase,
    AppointmentBase,
    UserBase,
    PatientCreate,
    SurgeonCreate,
    StaffCreate,
    OperatingRoomCreate,
    SurgeryCreate,
    SurgeryTypeCreate,
    AppointmentCreate,
    UserCreate,
    Patient,
    Surgeon,
    Staff,
    OperatingRoom,
    SurgeryType,
    Surgery,
    Appointment,
    User,
    Token,
    TokenData,
    PatientUpdate,
    SurgeonUpdate,
    StaffUpdate,
    OperatingRoomUpdate,
    SurgeryUpdate
)


def test_enum_values():
    """Test enum values."""
    # Test SurgeryStatus enum
    assert SurgeryStatus.SCHEDULED == "Scheduled"
    assert SurgeryStatus.IN_PROGRESS == "In Progress"
    assert SurgeryStatus.COMPLETED == "Completed"
    assert SurgeryStatus.CANCELLED == "Cancelled"

    # Test AppointmentStatus enum
    assert AppointmentStatus.SCHEDULED == "Scheduled"
    assert AppointmentStatus.COMPLETED == "Completed"
    assert AppointmentStatus.CANCELLED == "Cancelled"

    # Test UrgencyLevel enum
    assert UrgencyLevel.LOW == "Low"
    assert UrgencyLevel.MEDIUM == "Medium"
    assert UrgencyLevel.HIGH == "High"
    assert UrgencyLevel.EMERGENCY == "Emergency"


def test_base_models():
    """Test base models."""
    # Test PatientBase model
    patient = PatientBase(name="Test Patient", dob=date(1980, 1, 1), privacy_consent=True)
    assert patient.name == "Test Patient"
    assert patient.dob == date(1980, 1, 1)
    assert patient.privacy_consent is True
    assert patient.contact_info is None

    # Test SurgeonBase model
    surgeon = SurgeonBase(
        name="Dr. Test",
        specialization="Cardiology",
        credentials="MD"
    )
    assert surgeon.name == "Dr. Test"
    assert surgeon.specialization == "Cardiology"
    assert surgeon.credentials == "MD"
    assert surgeon.contact_info is None
    assert surgeon.availability is True

    # Test StaffBase model
    staff = StaffBase(name="Test Staff", role="Nurse")
    assert staff.name == "Test Staff"
    assert staff.role == "Nurse"
    assert staff.contact_info is None
    assert staff.specialization is None
    assert staff.availability is True

    # Test OperatingRoomBase model
    room = OperatingRoomBase(location="Test Room")
    assert room.location == "Test Room"

    # Test SurgeryBase model
    surgery = SurgeryBase(
        surgery_type_id=1,
        duration_minutes=60,
        urgency_level=UrgencyLevel.MEDIUM
    )
    assert surgery.surgery_type_id == 1
    assert surgery.duration_minutes == 60
    assert surgery.urgency_level == UrgencyLevel.MEDIUM
    assert surgery.patient_id is None
    assert surgery.surgeon_id is None
    assert surgery.room_id is None
    assert surgery.start_time is None
    assert surgery.end_time is None
    assert surgery.status == SurgeryStatus.SCHEDULED

    # Test SurgeryTypeBase model
    surgery_type = SurgeryTypeBase(name="Test Surgery Type", average_duration=60)
    assert surgery_type.name == "Test Surgery Type"
    assert surgery_type.average_duration == 60
    assert surgery_type.description is None

    # Test AppointmentBase model
    appointment = AppointmentBase(
        patient_id=1,
        surgeon_id=1,
        appointment_date=datetime.now()
    )
    assert appointment.patient_id == 1
    assert appointment.surgeon_id == 1
    assert appointment.room_id is None
    assert appointment.status == AppointmentStatus.SCHEDULED
    assert appointment.notes is None

    # Test UserBase model
    user = UserBase(username="testuser", email="test@example.com", role="admin")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == "admin"
    assert user.full_name is None
    assert user.staff_id is None


def test_create_models():
    """Test create models."""
    # Test PatientCreate model
    patient = PatientCreate(name="Test Patient", dob=date(1980, 1, 1), privacy_consent=True)
    assert patient.name == "Test Patient"
    assert patient.dob == date(1980, 1, 1)
    assert patient.privacy_consent is True

    # Test SurgeonCreate model
    surgeon = SurgeonCreate(
        name="Dr. Test",
        specialization="Cardiology",
        credentials="MD"
    )
    assert surgeon.name == "Dr. Test"
    assert surgeon.specialization == "Cardiology"
    assert surgeon.credentials == "MD"

    # Test StaffCreate model
    staff = StaffCreate(name="Test Staff", role="Nurse")
    assert staff.name == "Test Staff"
    assert staff.role == "Nurse"

    # Test OperatingRoomCreate model
    room = OperatingRoomCreate(location="Test Room")
    assert room.location == "Test Room"

    # Test SurgeryCreate model
    surgery = SurgeryCreate(
        surgery_type_id=1,
        duration_minutes=60,
        urgency_level=UrgencyLevel.MEDIUM
    )
    assert surgery.surgery_type_id == 1
    assert surgery.duration_minutes == 60
    assert surgery.urgency_level == UrgencyLevel.MEDIUM

    # Test SurgeryTypeCreate model
    surgery_type = SurgeryTypeCreate(name="Test Surgery Type", average_duration=60)
    assert surgery_type.name == "Test Surgery Type"
    assert surgery_type.average_duration == 60

    # Test AppointmentCreate model
    appointment = AppointmentCreate(
        patient_id=1,
        surgeon_id=1,
        appointment_date=datetime.now()
    )
    assert appointment.patient_id == 1
    assert appointment.surgeon_id == 1

    # Test UserCreate model
    user = UserCreate(username="testuser", email="test@example.com", password="password", role="admin")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "password"
    assert user.role == "admin"


def test_response_models():
    """Test response models."""
    # Test Patient model
    patient = Patient(
        patient_id=1,
        name="Test Patient",
        dob=date(1980, 1, 1),
        privacy_consent=True
    )
    assert patient.patient_id == 1
    assert patient.name == "Test Patient"
    assert patient.dob == date(1980, 1, 1)
    assert patient.privacy_consent is True

    # Test Surgeon model
    surgeon = Surgeon(
        surgeon_id=1,
        name="Dr. Test",
        specialization="Cardiology",
        credentials="MD"
    )
    assert surgeon.surgeon_id == 1
    assert surgeon.name == "Dr. Test"
    assert surgeon.specialization == "Cardiology"
    assert surgeon.credentials == "MD"

    # Test Staff model
    staff = Staff(
        staff_id=1,
        name="Test Staff",
        role="Nurse"
    )
    assert staff.staff_id == 1
    assert staff.name == "Test Staff"
    assert staff.role == "Nurse"

    # Test OperatingRoom model
    room = OperatingRoom(
        room_id=1,
        location="Test Room"
    )
    assert room.room_id == 1
    assert room.location == "Test Room"

    # Test SurgeryType model
    surgery_type = SurgeryType(
        type_id=1,
        name="Test Surgery Type",
        average_duration=60
    )
    assert surgery_type.type_id == 1
    assert surgery_type.name == "Test Surgery Type"
    assert surgery_type.average_duration == 60

    # Test Surgery model
    surgery = Surgery(
        surgery_id=1,
        surgery_type_id=1,
        duration_minutes=60,
        urgency_level=UrgencyLevel.MEDIUM
    )
    assert surgery.surgery_id == 1
    assert surgery.surgery_type_id == 1
    assert surgery.duration_minutes == 60
    assert surgery.urgency_level == UrgencyLevel.MEDIUM

    # Test Appointment model
    appointment = Appointment(
        appointment_id=1,
        patient_id=1,
        surgeon_id=1,
        appointment_date=datetime.now()
    )
    assert appointment.appointment_id == 1
    assert appointment.patient_id == 1
    assert appointment.surgeon_id == 1

    # Test User model
    user = User(
        user_id=1,
        username="testuser",
        email="test@example.com",
        role="admin",
        is_active=True,
        created_at=datetime.now()
    )
    assert user.user_id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == "admin"
    assert user.is_active is True


def test_token_models():
    """Test token models."""
    # Test Token model
    token = Token(access_token="test-token", token_type="bearer")
    assert token.access_token == "test-token"
    assert token.token_type == "bearer"

    # Test TokenData model
    token_data = TokenData(username="testuser", role="admin")
    assert token_data.username == "testuser"
    assert token_data.role == "admin"

    # Test TokenData model with defaults
    token_data = TokenData()
    assert token_data.username is None
    assert token_data.role is None


def test_update_models():
    """Test update models."""
    # Test PatientUpdate model
    patient = PatientUpdate(name="Updated Patient", contact_info="updated@example.com")
    assert patient.name == "Updated Patient"
    assert patient.contact_info == "updated@example.com"
    assert patient.privacy_consent is None

    # Test SurgeonUpdate model
    surgeon = SurgeonUpdate(
        name="Dr. Updated",
        specialization="Updated Specialization"
    )
    assert surgeon.name == "Dr. Updated"
    assert surgeon.specialization == "Updated Specialization"
    assert surgeon.credentials is None
    assert surgeon.contact_info is None
    assert surgeon.availability is None

    # Test StaffUpdate model
    staff = StaffUpdate(name="Updated Staff", role="Updated Role")
    assert staff.name == "Updated Staff"
    assert staff.role == "Updated Role"
    assert staff.contact_info is None
    assert staff.specialization is None
    assert staff.availability is None

    # Test OperatingRoomUpdate model
    room = OperatingRoomUpdate(location="Updated Room")
    assert room.location == "Updated Room"

    # Test SurgeryUpdate model
    surgery = SurgeryUpdate(
        surgery_type_id=2,
        duration_minutes=120,
        urgency_level=UrgencyLevel.HIGH
    )
    assert surgery.surgery_type_id == 2
    assert surgery.duration_minutes == 120
    assert surgery.urgency_level == UrgencyLevel.HIGH
    assert surgery.patient_id is None
    assert surgery.surgeon_id is None
    assert surgery.room_id is None
    assert surgery.start_time is None
    assert surgery.end_time is None
    assert surgery.status is None


# Run the tests
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
