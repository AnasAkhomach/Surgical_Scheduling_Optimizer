"""
Test script for the Tabu Search optimizer.

This script tests the Tabu Search optimizer with sample data.
"""

import sys
import os
import logging
import json
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models import (
    Surgery,
    OperatingRoom,
    Surgeon,
    SurgeryType,
    SurgeryRoomAssignment
)
from feasibility_checker import FeasibilityChecker
from neighborhood_strategies import NeighborhoodStrategies
from solution_evaluator import SolutionEvaluator
from tabu_optimizer import TabuOptimizer

def load_sample_data():
    """
    Load sample data for testing.

    Returns:
        Tuple of (surgeries, operating_rooms, surgeons, surgery_types, sds_times_data)
    """
    # Create sample surgeons
    surgeons = [
        Surgeon(surgeon_id=1, name="Dr. Smith", specialization="General", credentials="MD", availability=True),
        Surgeon(surgeon_id=2, name="Dr. Jones", specialization="Orthopedic", credentials="MD", availability=True),
        Surgeon(surgeon_id=3, name="Dr. Wilson", specialization="Cardiac", credentials="MD, PhD", availability=True)
    ]

    # Create sample surgery types
    surgery_types = [
        SurgeryType(type_id=1, name="Appendectomy", description="Appendix removal"),
        SurgeryType(type_id=2, name="Knee Replacement", description="Total knee replacement"),
        SurgeryType(type_id=3, name="Coronary Bypass", description="Heart bypass surgery")
    ]

    # Create sample operating rooms
    operating_rooms = [
        OperatingRoom(room_id=1, location="Main Building - Room 101"),
        OperatingRoom(room_id=2, location="Main Building - Room 102"),
        OperatingRoom(room_id=3, location="West Wing - Room 201")
    ]

    # Create sample surgeries
    surgeries = [
        Surgery(
            surgery_id=1,
            surgery_type_id=1,
            duration_minutes=60,
            surgeon_id=1,
            urgency_level="Medium"
        ),
        Surgery(
            surgery_id=2,
            surgery_type_id=2,
            duration_minutes=120,
            surgeon_id=2,
            urgency_level="Low"
        ),
        Surgery(
            surgery_id=3,
            surgery_type_id=3,
            duration_minutes=180,
            surgeon_id=3,
            urgency_level="High"
        ),
        Surgery(
            surgery_id=4,
            surgery_type_id=1,
            duration_minutes=90,
            surgeon_id=1,
            urgency_level="High"
        ),
        Surgery(
            surgery_id=5,
            surgery_type_id=2,
            duration_minutes=150,
            surgeon_id=2,
            urgency_level="Medium"
        )
    ]

    # Create sample sequence-dependent setup times
    sds_times_data = {
        (1, 1): 15,  # Same type, minimal setup
        (1, 2): 30,  # Different types, more setup
        (1, 3): 45,  # Very different types, lots of setup
        (2, 1): 30,
        (2, 2): 15,
        (2, 3): 30,
        (3, 1): 45,
        (3, 2): 30,
        (3, 3): 15
    }

    return surgeries, operating_rooms, surgeons, surgery_types, sds_times_data

def create_mock_db_session(surgeries, operating_rooms, surgeons, surgery_types):
    """
    Create a mock database session for testing.

    Args:
        surgeries: List of Surgery objects
        operating_rooms: List of OperatingRoom objects
        surgeons: List of Surgeon objects
        surgery_types: List of SurgeryType objects

    Returns:
        Mock database session
    """
    class MockQuery:
        def __init__(self, data):
            self.data = data

        def filter_by(self, **kwargs):
            filtered = []
            for item in self.data:
                match = True
                for key, value in kwargs.items():
                    if not hasattr(item, key) or getattr(item, key) != value:
                        match = False
                        break
                if match:
                    filtered.append(item)
            return self

        def all(self):
            return self.data

        def first(self):
            return self.data[0] if self.data else None

    class MockDBSession:
        def __init__(self):
            self.data = {
                Surgery: surgeries,
                OperatingRoom: operating_rooms,
                Surgeon: surgeons,
                SurgeryType: surgery_types
            }

        def query(self, model):
            return MockQuery(self.data.get(model, []))

        def add(self, obj):
            model = type(obj)
            if model not in self.data:
                self.data[model] = []
            self.data[model].append(obj)

        def commit(self):
            pass

        def rollback(self):
            pass

        def close(self):
            pass

    return MockDBSession()

def print_solution(solution):
    """
    Print a solution in a readable format.

    Args:
        solution: List of SurgeryRoomAssignment objects
    """
    if not solution:
        print("Empty solution")
        return

    # Sort by room and start time
    sorted_solution = sorted(solution, key=lambda a: (a.room_id, a.start_time))

    # Group by room
    rooms = {}
    for assignment in sorted_solution:
        if assignment.room_id not in rooms:
            rooms[assignment.room_id] = []
        rooms[assignment.room_id].append(assignment)

    # Print schedule by room
    for room_id, assignments in rooms.items():
        print(f"\nRoom {room_id}:")
        print("-" * 60)
        print(f"{'Surgery ID':<12}{'Start Time':<20}{'End Time':<20}{'Duration':<10}")
        print("-" * 60)

        for assignment in assignments:
            start_time = assignment.start_time.strftime("%Y-%m-%d %H:%M")
            end_time = assignment.end_time.strftime("%Y-%m-%d %H:%M")
            duration = (assignment.end_time - assignment.start_time).total_seconds() / 60
            print(f"{assignment.surgery_id:<12}{start_time:<20}{end_time:<20}{duration:<10.0f}")

def save_solution_to_json(solution, filename):
    """
    Save a solution to a JSON file.

    Args:
        solution: List of SurgeryRoomAssignment objects
        filename: Output filename
    """
    # Convert solution to serializable format
    serializable_solution = []
    for assignment in solution:
        serializable_solution.append({
            "surgery_id": assignment.surgery_id,
            "room_id": assignment.room_id,
            "start_time": assignment.start_time.isoformat(),
            "end_time": assignment.end_time.isoformat(),
            "duration_minutes": (assignment.end_time - assignment.start_time).total_seconds() / 60
        })

    # Save to file
    with open(filename, 'w') as f:
        json.dump(serializable_solution, f, indent=2)

    logger.info(f"Solution saved to {filename}")

def main():
    """Main function to test the Tabu Search optimizer."""
    # Load sample data
    surgeries, operating_rooms, surgeons, surgery_types, sds_times_data = load_sample_data()

    # Create mock database session
    db_session = create_mock_db_session(surgeries, operating_rooms, surgeons, surgery_types)

    # Create Tabu Search optimizer
    optimizer = TabuOptimizer(
        db_session=db_session,
        surgeries=surgeries,
        operating_rooms=operating_rooms,
        sds_times_data=sds_times_data,
        tabu_tenure=5,
        max_iterations=20,
        max_no_improvement=10,
        time_limit_seconds=30
    )

    # Run optimization
    logger.info("Starting optimization...")
    solution = optimizer.optimize()
    logger.info(f"Optimization complete. Found {len(solution)} assignments")

    # Print solution
    print_solution(solution)

    # Save solution to JSON
    save_solution_to_json(solution, "solution.json")

    return 0

if __name__ == "__main__":
    sys.exit(main())
