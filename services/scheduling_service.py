"""
Scheduling service facade for the surgery scheduling application.

This module provides a facade for scheduling operations, coordinating
multiple services to perform complex scheduling tasks.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple

from sqlalchemy.orm import Session

from models import (
    Surgery,
    OperatingRoom,
    Surgeon,
    SurgeryRoomAssignment,
    SurgeryType,
    SurgeryStaffAssignment,
    Staff,
    Patient
)
from services.unit_of_work import UnitOfWork
from services.exceptions import (
    SchedulingError,
    ValidationError,
    ResourceNotFoundError,
    ResourceConflictError
)
from services.validators import (
    SurgeryValidator,
    SurgeryRoomAssignmentValidator
)
from services.surgery_service import SurgeryService
from services.surgeon_service import SurgeonService
from services.operating_room_service import OperatingRoomService
from services.surgery_room_assignment_service import SurgeryRoomAssignmentService
from services.surgery_staff_assignment_service import SurgeryStaffAssignmentService
from services.notification_service import notification_service
from services.calendar_service import CalendarService
from services.logger_config import logger

# Import these conditionally to avoid import errors in tests
try:
    from tabu_optimizer import TabuOptimizer
    from feasibility_checker import FeasibilityChecker
except ImportError:
    # Create mock classes for testing
    class TabuOptimizer:
        def __init__(self, *args, **kwargs):
            pass

        def optimize(self, *args, **kwargs):
            return None

    class FeasibilityChecker:
        def __init__(self, *args, **kwargs):
            pass

        def is_feasible(self, *args, **kwargs):
            return True


class SchedulingService:
    """
    Facade for scheduling operations.

    This service coordinates multiple services to perform complex scheduling tasks.
    """

    def __init__(self, testing=False):
        """
        Initialize the scheduling service.

        Args:
            testing: Whether the service is being used in a test environment.
        """
        self.testing = testing
        self.surgery_service = SurgeryService(testing=testing)
        self.surgeon_service = SurgeonService()
        self.operating_room_service = OperatingRoomService()
        self.surgery_room_assignment_service = SurgeryRoomAssignmentService()
        self.surgery_staff_assignment_service = SurgeryStaffAssignmentService()
        self.calendar_service = CalendarService(testing=testing)
        self.feasibility_checker = FeasibilityChecker()

    def schedule_surgery(
        self,
        surgery_data: Dict[str, Any],
        room_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        staff_assignments: Optional[List[Dict[str, Any]]] = None,
        notify_surgeon: bool = True,
        update_calendar: bool = True
    ) -> int:
        """
        Schedule a surgery.

        This method creates a new surgery, assigns it to a room, and optionally
        assigns staff and sends notifications.

        Args:
            surgery_data: The surgery data.
            room_id: The ID of the room to assign.
            start_time: The start time of the surgery.
            staff_assignments: Staff assignments for the surgery.
            notify_surgeon: Whether to notify the surgeon.
            update_calendar: Whether to update the surgeon's calendar.

        Returns:
            The ID of the created surgery.

        Raises:
            ValidationError: If the surgery data is invalid.
            ResourceNotFoundError: If a required resource is not found.
            ResourceConflictError: If there is a conflict with existing resources.
            SchedulingError: If the surgery cannot be scheduled.
        """
        # Validate surgery data
        validator = SurgeryValidator()
        validator.validate_and_raise(surgery_data)

        with UnitOfWork(testing=self.testing) as uow:
            try:
                # Create the surgery
                surgery_id = self.surgery_service.create_surgery(uow.db, surgery_data)
                if not surgery_id:
                    raise SchedulingError("Failed to create surgery")

                # Get the created surgery
                surgery = uow.db.query(Surgery).filter_by(surgery_id=surgery_id).first()
                if not surgery:
                    raise ResourceNotFoundError("Surgery", surgery_id)

                # Assign to room if specified
                if room_id and start_time:
                    # Calculate end time based on duration
                    end_time = start_time + timedelta(minutes=surgery.duration_minutes)

                    # Create room assignment
                    assignment_data = {
                        'surgery_id': surgery_id,
                        'room_id': room_id,
                        'start_time': start_time,
                        'end_time': end_time
                    }

                    # Validate room assignment
                    room_validator = SurgeryRoomAssignmentValidator(uow.db, testing=self.testing)
                    room_validator.validate_and_raise(assignment_data)

                    # Create the assignment
                    assignment_id = self.surgery_room_assignment_service.create_surgery_room_assignment(
                        uow.db, assignment_data
                    )

                    if not assignment_id:
                        raise SchedulingError("Failed to create room assignment")

                    # Update surgery with room and times
                    self.surgery_service.update_surgery(
                        uow.db,
                        surgery_id,
                        {
                            'room_id': room_id,
                            'start_time': start_time,
                            'end_time': end_time
                        }
                    )

                # Assign staff if specified
                if staff_assignments:
                    for staff_data in staff_assignments:
                        staff_data['surgery_id'] = surgery_id
                        assignment_id = self.surgery_staff_assignment_service.create_surgery_staff_assignment(
                            uow.db, staff_data
                        )

                        if not assignment_id:
                            raise SchedulingError(f"Failed to create staff assignment for staff {staff_data['staff_id']}")

                # Notify surgeon if requested
                if notify_surgeon and surgery.surgeon_id:
                    surgeon = uow.db.query(Surgeon).filter_by(surgeon_id=surgery.surgeon_id).first()
                    if surgeon:
                        self._notify_surgeon_about_surgery(surgeon, surgery)

                # Update surgeon's calendar if requested
                if update_calendar and surgery.surgeon_id and surgery.start_time:
                    surgeon = uow.db.query(Surgeon).filter_by(surgeon_id=surgery.surgeon_id).first()
                    if surgeon:
                        self._update_surgeon_calendar(surgeon, None, surgery)

                return surgery_id

            except ValidationError as e:
                logger.error(f"Validation error scheduling surgery: {e}")
                raise

            except ResourceNotFoundError as e:
                logger.error(f"Resource not found scheduling surgery: {e}")
                raise

            except ResourceConflictError as e:
                logger.error(f"Resource conflict scheduling surgery: {e}")
                raise

            except Exception as e:
                logger.error(f"Error scheduling surgery: {e}")
                raise SchedulingError(f"Failed to schedule surgery: {e}")

    def reschedule_surgery(
        self,
        surgery_id: int,
        room_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        notify_surgeon: bool = True,
        update_calendar: bool = True
    ) -> bool:
        """
        Reschedule a surgery.

        This method updates the room assignment for a surgery and optionally
        sends notifications.

        Args:
            surgery_id: The ID of the surgery to reschedule.
            room_id: The ID of the new room.
            start_time: The new start time.
            notify_surgeon: Whether to notify the surgeon.
            update_calendar: Whether to update the surgeon's calendar.

        Returns:
            True if the surgery was rescheduled, False otherwise.

        Raises:
            ResourceNotFoundError: If the surgery is not found.
            ValidationError: If the new schedule is invalid.
            ResourceConflictError: If there is a conflict with existing resources.
            SchedulingError: If the surgery cannot be rescheduled.
        """
        with UnitOfWork(testing=self.testing) as uow:
            try:
                # Get the surgery
                surgery = uow.db.query(Surgery).filter_by(surgery_id=surgery_id).first()
                if not surgery:
                    raise ResourceNotFoundError("Surgery", surgery_id)

                # Get the original assignment
                original_assignment = (
                    uow.db.query(SurgeryRoomAssignment)
                    .filter_by(surgery_id=surgery_id)
                    .first()
                )

                # Store original surgery for calendar update
                original_surgery = surgery

                # Calculate end time based on duration
                end_time = start_time + timedelta(minutes=surgery.duration_minutes)

                if original_assignment:
                    # Update existing assignment
                    update_data = {}
                    if room_id:
                        update_data['room_id'] = room_id
                    if start_time:
                        update_data['start_time'] = start_time
                        update_data['end_time'] = end_time

                    # Validate the updated assignment
                    assignment_data = {
                        'assignment_id': original_assignment.assignment_id,
                        'surgery_id': surgery_id,
                        'room_id': room_id or original_assignment.room_id,
                        'start_time': start_time or original_assignment.start_time,
                        'end_time': end_time or original_assignment.end_time
                    }

                    room_validator = SurgeryRoomAssignmentValidator(uow.db, testing=self.testing)
                    room_validator.validate_and_raise(assignment_data)

                    # Update the assignment
                    success = self.surgery_room_assignment_service.update_surgery_room_assignment(
                        uow.db, original_assignment.assignment_id, update_data
                    )

                    if not success:
                        raise SchedulingError("Failed to update room assignment")
                else:
                    # Create new assignment
                    if not room_id or not start_time:
                        raise ValidationError("Room ID and start time are required for new assignments")

                    assignment_data = {
                        'surgery_id': surgery_id,
                        'room_id': room_id,
                        'start_time': start_time,
                        'end_time': end_time
                    }

                    room_validator = SurgeryRoomAssignmentValidator(uow.db, testing=self.testing)
                    room_validator.validate_and_raise(assignment_data)

                    assignment_id = self.surgery_room_assignment_service.create_surgery_room_assignment(
                        uow.db, assignment_data
                    )

                    if not assignment_id:
                        raise SchedulingError("Failed to create room assignment")

                # Update surgery with new room and times
                update_data = {}
                if room_id:
                    update_data['room_id'] = room_id
                if start_time:
                    update_data['start_time'] = start_time
                    update_data['end_time'] = end_time

                success = self.surgery_service.update_surgery(
                    uow.db, surgery_id, update_data
                )

                if not success:
                    raise SchedulingError("Failed to update surgery")

                # Get the updated surgery
                updated_surgery = uow.db.query(Surgery).filter_by(surgery_id=surgery_id).first()

                # Notify surgeon if requested
                if notify_surgeon and updated_surgery.surgeon_id:
                    surgeon = uow.db.query(Surgeon).filter_by(surgeon_id=updated_surgery.surgeon_id).first()
                    if surgeon:
                        self._notify_surgeon_about_rescheduling(surgeon, updated_surgery)

                # Update surgeon's calendar if requested
                if update_calendar and updated_surgery.surgeon_id:
                    surgeon = uow.db.query(Surgeon).filter_by(surgeon_id=updated_surgery.surgeon_id).first()
                    if surgeon:
                        self._update_surgeon_calendar(surgeon, original_surgery, updated_surgery)

                return True

            except ValidationError as e:
                logger.error(f"Validation error rescheduling surgery: {e}")
                raise

            except ResourceNotFoundError as e:
                logger.error(f"Resource not found rescheduling surgery: {e}")
                raise

            except ResourceConflictError as e:
                logger.error(f"Resource conflict rescheduling surgery: {e}")
                raise

            except Exception as e:
                logger.error(f"Error rescheduling surgery: {e}")
                raise SchedulingError(f"Failed to reschedule surgery: {e}")

    def _notify_surgeon_about_surgery(self, surgeon, surgery):
        """
        Notify a surgeon about a new surgery.

        Args:
            surgeon: The surgeon to notify.
            surgery: The surgery to notify about.
        """
        if not hasattr(surgeon, 'contact_info') or not surgeon.contact_info:
            logger.warning(f"Surgeon {surgeon.name} does not have contact information")
            return

        # Get surgery type name
        surgery_type_name = "Unknown"
        if hasattr(surgery, 'surgery_type_details') and surgery.surgery_type_details:
            surgery_type_name = surgery.surgery_type_details.name

        # Get room location
        room_location = "Unknown"
        if hasattr(surgery, 'room') and surgery.room:
            room_location = surgery.room.location

        # Format date and time
        surgery_date = "TBD"
        surgery_time = "TBD"
        if surgery.start_time:
            surgery_date = surgery.start_time.strftime("%A, %B %d, %Y")
            surgery_time = surgery.start_time.strftime("%I:%M %p")

        # Send notification
        notification_service.send_notification(
            recipient_email=surgeon.contact_info,
            subject=f"New Surgery Scheduled: {surgery_type_name}",
            body=f"""
            <h2>New Surgery Scheduled</h2>
            <p>Dear Dr. {surgeon.name},</p>
            <p>A new surgery has been scheduled for you:</p>
            <ul>
                <li><strong>Surgery Type:</strong> {surgery_type_name}</li>
                <li><strong>Date:</strong> {surgery_date}</li>
                <li><strong>Time:</strong> {surgery_time}</li>
                <li><strong>Location:</strong> {room_location}</li>
                <li><strong>Duration:</strong> {surgery.duration_minutes} minutes</li>
            </ul>
            <p>Please review your calendar for details.</p>
            """,
            notification_type="email",
            priority="high"
        )

    def _notify_surgeon_about_rescheduling(self, surgeon, surgery):
        """
        Notify a surgeon about a rescheduled surgery.

        Args:
            surgeon: The surgeon to notify.
            surgery: The surgery to notify about.
        """
        if not hasattr(surgeon, 'contact_info') or not surgeon.contact_info:
            logger.warning(f"Surgeon {surgeon.name} does not have contact information")
            return

        # Get surgery type name
        surgery_type_name = "Unknown"
        if hasattr(surgery, 'surgery_type_details') and surgery.surgery_type_details:
            surgery_type_name = surgery.surgery_type_details.name

        # Get room location
        room_location = "Unknown"
        if hasattr(surgery, 'room') and surgery.room:
            room_location = surgery.room.location

        # Format date and time
        surgery_date = "TBD"
        surgery_time = "TBD"
        if surgery.start_time:
            surgery_date = surgery.start_time.strftime("%A, %B %d, %Y")
            surgery_time = surgery.start_time.strftime("%I:%M %p")

        # Send notification
        notification_service.send_notification(
            recipient_email=surgeon.contact_info,
            subject=f"Surgery Rescheduled: {surgery_type_name}",
            body=f"""
            <h2>Surgery Rescheduled</h2>
            <p>Dear Dr. {surgeon.name},</p>
            <p>A surgery has been rescheduled:</p>
            <ul>
                <li><strong>Surgery Type:</strong> {surgery_type_name}</li>
                <li><strong>New Date:</strong> {surgery_date}</li>
                <li><strong>New Time:</strong> {surgery_time}</li>
                <li><strong>New Location:</strong> {room_location}</li>
                <li><strong>Duration:</strong> {surgery.duration_minutes} minutes</li>
            </ul>
            <p>Please review your calendar for details.</p>
            """,
            notification_type="email",
            priority="urgent"
        )

    def _update_surgeon_calendar(self, surgeon, original_surgery, new_surgery):
        """
        Update a surgeon's calendar.

        Args:
            surgeon: The surgeon whose calendar to update.
            original_surgery: The original surgery (can be None).
            new_surgery: The new surgery.
        """
        try:
            self.calendar_service.update_surgeon_calendar(surgeon, original_surgery, new_surgery)
        except Exception as e:
            logger.error(f"Error updating surgeon calendar: {e}")
            # Don't raise the exception, as this is a non-critical operation
