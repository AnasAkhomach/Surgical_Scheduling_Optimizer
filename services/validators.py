"""
Entity-specific validators for the surgery scheduling application.

This module provides validators for specific entities in the application.
"""

import os
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Union

from sqlalchemy.orm import Session

from models import (
    Surgery,
    OperatingRoom,
    Surgeon,
    Staff,
    Patient,
    SurgeryEquipment,
    SurgeryType,
    SurgeonPreference,
    SurgeryRoomAssignment
)
from services.validation import Validator
from services.exceptions import ValidationError

logger = logging.getLogger(__name__)


class PatientValidator(Validator):
    """Validator for patient data."""

    def _validate(self, data: Dict[str, Any]) -> None:
        """
        Validate patient data.

        Args:
            data: The patient data to validate.
        """
        # Required fields
        self.validate_required(data, ['name', 'dob', 'contact_info', 'privacy_consent'])

        # Name validation
        self.validate_string(data, 'name', min_length=2, max_length=255)

        # Date of birth validation
        self.validate_date(data, 'dob', max_date=datetime.now().date())

        # Contact info validation
        self.validate_string(data, 'contact_info', max_length=255, required=False)

        # Privacy consent validation
        self.validate_boolean(data, 'privacy_consent')


class SurgeonValidator(Validator):
    """Validator for surgeon data."""

    def _validate(self, data: Dict[str, Any]) -> None:
        """
        Validate surgeon data.

        Args:
            data: The surgeon data to validate.
        """
        # Required fields
        self.validate_required(data, ['name', 'specialization', 'credentials'])

        # Name validation
        self.validate_string(data, 'name', min_length=2, max_length=255)

        # Contact info validation
        self.validate_string(data, 'contact_info', max_length=255, required=False)

        # Specialization validation
        self.validate_string(data, 'specialization', min_length=2, max_length=255)

        # Credentials validation
        self.validate_string(data, 'credentials')

        # Availability validation
        self.validate_boolean(data, 'availability', required=False)


class StaffValidator(Validator):
    """Validator for staff data."""

    def _validate(self, data: Dict[str, Any]) -> None:
        """
        Validate staff data.

        Args:
            data: The staff data to validate.
        """
        # Required fields
        self.validate_required(data, ['name', 'role'])

        # Name validation
        self.validate_string(data, 'name', min_length=2, max_length=255)

        # Role validation
        self.validate_string(data, 'role', min_length=2, max_length=100)

        # Contact info validation
        self.validate_string(data, 'contact_info', max_length=255, required=False)

        # Specialization validation
        self.validate_string(data, 'specialization', max_length=255, required=False)

        # Availability validation
        self.validate_boolean(data, 'availability', required=False)


class OperatingRoomValidator(Validator):
    """Validator for operating room data."""

    def _validate(self, data: Dict[str, Any]) -> None:
        """
        Validate operating room data.

        Args:
            data: The operating room data to validate.
        """
        # Required fields
        self.validate_required(data, ['location'])

        # Location validation
        self.validate_string(data, 'location', min_length=2, max_length=255)


class SurgeryTypeValidator(Validator):
    """Validator for surgery type data."""

    def _validate(self, data: Dict[str, Any]) -> None:
        """
        Validate surgery type data.

        Args:
            data: The surgery type data to validate.
        """
        # Required fields
        self.validate_required(data, ['name'])

        # Name validation
        self.validate_string(data, 'name', min_length=2, max_length=100)

        # Description validation
        self.validate_string(data, 'description', required=False)

        # Check for duplicate name if we have a database session
        if self.db and 'name' in data:
            existing = self.db.query(SurgeryType).filter(SurgeryType.name == data['name']).first()
            if existing and ('type_id' not in data or existing.type_id != data['type_id']):
                self.add_error('name', f"Surgery type with name '{data['name']}' already exists")


class SurgeryValidator(Validator):
    """Validator for surgery data."""

    def _validate(self, data: Dict[str, Any]) -> None:
        """
        Validate surgery data.

        Args:
            data: The surgery data to validate.
        """
        # Required fields
        self.validate_required(data, [
            'scheduled_date',
            'surgery_type_id',
            'urgency_level',
            'duration_minutes'
        ])

        # Scheduled date validation
        self.validate_date(data, 'scheduled_date', min_date=datetime.now())

        # Surgery type validation
        self.validate_foreign_key(data, 'surgery_type_id', SurgeryType, 'type_id')

        # Urgency level validation
        self.validate_enum(
            data,
            'urgency_level',
            ['Low', 'Medium', 'High']
        )

        # Duration validation
        self.validate_integer(data, 'duration_minutes', min_value=1)

        # Status validation
        self.validate_enum(
            data,
            'status',
            ['Scheduled', 'In Progress', 'Completed', 'Cancelled'],
            required=False
        )

        # Start time validation
        self.validate_date(data, 'start_time', required=False)

        # End time validation
        self.validate_date(data, 'end_time', required=False)

        # Patient validation
        self.validate_foreign_key(data, 'patient_id', Patient, required=False)

        # Surgeon validation
        self.validate_foreign_key(data, 'surgeon_id', Surgeon, required=False)

        # Room validation
        self.validate_foreign_key(data, 'room_id', OperatingRoom, required=False)

        # Validate start and end times if both are provided
        if 'start_time' in data and data['start_time'] and 'end_time' in data and data['end_time']:
            if data['start_time'] >= data['end_time']:
                self.add_error('end_time', "End time must be after start time")


class SurgeryRoomAssignmentValidator(Validator):
    """Validator for surgery room assignment data."""

    def __init__(self, db=None, testing=False):
        """
        Initialize the validator.

        Args:
            db: SQLAlchemy database session.
            testing: Whether the validator is being used in a test environment.
        """
        super().__init__(db)
        self.testing = testing or os.getenv('TESTING', 'False').lower() in ('true', '1', 't')

    def _validate(self, data: Dict[str, Any]) -> None:
        """
        Validate surgery room assignment data.

        Args:
            data: The surgery room assignment data to validate.
        """
        # Required fields
        self.validate_required(data, ['surgery_id', 'room_id', 'start_time', 'end_time'])

        # Skip foreign key validation in testing mode
        if not self.testing:
            # Surgery validation
            self.validate_foreign_key(data, 'surgery_id', Surgery)

            # Room validation
            self.validate_foreign_key(data, 'room_id', OperatingRoom, 'room_id')

        # Start time validation
        self.validate_date(data, 'start_time')

        # End time validation
        self.validate_date(data, 'end_time')

        # Validate start and end times
        if 'start_time' in data and data['start_time'] and 'end_time' in data and data['end_time']:
            if data['start_time'] >= data['end_time']:
                self.add_error('end_time', "End time must be after start time")

            # Check for room conflicts if we have a database session and not in testing mode
            if self.db and not self.testing and 'room_id' in data and 'start_time' in data and 'end_time' in data:
                # Get existing assignments for the room
                existing_assignments = self.db.query(SurgeryRoomAssignment).filter(
                    SurgeryRoomAssignment.room_id == data['room_id'],
                    SurgeryRoomAssignment.end_time > data['start_time'],
                    SurgeryRoomAssignment.start_time < data['end_time']
                )

                # Exclude the current assignment if we're updating
                if 'assignment_id' in data:
                    existing_assignments = existing_assignments.filter(
                        SurgeryRoomAssignment.assignment_id != data['assignment_id']
                    )

                # Check if there are any conflicts
                if existing_assignments.first():
                    self.add_error(
                        'room_id',
                        f"Room {data['room_id']} is already booked during this time"
                    )


class SurgeonPreferenceValidator(Validator):
    """Validator for surgeon preference data."""

    def _validate(self, data: Dict[str, Any]) -> None:
        """
        Validate surgeon preference data.

        Args:
            data: The surgeon preference data to validate.
        """
        # Required fields
        self.validate_required(data, ['surgeon_id', 'preference_type', 'preference_value'])

        # Surgeon validation
        self.validate_foreign_key(data, 'surgeon_id', Surgeon)

        # Preference type validation
        self.validate_string(data, 'preference_type', min_length=2, max_length=100)

        # Preference value validation
        self.validate_string(data, 'preference_value')
