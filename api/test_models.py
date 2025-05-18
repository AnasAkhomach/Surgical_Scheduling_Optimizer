"""
Tests for the Pydantic models.

This module provides tests for the Pydantic models used for request and response validation.
"""

import os
import sys
import pytest
from datetime import datetime, date
from pydantic import ValidationError

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.models import (
    PatientCreate,
    SurgeonCreate,
    StaffCreate,
    OperatingRoomCreate,
    SurgeryCreate,
    SurgeryTypeCreate,
    AppointmentCreate,
    UserCreate,
    SurgeryStatus,
    AppointmentStatus,
    UrgencyLevel
)


def test_patient_create_model():
    """Test PatientCreate model validation."""
    # Valid data
    valid_data = {
        "name": "Test Patient",
        "dob": date(1980, 1, 1),
        "contact_info": "test@example.com",
        "privacy_consent": True
    }
    patient = PatientCreate(**valid_data)
    assert patient.name == "Test Patient"
    assert patient.dob == date(1980, 1, 1)
    assert patient.contact_info == "test@example.com"
    assert patient.privacy_consent is True
    
    # Missing required field
    invalid_data = {
        "dob": date(1980, 1, 1),
        "contact_info": "test@example.com"
    }
    with pytest.raises(ValidationError):
        PatientCreate(**invalid_data)
    
    # Invalid date format
    invalid_data = {
        "name": "Test Patient",
        "dob": "not-a-date",
        "contact_info": "test@example.com"
    }
    with pytest.raises(ValidationError):
        PatientCreate(**invalid_data)


def test_surgeon_create_model():
    """Test SurgeonCreate model validation."""
    # Valid data
    valid_data = {
        "name": "Dr. Test",
        "contact_info": "test@example.com",
        "specialization": "Cardiology",
        "credentials": "MD",
        "availability": True
    }
    surgeon = SurgeonCreate(**valid_data)
    assert surgeon.name == "Dr. Test"
    assert surgeon.contact_info == "test@example.com"
    assert surgeon.specialization == "Cardiology"
    assert surgeon.credentials == "MD"
    assert surgeon.availability is True
    
    # Missing required fields
    invalid_data = {
        "name": "Dr. Test",
        "contact_info": "test@example.com"
    }
    with pytest.raises(ValidationError):
        SurgeonCreate(**invalid_data)


def test_staff_create_model():
    """Test StaffCreate model validation."""
    # Valid data
    valid_data = {
        "name": "Test Staff",
        "role": "Nurse",
        "contact_info": "test@example.com",
        "specialization": "Pediatrics",
        "availability": True
    }
    staff = StaffCreate(**valid_data)
    assert staff.name == "Test Staff"
    assert staff.role == "Nurse"
    assert staff.contact_info == "test@example.com"
    assert staff.specialization == "Pediatrics"
    assert staff.availability is True
    
    # Missing required fields
    invalid_data = {
        "name": "Test Staff",
        "contact_info": "test@example.com"
    }
    with pytest.raises(ValidationError):
        StaffCreate(**invalid_data)


def test_operating_room_create_model():
    """Test OperatingRoomCreate model validation."""
    # Valid data
    valid_data = {
        "location": "Test Room"
    }
    room = OperatingRoomCreate(**valid_data)
    assert room.location == "Test Room"
    
    # Missing required fields
    invalid_data = {}
    with pytest.raises(ValidationError):
        OperatingRoomCreate(**invalid_data)


def test_surgery_create_model():
    """Test SurgeryCreate model validation."""
    # Valid data
    valid_data = {
        "surgery_type_id": 1,
        "duration_minutes": 60,
        "urgency_level": UrgencyLevel.MEDIUM,
        "patient_id": 1,
        "surgeon_id": 1,
        "room_id": 1,
        "start_time": datetime.now(),
        "end_time": datetime.now(),
        "status": SurgeryStatus.SCHEDULED
    }
    surgery = SurgeryCreate(**valid_data)
    assert surgery.surgery_type_id == 1
    assert surgery.duration_minutes == 60
    assert surgery.urgency_level == UrgencyLevel.MEDIUM
    assert surgery.patient_id == 1
    assert surgery.surgeon_id == 1
    assert surgery.room_id == 1
    assert surgery.status == SurgeryStatus.SCHEDULED
    
    # Missing required fields
    invalid_data = {
        "patient_id": 1,
        "surgeon_id": 1
    }
    with pytest.raises(ValidationError):
        SurgeryCreate(**invalid_data)
    
    # Invalid enum value
    invalid_data = {
        "surgery_type_id": 1,
        "duration_minutes": 60,
        "urgency_level": "Invalid",
        "patient_id": 1,
        "surgeon_id": 1
    }
    with pytest.raises(ValidationError):
        SurgeryCreate(**invalid_data)


def test_appointment_create_model():
    """Test AppointmentCreate model validation."""
    # Valid data
    valid_data = {
        "patient_id": 1,
        "surgeon_id": 1,
        "room_id": 1,
        "appointment_date": datetime.now(),
        "status": AppointmentStatus.SCHEDULED,
        "notes": "Test notes"
    }
    appointment = AppointmentCreate(**valid_data)
    assert appointment.patient_id == 1
    assert appointment.surgeon_id == 1
    assert appointment.room_id == 1
    assert appointment.status == AppointmentStatus.SCHEDULED
    assert appointment.notes == "Test notes"
    
    # Missing required fields
    invalid_data = {
        "patient_id": 1
    }
    with pytest.raises(ValidationError):
        AppointmentCreate(**invalid_data)


def test_user_create_model():
    """Test UserCreate model validation."""
    # Valid data
    valid_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password",
        "full_name": "Test User",
        "role": "admin",
        "staff_id": 1
    }
    user = UserCreate(**valid_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "password"
    assert user.full_name == "Test User"
    assert user.role == "admin"
    assert user.staff_id == 1
    
    # Missing required fields
    invalid_data = {
        "username": "testuser",
        "full_name": "Test User"
    }
    with pytest.raises(ValidationError):
        UserCreate(**invalid_data)
    
    # Invalid email format
    invalid_data = {
        "username": "testuser",
        "email": "not-an-email",
        "password": "password"
    }
    with pytest.raises(ValidationError):
        UserCreate(**invalid_data)


# Run the tests
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
