# seed_database.py
import os
from dotenv import load_dotenv
from initialize_data import (
    initialize_patients_sqlalchemy,
    initialize_staff_members_sqlalchemy,
    initialize_surgeons_sqlalchemy,
    initialize_operating_rooms_sqlalchemy,
    initialize_surgery_equipments_sqlalchemy,
    initialize_surgeries_sqlalchemy, # Added missing import
)
from models import OperatingRoom, Patient, Staff, Surgeon, SurgeryEquipment

from datetime import date, timedelta

# Example seed data for MySQL
# This data is illustrative. Actual data comes from initialize_data functions.
operating_rooms_example = [
    OperatingRoom(location="OR-1"),
    OperatingRoom(location="OR-2"),
]

patients_example = [
    Patient(
        name="John Doe",
        dob=date(1980, 5, 15),
        contact_info="555-1234",
        privacy_consent=True,
    ),
    Patient(
        name="Jane Smith",
        dob=date(1990, 8, 22),
        contact_info="555-5678",
        privacy_consent=True,
    ),
]

staff_members_example = [
    Staff(
        name="Alice Brown",
        role="Nurse",
        contact_info="555-1111",
        specializations="General",
        availability=True,
    ),
    Staff(
        name="Bob White",
        role="Anesthetist",
        contact_info="555-2222",
        specializations="Anesthesia",
        availability=True,
    ),
]

surgeons_example = [
    Surgeon(
        name="Dr. House",
        contact_info="555-3333",
        specialization="Cardiology",
        credentials="MD, PhD",
        availability=True,
    ),
    Surgeon(
        name="Dr. Grey",
        contact_info="555-4444",
        specialization="Neurosurgery",
        credentials="MD",
        availability=True,
    ),
]

surgery_equipments_example = [
    SurgeryEquipment(name="Scalpel", type="Cutting", availability=True),
    SurgeryEquipment(name="Retractor", type="Holding", availability=True),
]


# Removed SessionLocal import as session will be passed in

def seed_initial_data(db_session):
    """Seeds the database with initial data using the provided session."""
    try:
        # Add base entities first (no foreign key dependencies)
        db_session.add_all(initialize_operating_rooms_sqlalchemy())
        db_session.add_all(initialize_patients_sqlalchemy())
        db_session.add_all(initialize_staff_members_sqlalchemy())
        db_session.add_all(initialize_surgeons_sqlalchemy())
        db_session.add_all(initialize_surgery_equipments_sqlalchemy())

        # Commit base entities first so they get IDs assigned
        db_session.commit()

        # Now add surgeries which depend on the above entities
        db_session.add_all(initialize_surgeries_sqlalchemy())

        # Final commit for dependent entities
        db_session.commit()
        # print("Seed data inserted successfully using provided session.") # Logging can be handled by caller
    except Exception as e:
        db_session.rollback()
        # print(f"Error seeding data using provided session: {e}") # Error handling/logging by caller
        raise # Re-raise the exception to be handled by the caller
    # finally:
        # The session is managed by the caller, so no db_session.close() here.


if __name__ == "__main__":
    # Load environment variables if necessary (e.g., for database connection strings)
    load_dotenv()
    from db_config import SessionLocal # Import here for standalone execution

    print("Starting database seeding (standalone execution)...")
    db = SessionLocal()
    try:
        seed_initial_data(db) # Call the modified function
        print("Database seeding completed (standalone execution).")
    except Exception as e:
        print(f"Error during standalone database seeding: {e}")
    finally:
        db.close()
