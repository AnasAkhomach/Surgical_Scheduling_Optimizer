"""Service layer for managing surgeries in the surgical scheduling system."""

import logging
from sqlalchemy.exc import SQLAlchemyError
from .calendar_service import CalendarService
from .notification_service import notification_service
from models import Surgery

logger = logging.getLogger(__name__)


class SurgeryService:
    """Provides services for managing surgeries."""

    def __init__(self, testing=False):
        self.calendar_service = CalendarService(testing=testing)

    @staticmethod
    def create_surgery(db, surgery_data):
        """Creates a new surgery record in the database."""
        try:
            new_surgery = Surgery(
                patient_id=surgery_data.get("patient_id"),
                scheduled_date=surgery_data["scheduled_date"],
                surgery_type_id=surgery_data.get("surgery_type_id"),
                urgency_level=surgery_data["urgency_level"],
                duration_minutes=surgery_data["duration_minutes"],
                status=surgery_data.get("status", "Scheduled"),
                start_time=surgery_data.get("start_time"),
                end_time=surgery_data.get("end_time"),
                surgeon_id=surgery_data.get("surgeon_id"),
                room_id=surgery_data.get("room_id"),
            )
            db.add(new_surgery)
            db.commit()
            db.refresh(new_surgery)
            logger.info("Surgery %s created successfully.", new_surgery.surgery_id)
            return new_surgery.surgery_id
        except SQLAlchemyError as e:
            db.rollback()
            logger.error("Error creating surgery: %s", e)
            return None

    @staticmethod
    def update_surgery(db, surgery_id, update_fields):
        """Updates an existing surgery record."""
        try:
            result = (
                db.query(Surgery).filter_by(surgery_id=surgery_id).update(update_fields)
            )
            db.commit()
            if result:
                logger.info("Surgery %s updated successfully.", surgery_id)
                return True
            logger.warning("No changes made to surgery %s.", surgery_id)
            return False
        except SQLAlchemyError as e:
            db.rollback()
            logger.error("Error updating surgery: %s", e)
            return False

    @staticmethod
    def delete_surgery(db, surgery_id):
        """Deletes a surgery record."""
        try:
            result = db.query(Surgery).filter_by(surgery_id=surgery_id).delete()
            db.commit()
            if result:
                logger.info("Surgery %s deleted successfully.", surgery_id)
                return True
            logger.warning("Surgery %s not found.", surgery_id)
            return False
        except SQLAlchemyError as e:
            db.rollback()
            logger.error("Error deleting surgery: %s", e)
            return False

    @staticmethod
    def get_surgery(db, surgery_id):
        """Fetches a surgery by its ID."""
        try:
            surgery = db.query(Surgery).filter_by(surgery_id=surgery_id).first()
            if surgery:
                return surgery
            logger.warning("Surgery %s not found.", surgery_id)
            return None
        except SQLAlchemyError as e:
            logger.error("Error fetching surgery: %s", e)
            return None

    def schedule_surgery(self, db, surgeon, surgery_details):
        """Schedules a surgery, updates the surgeon's calendar, and sends notifications."""
        try:
            surgery_id = self.create_surgery(db, surgery_details)
            if not surgery_id:
                logger.error("Failed to save surgery to database.")
                return "Failed to save surgery to database."
            self.calendar_service.update_surgeon_calendar(
                surgeon, None, surgery_details
            )
            notification_service.send_notification(
                recipient_email=surgeon["email"],
                subject="New Surgery Scheduled",
                body=(
                    f"A new surgery {surgery_details['surgery_type']} has been scheduled for {surgery_details['scheduled_date']}.",
                ),
            )
            logger.info("Surgery successfully scheduled and notifications sent.")
            return "Surgery successfully scheduled and notifications sent."
        except SQLAlchemyError as e:
            logger.error("Database error scheduling surgery: %s", e)
            return f"A database error occurred: {e}"
        except Exception as e:
            logger.error("Error scheduling surgery: %s", e)
            return f"An error occurred: {e}"
