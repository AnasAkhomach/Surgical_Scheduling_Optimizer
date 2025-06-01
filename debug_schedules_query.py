from db_config import get_db
from models import Surgery, SurgeryRoomAssignment, OperatingRoom, Surgeon, Patient, SurgeryType
from api.models import UrgencyLevel, SurgeryStatus
from datetime import datetime, date

def test_schedules_query():
    try:
        db = next(get_db())

        # Test the query that's used in the schedules endpoint
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())

        current_assignments = db.query(SurgeryRoomAssignment).filter(
            SurgeryRoomAssignment.start_time >= start_of_day,
            SurgeryRoomAssignment.start_time <= end_of_day
        ).all()

        print(f"Found {len(current_assignments)} assignments for today")

        if current_assignments:
            assignment = current_assignments[0]
            print(f"Testing first assignment: surgery_id={assignment.surgery_id}")

            # Test surgery query
            surgery_db = db.query(Surgery).filter(Surgery.surgery_id == assignment.surgery_id).first()
            if surgery_db:
                print(f"Surgery found: ID {surgery_db.surgery_id}")
                print(f"Surgery urgency_level: {surgery_db.urgency_level}")
                print(f"Surgery status: {surgery_db.status}")

                # Test enum conversion
                if surgery_db.urgency_level:
                    try:
                        urgency_level = UrgencyLevel(surgery_db.urgency_level)
                        print(f"Urgency enum conversion successful: {urgency_level}")
                    except ValueError as e:
                        print(f"Urgency enum conversion failed: {e}")

                if surgery_db.status:
                    try:
                        status = SurgeryStatus(surgery_db.status)
                        print(f"Status enum conversion successful: {status}")
                    except ValueError as e:
                        print(f"Status enum conversion failed: {e}")
            else:
                print("Surgery not found")

        print("Query test completed successfully")

    except Exception as e:
        print(f"Error in query test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_schedules_query()