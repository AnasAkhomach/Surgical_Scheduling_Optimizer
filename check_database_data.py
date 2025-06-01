import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Surgery, SurgeryRoomAssignment, OperatingRoom, Surgeon, Patient, SurgeryType
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/surgery_scheduling")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_and_create_test_data():
    db = SessionLocal()
    try:
        print("Checking database tables...")

        # Check existing data
        surgery_count = db.query(Surgery).count()
        assignment_count = db.query(SurgeryRoomAssignment).count()
        room_count = db.query(OperatingRoom).count()
        surgeon_count = db.query(Surgeon).count()
        patient_count = db.query(Patient).count()
        surgery_type_count = db.query(SurgeryType).count()

        print(f"Surgeries: {surgery_count}")
        print(f"Surgery Room Assignments: {assignment_count}")
        print(f"Operating Rooms: {room_count}")
        print(f"Surgeons: {surgeon_count}")
        print(f"Patients: {patient_count}")
        print(f"Surgery Types: {surgery_type_count}")

        # If we have surgeries but no assignments, create some test assignments
        if surgery_count > 0 and assignment_count == 0 and room_count > 0:
            print("\nCreating test surgery room assignments...")

            # Get first few surgeries and rooms
            surgeries = db.query(Surgery).limit(3).all()
            rooms = db.query(OperatingRoom).limit(2).all()

            if surgeries and rooms:
                base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

                for i, surgery in enumerate(surgeries):
                    room = rooms[i % len(rooms)]
                    start_time = base_time + timedelta(hours=i*2)
                    end_time = start_time + timedelta(minutes=surgery.duration_minutes or 60)

                    assignment = SurgeryRoomAssignment(
                        surgery_id=surgery.surgery_id,
                        room_id=room.room_id,
                        start_time=start_time,
                        end_time=end_time
                    )
                    db.add(assignment)
                    print(f"Created assignment: Surgery {surgery.surgery_id} -> Room {room.room_id} at {start_time}")

                db.commit()
                print(f"Created {len(surgeries)} test assignments")
            else:
                print("No surgeries or rooms found to create assignments")

        # Final count
        final_assignment_count = db.query(SurgeryRoomAssignment).count()
        print(f"\nFinal Surgery Room Assignments: {final_assignment_count}")

        if final_assignment_count > 0:
            print("\nSample assignments:")
            assignments = db.query(SurgeryRoomAssignment).limit(3).all()
            for assignment in assignments:
                print(f"  Assignment {assignment.assignment_id}: Surgery {assignment.surgery_id} -> Room {assignment.room_id}")
                print(f"    Time: {assignment.start_time} to {assignment.end_time}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    check_and_create_test_data()