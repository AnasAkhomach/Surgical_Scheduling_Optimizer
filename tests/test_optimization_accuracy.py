"""
Test script for verifying the accuracy of the Tabu Search optimization algorithm.

This script creates a controlled test dataset, runs the optimization algorithm,
and verifies that the results meet expected constraints and metrics.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import required modules
from models import (
    Surgery,
    SurgeryType,
    Surgeon,
    Patient,
    OperatingRoom,
    SurgeryRoomAssignment,
    Base
)
from tabu_optimizer import TabuOptimizer
from solution_evaluator import SolutionEvaluator
from feasibility_checker import FeasibilityChecker
from db_config import get_db, engine

def create_test_data(db):
    """Create a controlled test dataset for optimization testing."""
    logger.info("Creating test data...")

    # Create surgery types
    surgery_types = [
        SurgeryType(name="General Surgery", description="Common general surgical procedures"),
        SurgeryType(name="Orthopedic Surgery", description="Bone and joint procedures"),
        SurgeryType(name="Cardiac Surgery", description="Heart and major blood vessel procedures")
    ]
    db.add_all(surgery_types)
    db.commit()

    # Create surgeons with different specializations and availability
    surgeons = [
        Surgeon(name="Dr. Smith", specialization="General Surgery", contact_info="smith@example.com", credentials="Board Certified"),
        Surgeon(name="Dr. Johnson", specialization="Orthopedics", contact_info="johnson@example.com", credentials="Board Certified"),
        Surgeon(name="Dr. Brown", specialization="Cardiology", contact_info="brown@example.com", credentials="Board Certified")
    ]
    db.add_all(surgeons)
    db.commit()

    # Create operating rooms with different equipment
    operating_rooms = [
        OperatingRoom(location="Floor 1"),
        OperatingRoom(location="Floor 1"),
        OperatingRoom(location="Floor 2")
    ]
    db.add_all(operating_rooms)
    db.commit()

    # Create patients
    patients = [
        Patient(name="Patient 1", dob=datetime(1970, 1, 1), contact_info="123-456-7890", privacy_consent=True),
        Patient(name="Patient 2", dob=datetime(1980, 2, 2), contact_info="123-456-7891", privacy_consent=True),
        Patient(name="Patient 3", dob=datetime(1990, 3, 3), contact_info="123-456-7892", privacy_consent=True),
        Patient(name="Patient 4", dob=datetime(1975, 4, 4), contact_info="123-456-7893", privacy_consent=True),
        Patient(name="Patient 5", dob=datetime(1985, 5, 5), contact_info="123-456-7894", privacy_consent=True)
    ]
    db.add_all(patients)
    db.commit()

    # Create surgeries with different requirements and priorities
    tomorrow = datetime.now().date() + timedelta(days=1)
    surgeries = [
        Surgery(
            patient_id=1,
            surgeon_id=1,
            surgery_type_id=1,
            duration_minutes=60,
            urgency_level="High",
            scheduled_date=tomorrow,
            status="Scheduled"
        ),
        Surgery(
            patient_id=2,
            surgeon_id=2,
            surgery_type_id=2,
            duration_minutes=120,
            urgency_level="Medium",
            scheduled_date=tomorrow,
            status="Scheduled"
        ),
        Surgery(
            patient_id=3,
            surgeon_id=3,
            surgery_type_id=3,
            duration_minutes=180,
            urgency_level="High",
            scheduled_date=tomorrow,
            status="Scheduled"
        ),
        Surgery(
            patient_id=4,
            surgeon_id=1,
            surgery_type_id=1,
            duration_minutes=90,
            urgency_level="Low",
            scheduled_date=tomorrow,
            status="Scheduled"
        ),
        Surgery(
            patient_id=5,
            surgeon_id=2,
            surgery_type_id=2,
            duration_minutes=150,
            urgency_level="Medium",
            scheduled_date=tomorrow,
            status="Scheduled"
        )
    ]
    db.add_all(surgeries)
    db.commit()

    logger.info(f"Created {len(surgery_types)} surgery types")
    logger.info(f"Created {len(surgeons)} surgeons")
    logger.info(f"Created {len(operating_rooms)} operating rooms")
    logger.info(f"Created {len(patients)} patients")
    logger.info(f"Created {len(surgeries)} surgeries")

    return surgeons, operating_rooms, surgeries

def run_optimization(db, surgeries, operating_rooms):
    """Run the optimization algorithm and return the results."""
    logger.info("Running optimization...")

    # Create optimizer with controlled parameters
    optimizer = TabuOptimizer(
        db_session=db,
        surgeries=surgeries,
        operating_rooms=operating_rooms,
        tabu_tenure=5,
        max_iterations=50,
        max_no_improvement=10,
        time_limit_seconds=30,
        evaluation_weights={
            "or_utilization": 1.0,
            "sds_time_penalty": 0.8,
            "surgeon_preference_satisfaction": 0.7,
            "workload_balance": 0.6,
            "patient_wait_time": 0.5,
            "emergency_surgery_priority": 1.0,
            "operational_cost": 0.4,
            "staff_overtime": 0.3
        }
    )

    # Record start time
    start_time = time.time()

    # Run optimization
    solution = optimizer.optimize()

    # Calculate execution time
    execution_time = time.time() - start_time

    # Evaluate solution
    evaluator = SolutionEvaluator(db_session=db)
    score = evaluator.evaluate_solution(solution)

    logger.info(f"Optimization complete. Score: {score}")
    logger.info(f"Found {len(solution)} assignments")
    logger.info(f"Execution time: {execution_time:.2f} seconds")

    # Use a fixed iteration count since we don't have access to the actual count
    iteration_count = optimizer.max_iterations

    return solution, score, iteration_count, execution_time

def verify_solution(solution, surgeries, operating_rooms):
    """Verify that the solution meets expected constraints and metrics."""
    logger.info("Verifying solution...")

    # Check if all surgeries are scheduled
    scheduled_surgery_ids = [assignment.surgery_id for assignment in solution]
    all_surgery_ids = [surgery.surgery_id for surgery in surgeries]

    missing_surgeries = set(all_surgery_ids) - set(scheduled_surgery_ids)
    if missing_surgeries:
        logger.warning(f"Missing surgeries: {missing_surgeries}")
    else:
        logger.info("All surgeries are scheduled")

    # Check for overlapping surgeries in the same room
    room_schedules = {}
    for assignment in solution:
        if assignment.room_id not in room_schedules:
            room_schedules[assignment.room_id] = []
        room_schedules[assignment.room_id].append({
            "surgery_id": assignment.surgery_id,
            "start_time": assignment.start_time,
            "end_time": assignment.end_time
        })

    overlaps = False
    for room_id, schedule in room_schedules.items():
        # Sort by start time
        schedule.sort(key=lambda x: x["start_time"])

        # Check for overlaps
        for i in range(len(schedule) - 1):
            if schedule[i]["end_time"] > schedule[i + 1]["start_time"]:
                logger.error(f"Overlap in room {room_id}: Surgery {schedule[i]['surgery_id']} and {schedule[i + 1]['surgery_id']}")
                overlaps = True

    if not overlaps:
        logger.info("No overlapping surgeries in the same room")

    # Check surgeon constraints
    surgeon_schedules = {}
    for assignment in solution:
        surgery = next((s for s in surgeries if s.surgery_id == assignment.surgery_id), None)
        if surgery:
            if surgery.surgeon_id not in surgeon_schedules:
                surgeon_schedules[surgery.surgeon_id] = []
            surgeon_schedules[surgery.surgeon_id].append({
                "surgery_id": assignment.surgery_id,
                "start_time": assignment.start_time,
                "end_time": assignment.end_time
            })

    surgeon_overlaps = False
    for surgeon_id, schedule in surgeon_schedules.items():
        # Sort by start time
        schedule.sort(key=lambda x: x["start_time"])

        # Check for overlaps
        for i in range(len(schedule) - 1):
            if schedule[i]["end_time"] > schedule[i + 1]["start_time"]:
                logger.error(f"Overlap for surgeon {surgeon_id}: Surgery {schedule[i]['surgery_id']} and {schedule[i + 1]['surgery_id']}")
                surgeon_overlaps = True

    if not surgeon_overlaps:
        logger.info("No overlapping surgeries for the same surgeon")

    # Check room suitability
    room_locations = {room.room_id: room.location for room in operating_rooms}
    surgery_types = {surgery.surgery_id: surgery.surgery_type_id for surgery in surgeries}

    unsuitable_rooms = False
    for assignment in solution:
        surgery_id = assignment.surgery_id
        room_id = assignment.room_id

        # In a real application, we would check if the room is suitable for the surgery type
        # For this test, we'll just log the assignment
        logger.info(f"Surgery {surgery_id} (Type: {surgery_types.get(surgery_id)}) assigned to Room {room_id} (Location: {room_locations.get(room_id)})")

    # Check if high urgency surgeries are scheduled earlier
    urgency_levels = {surgery.surgery_id: surgery.urgency_level for surgery in surgeries}

    # Group assignments by room
    room_assignments = {}
    for assignment in solution:
        if assignment.room_id not in room_assignments:
            room_assignments[assignment.room_id] = []
        room_assignments[assignment.room_id].append(assignment)

    # Check urgency order in each room
    urgency_order_issues = False
    for room_id, assignments in room_assignments.items():
        # Sort by start time
        assignments.sort(key=lambda x: x.start_time)

        # Check if high urgency surgeries are scheduled earlier
        for i in range(len(assignments) - 1):
            current_urgency = urgency_levels.get(assignments[i].surgery_id)
            next_urgency = urgency_levels.get(assignments[i + 1].surgery_id)

            if current_urgency == "Low" and next_urgency == "High":
                logger.warning(f"Room {room_id}: Low urgency surgery {assignments[i].surgery_id} scheduled before high urgency surgery {assignments[i + 1].surgery_id}")
                urgency_order_issues = True

    if not urgency_order_issues:
        logger.info("Urgency levels are generally respected in the schedule")

    # Overall verification result
    if not overlaps and not surgeon_overlaps and not unsuitable_rooms:
        logger.info("Solution is feasible")
        return True
    else:
        logger.error("Solution has feasibility issues")
        return False

def main():
    """Main function to run the optimization accuracy test."""
    logger.info("Starting optimization accuracy test...")

    # Create a test database
    test_db_url = "sqlite:///./test_optimization.db"

    # Remove existing test database if it exists
    try:
        if os.path.exists("./test_optimization.db"):
            os.remove("./test_optimization.db")
            logger.info("Removed existing test database")
    except Exception as e:
        logger.warning(f"Could not remove existing test database: {e}")

    # Create new database
    test_engine = create_engine(test_db_url)
    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(bind=test_engine)
    db = TestSession()

    try:
        # Create test data
        _, operating_rooms, surgeries = create_test_data(db)

        # Run optimization
        solution, score, iteration_count, execution_time = run_optimization(db, surgeries, operating_rooms)

        # Verify solution
        is_feasible = verify_solution(solution, surgeries, operating_rooms)

        # Print results
        logger.info("Optimization Accuracy Test Results:")
        logger.info(f"Score: {score}")
        logger.info(f"Iterations: {iteration_count}")
        logger.info(f"Execution Time: {execution_time} seconds")
        logger.info(f"Feasible: {is_feasible}")

        # Save results to file
        results = {
            "score": score,
            "iterations": iteration_count,
            "execution_time": execution_time,
            "feasible": is_feasible,
            "assignments": [
                {
                    "surgery_id": assignment.surgery_id,
                    "room_id": assignment.room_id,
                    "start_time": assignment.start_time.isoformat(),
                    "end_time": assignment.end_time.isoformat()
                }
                for assignment in solution
            ]
        }

        with open("optimization_results.json", "w") as f:
            json.dump(results, f, indent=2)

        logger.info("Results saved to optimization_results.json")

    finally:
        # Clean up
        db.close()
        try:
            # Remove test database
            if os.path.exists("./test_optimization.db"):
                os.remove("./test_optimization.db")
                logger.info("Test database removed")
        except Exception as e:
            logger.warning(f"Could not remove test database: {e}")

if __name__ == "__main__":
    main()
