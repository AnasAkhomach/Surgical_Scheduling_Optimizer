"""
Tests for the scheduling service.
"""

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from services.scheduling_service import SchedulingService
from services.exceptions import ValidationError, ResourceNotFoundError





def test_schedule_surgery():
    """Test scheduling a surgery."""
    # Create a mock scheduling service
    service = SchedulingService(testing=True)

    # Mock the schedule_surgery method to return a surgery ID
    service.schedule_surgery = MagicMock(return_value=1)

    # Create surgery data
    surgery_data = {
        "scheduled_date": datetime.now() + timedelta(days=1),
        "surgery_type_id": 1,
        "urgency_level": "Medium",
        "duration_minutes": 60,
        "patient_id": 1,
        "surgeon_id": 1
    }

    # Schedule the surgery
    start_time = datetime.now() + timedelta(days=1, hours=9)
    surgery_id = service.schedule_surgery(
        surgery_data=surgery_data,
        room_id=1,
        start_time=start_time,
        notify_surgeon=True,
        update_calendar=True
    )

    # Check that the surgery was created
    assert surgery_id is not None

    # Check that the service method was called with the correct arguments
    service.schedule_surgery.assert_called_once_with(
        surgery_data=surgery_data,
        room_id=1,
        start_time=start_time,
        notify_surgeon=True,
        update_calendar=True
    )


def test_schedule_surgery_validation_error():
    """Test scheduling a surgery with invalid data."""
    # Create a mock scheduling service
    service = SchedulingService(testing=True)

    # Mock the schedule_surgery method to raise ValidationError
    service.schedule_surgery = MagicMock(side_effect=ValidationError("Validation failed"))

    # Create invalid surgery data (missing required fields)
    surgery_data = {
        "scheduled_date": datetime.now() + timedelta(days=1),
        # Missing surgery_type_id
        "urgency_level": "Medium",
        "duration_minutes": 60,
        "patient_id": 1,
        "surgeon_id": 1
    }

    # Schedule the surgery (should raise ValidationError)
    with pytest.raises(ValidationError):
        service.schedule_surgery(
            surgery_data=surgery_data,
            room_id=1,
            start_time=datetime.now() + timedelta(days=1, hours=9)
        )


def test_reschedule_surgery():
    """Test rescheduling a surgery."""
    # Create a mock scheduling service
    service = SchedulingService(testing=True)

    # Mock the reschedule_surgery method to return True
    service.reschedule_surgery = MagicMock(return_value=True)

    # Reschedule the surgery
    new_start_time = datetime.now() + timedelta(days=1, hours=13)
    success = service.reschedule_surgery(
        surgery_id=1,
        start_time=new_start_time,
        notify_surgeon=True,
        update_calendar=True
    )

    # Check that the surgery was rescheduled
    assert success is True

    # Check that the service method was called with the correct arguments
    service.reschedule_surgery.assert_called_once_with(
        surgery_id=1,
        start_time=new_start_time,
        notify_surgeon=True,
        update_calendar=True
    )


def test_reschedule_surgery_not_found():
    """Test rescheduling a surgery that doesn't exist."""
    # Create a mock scheduling service
    service = SchedulingService(testing=True)

    # Mock the reschedule_surgery method to raise ResourceNotFoundError
    service.reschedule_surgery = MagicMock(side_effect=ResourceNotFoundError("Surgery", 999))

    # Reschedule a non-existent surgery (should raise ResourceNotFoundError)
    with pytest.raises(ResourceNotFoundError):
        service.reschedule_surgery(
            surgery_id=999,
            start_time=datetime.now() + timedelta(days=1, hours=13)
        )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
