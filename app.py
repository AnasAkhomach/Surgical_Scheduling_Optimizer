"""
Application for surgery scheduling with Tabu Search optimization.

This module provides a command-line interface for the surgery scheduling application.
"""

import argparse
import logging
import json
import sys
import os
from datetime import datetime, timedelta

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
from db_config import SessionLocal, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SchedulerApp:
    """
    Application for surgery scheduling with Tabu Search optimization.

    This class provides a command-line interface for the surgery scheduling application.
    """

    def __init__(self):
        """Initialize the application."""
        self.db_session = None
        self.surgeries = []
        self.operating_rooms = []
        self.surgeons = []
        self.surgery_types = []
        self.sds_times_data = {}

    def load_data_from_json(self, surgeries_file, rooms_file, surgeons_file=None, sds_times_file=None):
        """
        Load data from JSON files.

        Args:
            surgeries_file: Path to surgeries JSON file
            rooms_file: Path to operating rooms JSON file
            surgeons_file: Path to surgeons JSON file (optional)
            sds_times_file: Path to sequence-dependent setup times JSON file (optional)

        Returns:
            True if data was loaded successfully, False otherwise
        """
        try:
            # Load surgeries
            with open(surgeries_file, 'r') as f:
                surgeries_data = json.load(f)

            self.surgeries = []
            for surgery_data in surgeries_data:
                surgery = Surgery(
                    surgery_id=surgery_data['surgery_id'],
                    surgery_type_id=surgery_data['surgery_type_id'],
                    duration_minutes=surgery_data['duration_minutes'],
                    surgeon_id=surgery_data['surgeon_id'],
                    urgency_level=surgery_data.get('urgency_level', 'Medium')
                )
                self.surgeries.append(surgery)

            logger.info(f"Loaded {len(self.surgeries)} surgeries from {surgeries_file}")

            # Load operating rooms
            with open(rooms_file, 'r') as f:
                rooms_data = json.load(f)

            self.operating_rooms = []
            for room_data in rooms_data:
                # Parse operational_start_time if provided
                operational_start_time = None
                if 'operational_start_time' in room_data:
                    try:
                        time_str = room_data['operational_start_time']
                        operational_start_time = datetime.strptime(time_str, '%H:%M:%S').time()
                    except ValueError:
                        logger.warning(f"Invalid time format for operational_start_time: {time_str}")

                room = OperatingRoom(
                    room_id=room_data['room_id'],
                    location=room_data.get('location', f"Room {room_data['room_id']}"),
                    operational_start_time=operational_start_time
                )
                self.operating_rooms.append(room)

            logger.info(f"Loaded {len(self.operating_rooms)} operating rooms from {rooms_file}")

            # Load surgeons if provided
            if surgeons_file:
                with open(surgeons_file, 'r') as f:
                    surgeons_data = json.load(f)

                self.surgeons = []
                for surgeon_data in surgeons_data:
                    surgeon = Surgeon(
                        surgeon_id=surgeon_data['surgeon_id'],
                        name=surgeon_data.get('name', f"Surgeon {surgeon_data['surgeon_id']}"),
                        specialization=surgeon_data.get('specialization', 'General'),
                        credentials=surgeon_data.get('credentials', 'MD'),
                        availability=surgeon_data.get('availability', True)
                    )
                    self.surgeons.append(surgeon)

                logger.info(f"Loaded {len(self.surgeons)} surgeons from {surgeons_file}")

            # Load sequence-dependent setup times if provided
            if sds_times_file:
                with open(sds_times_file, 'r') as f:
                    sds_data = json.load(f)

                self.sds_times_data = {}
                for from_type, to_types in sds_data.items():
                    for to_type, setup_time in to_types.items():
                        self.sds_times_data[(int(from_type), int(to_type))] = setup_time

                logger.info(f"Loaded {len(self.sds_times_data)} sequence-dependent setup times from {sds_times_file}")

            return True
        except Exception as e:
            logger.error(f"Error loading data from JSON: {e}")
            return False

    def load_data_from_db(self):
        """
        Load data from database.

        Returns:
            True if data was loaded successfully, False otherwise
        """
        try:
            # Create database session
            self.db_session = SessionLocal()

            # Load surgeries
            self.surgeries = self.db_session.query(Surgery).all()
            logger.info(f"Loaded {len(self.surgeries)} surgeries from database")

            # Load operating rooms
            self.operating_rooms = self.db_session.query(OperatingRoom).all()
            logger.info(f"Loaded {len(self.operating_rooms)} operating rooms from database")

            # Load surgeons
            self.surgeons = self.db_session.query(Surgeon).all()
            logger.info(f"Loaded {len(self.surgeons)} surgeons from database")

            # Load surgery types
            self.surgery_types = self.db_session.query(SurgeryType).all()
            logger.info(f"Loaded {len(self.surgery_types)} surgery types from database")

            # Load sequence-dependent setup times
            sds_times = self.db_session.query(SurgeryType).all()
            # TODO: Implement loading SDST from database

            return True
        except Exception as e:
            logger.error(f"Error loading data from database: {e}")
            return False

    def run_scheduler(self, use_db=False, max_iterations=100, tabu_tenure=10, max_no_improvement=20, time_limit_seconds=300):
        """
        Run the scheduler.

        Args:
            use_db: Whether to use the database
            max_iterations: Maximum number of iterations
            tabu_tenure: Tabu tenure
            max_no_improvement: Maximum number of iterations without improvement
            time_limit_seconds: Time limit in seconds

        Returns:
            List of SurgeryRoomAssignment objects
        """
        # Load data if needed
        if use_db and not self.surgeries:
            if not self.load_data_from_db():
                logger.error("Failed to load data from database")
                return None

        if not self.surgeries or not self.operating_rooms:
            logger.error("No surgeries or operating rooms loaded")
            return None

        # Create optimizer
        optimizer = TabuOptimizer(
            db_session=self.db_session if use_db else None,
            surgeries=self.surgeries,
            operating_rooms=self.operating_rooms,
            sds_times_data=self.sds_times_data,
            tabu_tenure=tabu_tenure,
            max_iterations=max_iterations,
            max_no_improvement=max_no_improvement,
            time_limit_seconds=time_limit_seconds
        )

        # Run optimization
        logger.info("Starting optimization...")
        solution = optimizer.optimize()
        logger.info(f"Optimization complete. Found {len(solution)} assignments")

        return solution

    def print_solution(self, solution):
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

    def save_solution_to_json(self, solution, filename):
        """
        Save a solution to a JSON file.

        Args:
            solution: List of SurgeryRoomAssignment objects
            filename: Output filename

        Returns:
            True if the solution was saved successfully, False otherwise
        """
        try:
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
            return True
        except Exception as e:
            logger.error(f"Error saving solution to JSON: {e}")
            return False

    def close(self):
        """Close the database session."""
        if self.db_session:
            self.db_session.close()
            self.db_session = None

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Surgery Scheduler')
    parser.add_argument('--surgeries', help='Path to surgeries JSON file')
    parser.add_argument('--rooms', help='Path to operating rooms JSON file')
    parser.add_argument('--surgeons', help='Path to surgeons JSON file')
    parser.add_argument('--sds', help='Path to sequence-dependent setup times JSON file')
    parser.add_argument('--output', help='Path to output JSON file')
    parser.add_argument('--use-db', action='store_true', help='Use database instead of JSON files')
    parser.add_argument('--iterations', type=int, default=100, help='Maximum iterations for Tabu Search')
    parser.add_argument('--tabu-size', type=int, default=10, help='Size of tabu list')
    parser.add_argument('--no-improvement', type=int, default=20, help='Maximum iterations without improvement')
    parser.add_argument('--time-limit', type=int, default=300, help='Time limit in seconds')

    args = parser.parse_args()

    app = SchedulerApp()

    # Load data
    if args.use_db:
        if not app.load_data_from_db():
            logger.error("Failed to load data from database. Exiting.")
            return 1
    else:
        if not args.surgeries or not args.rooms:
            logger.error("Surgeries and rooms files are required when not using database. Exiting.")
            return 1

        if not app.load_data_from_json(args.surgeries, args.rooms, args.surgeons, args.sds):
            logger.error("Failed to load data from JSON files. Exiting.")
            return 1

    # Run scheduler
    solution = app.run_scheduler(
        use_db=args.use_db,
        max_iterations=args.iterations,
        tabu_tenure=args.tabu_size,
        max_no_improvement=args.no_improvement,
        time_limit_seconds=args.time_limit
    )

    if not solution:
        logger.error("Scheduler failed to find a solution.")
        app.close()
        return 1

    # Print solution
    app.print_solution(solution)

    # Save solution if output file specified
    if args.output:
        if not app.save_solution_to_json(solution, args.output):
            logger.error("Failed to save solution to JSON file.")
            app.close()
            return 1

    app.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
