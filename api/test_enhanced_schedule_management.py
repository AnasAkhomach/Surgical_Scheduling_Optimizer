"""
Tests for enhanced schedule management API endpoints.

This module provides comprehensive tests for the enhanced schedule management functionality.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_config import get_db, Base
from api.main import app
from api.auth import get_current_active_user
from models import (
    User, Surgery, OperatingRoom, Surgeon, Patient, SurgeryType,
    SurgeryRoomAssignment, ScheduleHistory
)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_active_user():
    return User(
        user_id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        role="admin",
        is_active=True,
        hashed_password="fake_hash",
        created_at=datetime.now()
    )

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_active_user] = override_get_current_active_user

client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create test data
    # Surgery types
    surgery_type1 = SurgeryType(type_id=1, name="Appendectomy", description="Appendix removal", average_duration=90)
    surgery_type2 = SurgeryType(type_id=2, name="Gallbladder", description="Gallbladder surgery", average_duration=120)

    # Operating rooms
    room1 = OperatingRoom(room_id=1, name="OR-1", location="Building A, Room 101", status="Active") # Added name and status
    room2 = OperatingRoom(room_id=2, name="OR-2", location="Building B, Room 202", status="Active") # Added name and status

    # Surgeons
    surgeon1 = Surgeon(surgeon_id=1, name="Dr. Smith", contact_info="smith@hospital.com",
                      specialization="General Surgery", credentials="MD, FACS")
    surgeon2 = Surgeon(surgeon_id=2, name="Dr. Jones", contact_info="jones@hospital.com",
                      specialization="General Surgery", credentials="MD, FACS")

    # Patients
    patient1 = Patient(patient_id=1, name="John Doe", dob=date(1980, 1, 1),
                      contact_info="john@email.com", privacy_consent=True)
    patient2 = Patient(patient_id=2, name="Jane Smith", dob=date(1990, 1, 1),
                      contact_info="jane@email.com", privacy_consent=True)

    # Add all test data
    db.add_all([surgery_type1, surgery_type2, room1, room2, surgeon1, surgeon2, patient1, patient2])
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


def test_schedule_conflict_detection(db):
    """Test schedule conflict detection."""
    test_date = date.today()

    # Create overlapping surgeries
    surgery1 = Surgery(
        surgery_id=1,
        surgery_type_id=1,
        duration_minutes=90,
        urgency_level="Elective",
        patient_id=1,
        surgeon_id=1,
        room_id=1,
        scheduled_date=test_date,
        start_time=datetime.combine(test_date, datetime.min.time().replace(hour=9)),
        end_time=datetime.combine(test_date, datetime.min.time().replace(hour=10, minute=30)),
        status="Scheduled"
    )

    surgery2 = Surgery(
        surgery_id=2,
        surgery_type_id=2,
        duration_minutes=120,
        urgency_level="Elective",
        patient_id=2,
        surgeon_id=1,  # Same surgeon - conflict
        room_id=2,
        scheduled_date=test_date,
        start_time=datetime.combine(test_date, datetime.min.time().replace(hour=10)),
        end_time=datetime.combine(test_date, datetime.min.time().replace(hour=12)),
        status="Scheduled"
    )

    db.add_all([surgery1, surgery2])
    db.commit()

    # Test conflict detection
    response = client.get(f"/api/schedules/conflicts?schedule_date={test_date}")
    assert response.status_code == 200

    data = response.json()
    assert data["is_valid"] == False
    assert data["total_conflicts"] > 0
    assert data["critical_conflicts"] > 0
    assert len(data["conflicts"]) > 0

    # Check conflict details
    conflict = data["conflicts"][0]
    assert conflict["conflict_type"] == "surgeon_overlap"
    assert conflict["severity"] == "critical"


def test_manual_schedule_adjustment(db):
    """Test manual schedule adjustment."""
    test_date = date.today()

    # Create a surgery
    surgery = Surgery(
        surgery_id=1,
        surgery_type_id=1,
        duration_minutes=90,
        urgency_level="Elective",
        patient_id=1,
        surgeon_id=1,
        room_id=1,
        scheduled_date=test_date,
        start_time=datetime.combine(test_date, datetime.min.time().replace(hour=9)),
        end_time=datetime.combine(test_date, datetime.min.time().replace(hour=10, minute=30)),
        status="Scheduled"
    )

    db.add(surgery)
    db.commit()

    # Test manual adjustment
    adjustment_data = {
        "surgery_id": 1,
        "new_room_id": 2,
        "new_surgeon_id": 2,
        "new_start_time": datetime.combine(test_date, datetime.min.time().replace(hour=14)).isoformat(),
        "reason": "Patient request for afternoon slot",
        "force_override": False
    }

    response = client.post("/api/schedules/adjust", json=adjustment_data)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] == True
    assert "Room changed" in str(data["changes_applied"])
    assert "Surgeon changed" in str(data["changes_applied"])


def test_schedule_comparison(db):
    """Test schedule comparison functionality."""
    test_date = date.today()

    # Create current schedule
    current_schedule = [
        {
            "surgery_id": 1,
            "room_id": 1,
            "room": "OR-1",
            "surgeon_id": 1,
            "surgeon": "Dr. Smith",
            "surgery_type_id": 1,
            "surgery_type": "Appendectomy",
            "start_time": datetime.combine(test_date, datetime.min.time().replace(hour=9)).isoformat(),
            "end_time": datetime.combine(test_date, datetime.min.time().replace(hour=10, minute=30)).isoformat(),
            "duration_minutes": 90,
            "patient_id": 1,
            "patient_name": "John Doe",
            "urgency_level": "Elective",
            "status": "Scheduled"
        }
    ]

    # Create proposed schedule with changes
    proposed_schedule = [
        {
            "surgery_id": 1,
            "room_id": 2,  # Changed room
            "room": "OR-2",
            "surgeon_id": 2,  # Changed surgeon
            "surgeon": "Dr. Jones",
            "surgery_type_id": 1,
            "surgery_type": "Appendectomy",
            "start_time": datetime.combine(test_date, datetime.min.time().replace(hour=14)).isoformat(),  # Changed time
            "end_time": datetime.combine(test_date, datetime.min.time().replace(hour=15, minute=30)).isoformat(),
            "duration_minutes": 90,
            "patient_id": 1,
            "patient_name": "John Doe",
            "urgency_level": "Elective",
            "status": "Scheduled"
        }
    ]

    comparison_data = {
        "current_schedule": current_schedule,
        "proposed_schedule": proposed_schedule
    }

    response = client.post("/api/schedules/compare", json=comparison_data)
    assert response.status_code == 200

    data = response.json()
    assert len(data["changes"]) > 0
    assert data["changes"][0]["change_type"] == "modified"
    assert "room changed" in data["changes"][0]["description"]
    assert "surgeon changed" in data["changes"][0]["description"]
    assert "metrics_comparison" in data
    assert "improvement_summary" in data


def test_schedule_history(db):
    """Test schedule history tracking."""
    test_date = date.today()

    # Create a schedule history entry
    history_entry = ScheduleHistory(
        schedule_date=test_date,
        created_by_user_id=1,
        action_type="manual_adjustment",
        changes_summary="Test adjustment for room change",
        affected_surgeries='[1, 2]',
        schedule_snapshot='[]'
    )

    db.add(history_entry)
    db.commit()

    # Test getting history
    response = client.get(f"/api/schedules/history?schedule_date={test_date}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0
    assert data[0]["action_type"] == "manual_adjustment"
    assert data[0]["changes_summary"] == "Test adjustment for room change"
    assert data[0]["created_by_username"] == "testuser"


def test_schedule_validation_with_no_conflicts(db):
    """Test schedule validation when there are no conflicts."""
    test_date = date.today()

    # Create non-overlapping surgeries
    surgery1 = Surgery(
        surgery_id=1,
        surgery_type_id=1,
        duration_minutes=90,
        urgency_level="Elective",
        patient_id=1,
        surgeon_id=1,
        room_id=1,
        scheduled_date=test_date,
        start_time=datetime.combine(test_date, datetime.min.time().replace(hour=9)),
        end_time=datetime.combine(test_date, datetime.min.time().replace(hour=10, minute=30)),
        status="Scheduled"
    )

    surgery2 = Surgery(
        surgery_id=2,
        surgery_type_id=2,
        duration_minutes=120,
        urgency_level="Elective",
        patient_id=2,
        surgeon_id=2,  # Different surgeon
        room_id=2,     # Different room
        scheduled_date=test_date,
        start_time=datetime.combine(test_date, datetime.min.time().replace(hour=14)),
        end_time=datetime.combine(test_date, datetime.min.time().replace(hour=16)),
        status="Scheduled"
    )

    db.add_all([surgery1, surgery2])
    db.commit()

    # Test conflict detection
    response = client.get(f"/api/schedules/conflicts?schedule_date={test_date}")
    assert response.status_code == 200

    data = response.json()
    assert data["is_valid"] == True
    assert data["total_conflicts"] == 0
    assert data["critical_conflicts"] == 0
