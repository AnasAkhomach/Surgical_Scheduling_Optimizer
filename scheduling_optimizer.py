import logging
import random
import time
import copy
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from models import ( # Assuming models.py defines these
    Surgery,
    OperatingRoom,
    Surgeon,
    SurgeryEquipment,
    SurgeryRoomAssignment,
    SurgeryEquipmentUsage,
    SurgeryType,  # Added
    SequenceDependentSetupTime,  # Added
    Base
)
from tabu_list import TabuList

# New refactored components
from feasibility_checker import FeasibilityChecker
from scheduler_utils import SchedulerUtils
from solution_evaluator import SolutionEvaluator
from neighborhood_strategies import NeighborhoodStrategies
from tabu_search_core import TabuSearchCore

# Initialize logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TabuSearchScheduler:
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self.surgeries: List[Surgery] = []
        self.operating_rooms: List[OperatingRoom] = []
        self.surgeons: List[Surgeon] = []
        self.equipment: List[SurgeryEquipment] = []
        self.surgery_room_assignments: List[SurgeryRoomAssignment] = [] # In-memory assignments for current run
        self.sds_times_data: Dict[tuple[int, int], int] = {} # To store {(from_type_id, to_type_id): setup_minutes}
        self.surgery_types: List[SurgeryType] = [] # To store SurgeryType objects

        self._load_initial_data() # This will now also load SDST data

        # Initialize refactored components
        self.feasibility_checker = FeasibilityChecker(
            db_session=self.db_session,
            surgeries_data=self.surgeries, # Corrected parameter name
            operating_rooms_data=self.operating_rooms, # Corrected parameter name
            all_surgery_equipments_data=self.equipment # Added missing parameter
        )
        self.scheduler_utils = SchedulerUtils(
            db_session=self.db_session,
            surgeries=self.surgeries,
            operating_rooms=self.operating_rooms,
            feasibility_checker=self.feasibility_checker,
            surgery_equipments=self.equipment, # Added missing parameter
            surgery_equipment_usages=[], # Added missing parameter, assuming empty list is acceptable for now
            sds_times_data=self.sds_times_data # Pass the loaded SDST data
        )
        self.solution_evaluator = SolutionEvaluator(
            db_session=self.db_session,
            weights=None,  # Or load from config
            sds_times_data=self.sds_times_data # Pass the loaded SDST data
        )
        self.neighborhood_strategies = NeighborhoodStrategies(
            db_session=self.db_session,
            surgeries_data=self.surgeries, # Corrected parameter name
            operating_rooms_data=self.operating_rooms, # Corrected parameter name
            surgeons_data=self.surgeons, # Corrected parameter name
            feasibility_checker=self.feasibility_checker,
            scheduler_utils=self.scheduler_utils,
            sds_times_data=self.sds_times_data # Pass SDST data
        )
        self.tabu_search_core = TabuSearchCore(
            solution_evaluator=self.solution_evaluator,
            neighborhood_generator=self.neighborhood_strategies, # Corrected parameter name
            initial_solution_assignments=self.surgery_room_assignments, # This will be an empty list initially
            feasibility_checker=self.feasibility_checker # Add feasibility_checker here
        )
        # self.tabu_search_core will be properly initialized in the run() method with the actual initial solution

        logger.info("TabuSearchScheduler initialized with refactored components. TabuSearchCore will be re-initialized in run().")

    def _load_initial_data(self):
        """Loads initial data from the database if a session is provided."""
        if self.db_session:
            try:
                self.surgeries = self.db_session.query(Surgery).all()
                self.operating_rooms = self.db_session.query(OperatingRoom).all()
                self.surgeons = self.db_session.query(Surgeon).all()
                self.equipment = self.db_session.query(SurgeryEquipment).all()
                self.surgery_types = self.db_session.query(SurgeryType).all() # Load Surgery Types

                # Load Sequence Dependent Setup Times and format them for SchedulerUtils
                sds_times_raw = self.db_session.query(SequenceDependentSetupTime).all()
                self.sds_times_data = {
                    (sds.from_surgery_type_id, sds.to_surgery_type_id): sds.setup_time_minutes
                    for sds in sds_times_raw
                }

                logger.info(
                    f"Loaded {len(self.surgeries)} surgeries, {len(self.operating_rooms)} rooms, "
                    f"{len(self.surgeons)} surgeons, {len(self.equipment)} equipment items, "
                    f"{len(self.surgery_types)} surgery types, and {len(self.sds_times_data)} SDST entries from DB."
                )
            except Exception as e:
                logger.error(f"Error loading data from database: {e}")
                # Fallback to empty lists if DB load fails
                self.surgeries = []
                self.operating_rooms = []
                self.surgeons = []
                self.equipment = []
                self.surgery_types = []
                self.sds_times_data = {}
        else:
            logger.warning(
                "No DB session provided. Scheduler will operate with empty initial data unless populated otherwise."
            )

    def run(
        self,
        max_iterations=100,
        tabu_tenure=10,
        max_iterations_without_improvement_ratio=0.25,
        time_limit_seconds=None,
    ):
        """Main Tabu Search optimization loop using refactored components."""
        logger.info(
            "Starting Tabu Search with parameters: max_iterations=%s, tabu_tenure=%s, "
            "max_iterations_without_improvement_ratio=%s, time_limit_seconds=%s",
            max_iterations,
            tabu_tenure,
            max_iterations_without_improvement_ratio,
            time_limit_seconds,
        )

        if not self.surgeries or not self.operating_rooms:
            logger.error("Cannot run optimizer: missing surgeries or rooms data.")
            return None

        # Generate initial solution using SchedulerUtils
        # The initialize_solution method in SchedulerUtils populates its own list and returns it.
        generated_assignments = self.scheduler_utils.initialize_solution()
        self.surgery_room_assignments = generated_assignments # Update the scheduler's list with the generated assignments
        initial_solution_assignments = copy.deepcopy(self.surgery_room_assignments)

        if not initial_solution_assignments:
            logger.error("Failed to generate an initial feasible solution.")
            return None

        logger.info(f"Initial solution generated with {len(initial_solution_assignments)} assignments.")

        # Re-initialize TabuSearchCore here with the actual initial_solution_assignments
        self.tabu_search_core = TabuSearchCore(
            solution_evaluator=self.solution_evaluator,
            neighborhood_generator=self.neighborhood_strategies,
            initial_solution_assignments=initial_solution_assignments,
            feasibility_checker=self.feasibility_checker # Add feasibility_checker here
        )
        logger.info("TabuSearchCore re-initialized in run() method with populated initial solution.")

        # Run the Tabu Search algorithm using the newly initialized TabuSearchCore
        best_solution_assignments, best_score = self.tabu_search_core.search(
            max_iterations=max_iterations,
            tabu_tenure=tabu_tenure,
            max_iterations_without_improvement_ratio=max_iterations_without_improvement_ratio,
            time_limit_seconds=time_limit_seconds
            # surgeries=self.surgeries, # Pass necessary data if needed by search or its components
            # operating_rooms=self.operating_rooms
        )
        # Note: The search method in TabuSearchCore returns a tuple (best_solution_assignments, best_score)
        # We need to handle this if we only expect assignments, or use both.

        if not best_solution_assignments:
            logger.error("Tabu search did not return a best solution.")
            return None

        self.surgery_room_assignments = best_solution_assignments # Update scheduler's main assignments

        # Placeholder schedule times for the final evaluation
        # These should ideally match the context used within TabuSearchCore or be derived from the best_solution_assignments
        final_eval_start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        final_eval_end_time = final_eval_start_time + timedelta(days=1)

        best_score = self.solution_evaluator.evaluate_solution(best_solution_assignments, final_eval_start_time, final_eval_end_time)
        logger.info(f"Optimization finished. Best score: {best_score}")

        # Save the final schedule to the database
        if self.db_session:
            self._save_schedule_to_db(best_solution_assignments)

        return best_solution_assignments

    def _save_schedule_to_db(self, schedule_assignments: List[SurgeryRoomAssignment]):
        """Saves the final schedule assignments to the database."""
        logger.info("DB session provided. Saving final schedule to database...")
        try:
            # Begin a transaction
            with self.db_session.begin_nested(): # Use begin_nested for safety with outer transactions
                surgery_ids_in_schedule = [getattr(assignment, "surgery_id") for assignment in schedule_assignments]

                # Delete existing assignments for these surgeries to avoid conflicts
                # This assumes we are rescheduling these specific surgeries
                if surgery_ids_in_schedule:
                    deleted_count = (
                        self.db_session.query(SurgeryRoomAssignment)
                        .filter(SurgeryRoomAssignment.surgery_id.in_(surgery_ids_in_schedule))
                        .delete(synchronize_session=False)
                    )
                    logger.info(f"Cleared {deleted_count} existing surgery room assignments from DB for scheduled surgeries.")

                    # Also clear related equipment usage for these surgeries before adding new ones
                    self.db_session.query(SurgeryEquipmentUsage).filter(
                        SurgeryEquipmentUsage.surgery_id.in_(surgery_ids_in_schedule)
                    ).delete(synchronize_session=False)
                    logger.info(f"Cleared existing equipment usage records for scheduled surgeries.")


                # Add new assignments and update surgery statuses
                for assignment_data in schedule_assignments:
                    # assignment_data is now expected to be a SurgeryRoomAssignment model instance
                    surgery_id = assignment_data.surgery_id
                    room_id = assignment_data.room_id
                    start_time_dt = assignment_data.start_time # Should be a datetime object
                    end_time_dt = assignment_data.end_time   # Should be a datetime object

                    if not isinstance(start_time_dt, datetime) or not isinstance(end_time_dt, datetime):
                        logger.error(f"Assignment for surgery {surgery_id} has invalid datetime types: start={type(start_time_dt)}, end={type(end_time_dt)}. Skipping DB save for this assignment.")
                        continue

                    surgery_obj = self.db_session.query(Surgery).filter(Surgery.surgery_id == surgery_id).first()
                    if surgery_obj:
                        surgery_obj.status = "Scheduled"
                        surgery_obj.start_time = start_time_dt
                        surgery_obj.end_time = end_time_dt
                        surgery_obj.room_id = room_id

                        # Create a new SurgeryRoomAssignment for the DB session
                        # This ensures we are adding a session-bound object if assignment_data is transient
                        # or to simply reflect the final state.
                        new_db_assignment = SurgeryRoomAssignment(
                            surgery_id=surgery_id,
                            room_id=room_id,
                            start_time=start_time_dt, # Pass datetime object directly
                            end_time=end_time_dt,     # Pass datetime object directly
                        )
                        self.db_session.add(new_db_assignment)
                        logger.debug(f"Assigning to DB: Surgery {surgery_id} in Room {room_id} from {start_time_dt.isoformat()} to {end_time_dt.isoformat()}")

                        # Add equipment usage records
                        # Find the original surgery object from self.surgeries to get its details like type
                        original_surgery_details = next((s for s in self.surgeries if s.surgery_id == surgery_id), None)
                        if original_surgery_details:
                            required_equipment_dict = self.feasibility_checker._get_required_equipment_for_surgery(original_surgery_details)
                            for eq_name, quantity in required_equipment_dict.items():
                                equipment_db_obj = self.db_session.query(SurgeryEquipment).filter(SurgeryEquipment.name == eq_name).first()
                                if equipment_db_obj:
                                    # Use the correct schema fields: usage_start_time and usage_end_time
                                    # Calculate equipment usage times based on surgery schedule
                                    surgery_start = assignment.start_time
                                    surgery_end = assignment.end_time

                                    usage_record = SurgeryEquipmentUsage(
                                        surgery_id=surgery_id,
                                        equipment_id=equipment_db_obj.equipment_id,
                                        usage_start_time=surgery_start,
                                        usage_end_time=surgery_end
                                    )
                                    self.db_session.add(usage_record)
                                else:
                                    logger.warning(f"Equipment '{eq_name}' not found in DB for surgery {surgery_id}.")
                        else:
                            logger.warning(f"Original surgery details for {surgery_id} not found for equipment usage logging.")

                    else:
                        logger.warning(f"Surgery with ID {surgery_id} not found in database. Skipping DB assignment.")

                self.db_session.commit() # Commit the nested transaction
            logger.info(
                f"Successfully saved {len(schedule_assignments)} assignments to the database with related updates."
            )
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error saving schedule to database: {e}")

# Keep the main execution block for now, may need adjustments
if __name__ == "__main__":
    from db_config import get_db, engine # Import get_db and engine from db_config
    from initialize_data import initialize_surgeries, initialize_operating_rooms, initialize_surgeons # Assuming these exist

    # Ensure tables are created using the engine from db_config
    # This should ideally be handled by setup_database.py, but good to have a check or ensure it's run prior.
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Ensured tables are created using db_config engine.")
    except Exception as e:
        logger.error(f"Error ensuring tables are created with db_config engine: {e}")
        # Decide if to proceed or exit if table creation check fails

    db_session_instance: Optional[Session] = None
    try:
        # Get a DB session using the centralized get_db function
        db_context = get_db()
        db_session_instance = next(db_context)

        # Seed the database with initial data
        from seed_database import seed_initial_data # Assuming this function exists
        seed_initial_data(db_session_instance)
        logger.info("Initial data seeding attempted.")

    except Exception as e:
        logger.error(f"Failed to connect to database, setup session, or seed data: {e}")

    if db_session_instance:
        try:
            logger.info("Running Tabu Search Optimizer with DB session...")
            # Create scheduler instance WITH DB session
            scheduler_db = TabuSearchScheduler(db_session=db_session_instance)

            # If scheduler._load_initial_data() doesn't populate sufficiently or you want to use mocks for testing:
            # scheduler_db.surgeries = initialize_surgeries() # Make sure these return DB model instances or compatible objects
            # scheduler_db.operating_rooms = initialize_operating_rooms()
            # scheduler_db.surgeons = initialize_surgeons()
            # scheduler_db.feasibility_checker.surgeries = scheduler_db.surgeries # Update components if manually setting data
            # scheduler_db.scheduler_utils.surgeries = scheduler_db.surgeries
            # ... and so on for other components and data lists

            # Ensure components are re-initialized or updated if data is loaded/mocked after main __init__
            # This is important if _load_initial_data in __init__ was skipped or insufficient
            if not scheduler_db.surgeries: # Example check, if data wasn't loaded
                 logger.warning("Initial data not loaded from DB, attempting to use mock data if available.")
                 # Potentially load mock data here if initialize_data functions are robust
                 # For a real scenario, ensure data is loaded correctly in _load_initial_data

            final_schedule_assignments_db = scheduler_db.run(
                max_iterations=50, # Reduced for faster testing
                tabu_tenure=5,
                max_iterations_without_improvement_ratio=0.4,
                time_limit_seconds=120, # Increased time limit slightly
            )

            if final_schedule_assignments_db:
                logger.info(
                    "DB optimization complete. Final schedule assignments (also saved to DB if successful):"
                )
                for i, assignment in enumerate(final_schedule_assignments_db):
                    surgery_id = getattr(assignment, "surgery_id", "N/A")
                    room_id = getattr(assignment, "room_id", "N/A")
                    start_time = getattr(assignment, "start_time", "N/A")
                    logger.info(
                        f"  {i + 1}. Surgery {surgery_id} in Room {room_id} at {start_time}"
                    )
            else:
                logger.info("DB-based optimization did not produce a schedule.")

        except Exception as e:
            logger.error(f"An error occurred during DB-based optimization: {e}", exc_info=True)
        finally:
            db_session_instance.close()
            logger.info("DB session closed.")
    else:
        logger.warning(
            "Skipping DB-based optimization example as DB session could not be established."
        )
