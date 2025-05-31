"""Service layer for managing operating rooms in the surgical scheduling system."""

from sqlalchemy.exc import SQLAlchemyError
from models import OperatingRoom


class OperatingRoomService:
    """Provides services for managing operating rooms."""

    @staticmethod
    def create_operating_room(db, operating_room_data):
        """Creates a new operating room record."""
        try:
            new_room = OperatingRoom(location=operating_room_data["location"])
            db.add(new_room)
            db.commit()
            db.refresh(new_room)
            print(f"Operating room {new_room.room_id} created successfully.")
            return new_room.room_id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating operating room: {e}")
            return None

    @staticmethod
    def get_operating_room(db, room_id):
        """Retrieves an operating room by room_id and returns an OperatingRoom instance."""
        try:
            operating_room = db.query(OperatingRoom).filter_by(room_id=room_id).first()
            if operating_room:
                return operating_room
            print(f"No operating room found with ID {room_id}")
            return None
        except SQLAlchemyError as e:
            print(f"Error retrieving operating room: {e}")
            return None

    @staticmethod
    def update_operating_room(db, room_id, update_fields):
        """Updates an existing operating room record."""
        try:
            result = db.query(OperatingRoom).filter_by(room_id=room_id).update(update_fields)
            db.commit()
            if result:
                print(f"Operating room {room_id} updated successfully.")
                return True
            print(f"No operating room found with ID {room_id} or no new data to update.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error updating operating room: {e}")
            return False

    @staticmethod
    def delete_operating_room(db, room_id):
        """Deletes an operating room record."""
        try:
            result = db.query(OperatingRoom).filter_by(room_id=room_id).delete()
            db.commit()
            if result:
                print(f"Operating room {room_id} deleted successfully.")
                return True
            print(f"No operating room found with ID {room_id}.")
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting operating room: {e}")
            return False

    @staticmethod
    def get_all_operating_rooms(db, skip: int = 0, limit: int = 100):
        """Retrieves all operating room records with pagination."""
        try:
            operating_rooms = db.query(OperatingRoom).offset(skip).limit(limit).all()
            return operating_rooms
        except SQLAlchemyError as e:
            print(f"Error retrieving all operating rooms: {e}")
            return []
