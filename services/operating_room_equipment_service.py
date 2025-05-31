"""Service layer for managing operating room equipment in the surgical scheduling system."""

from sqlalchemy.exc import SQLAlchemyError
from models import OperatingRoomEquipment


class OperatingRoomEquipmentService:
    """Provides services for managing operating room equipment."""

    @staticmethod
    def get_equipment(db, skip: int = 0, limit: int = 100):
        """Retrieves all operating room equipment records."""
        try:
            return db.query(OperatingRoomEquipment).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Error fetching all operating room equipment: {e}")
            return []

    @staticmethod
    def create_operating_room_equipment(db, equipment_data):  # Added db parameter
        """Creates a new operating room equipment record."""
        try:
            new_equipment = OperatingRoomEquipment(**equipment_data)
            db.add(new_equipment)
            db.commit()
            db.refresh(new_equipment)  # Added refresh
            print(f"Operating room equipment {new_equipment.id} created successfully.")
            return new_equipment.id  # Return ID
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating operating room equipment: {e}")
            return None  # Return None on error

    @staticmethod
    def get_operating_room_equipment(db, equipment_id):  # Added db parameter
        """Retrieves operating room equipment by ID."""
        try:
            equipment = (
                db.query(OperatingRoomEquipment).filter_by(id=equipment_id).first()
            )
            if equipment:
                return equipment
            print(f"No operating room equipment found with ID {equipment_id}")
            return None
        except SQLAlchemyError as e:
            print(f"Error fetching operating room equipment: {e}")
            return None

    @staticmethod
    def update_operating_room_equipment(
        db, equipment_id, update_fields
    ):  # Added db parameter
        """Updates existing operating room equipment."""
        try:
            result = (
                db.query(OperatingRoomEquipment)
                .filter_by(id=equipment_id)
                .update(update_fields)
            )
            db.commit()
            if result:
                print(f"Operating room equipment {equipment_id} updated successfully.")
                return True
            print(
                f"No operating room equipment found with ID {equipment_id} or no new data to update."
            )
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating operating room equipment: {e}")
            return False

    @staticmethod
    def delete_operating_room_equipment(db, equipment_id):  # Added db parameter
        """Deletes operating room equipment."""
        try:
            result = (
                db.query(OperatingRoomEquipment).filter_by(id=equipment_id).delete()
            )
            db.commit()
            if result:
                print(f"Operating room equipment {equipment_id} deleted successfully.")
                return True
            print(f"No operating room equipment found with ID {equipment_id}.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting operating room equipment: {e}")
            return False
