"""
Tabu Search optimizer for surgery scheduling.

This module provides a comprehensive Tabu Search optimizer that works with the full models
and uses components for feasibility checking, neighborhood generation, and solution evaluation.
"""

import logging
import random
import copy
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union

from models import (
    Surgery,
    OperatingRoom,
    Surgeon,
    SurgeryRoomAssignment
)
from feasibility_checker import FeasibilityChecker
from neighborhood_strategies import NeighborhoodStrategies
from solution_evaluator import SolutionEvaluator

logger = logging.getLogger(__name__)

class TabuList:
    """
    Tabu list for the Tabu Search algorithm.

    This class maintains a list of tabu moves and their tenures.
    """

    def __init__(self, default_tenure=10, min_tenure=None, max_tenure=None):
        """
        Initialize the tabu list.

        Args:
            default_tenure: Default tenure for tabu moves
            min_tenure: Minimum tenure for tabu moves (for randomized tenures)
            max_tenure: Maximum tenure for tabu moves (for randomized tenures)
        """
        self.tabu_items = {}  # Dictionary of tabu moves and their remaining tenures
        self.default_tenure = default_tenure
        self.min_tenure = min_tenure if min_tenure is not None else max(1, default_tenure // 2)
        self.max_tenure = max_tenure if max_tenure is not None else default_tenure

    def add(self, move, tenure=None):
        """
        Add a move to the tabu list.

        Args:
            move: The move to add (must be hashable)
            tenure: Optional specific tenure for this move
        """
        if tenure is None:
            # Use randomized tenure if not specified
            tenure = random.randint(self.min_tenure, self.max_tenure)

        self.tabu_items[move] = tenure
        logger.debug(f"Added move {move} to tabu list with tenure {tenure}")

    def is_tabu(self, move):
        """
        Check if a move is tabu.

        Args:
            move: The move to check

        Returns:
            True if the move is tabu, False otherwise
        """
        return move in self.tabu_items

    def get_tenure(self, move):
        """
        Get the remaining tenure of a move.

        Args:
            move: The move to check

        Returns:
            Remaining tenure, or 0 if the move is not tabu
        """
        return self.tabu_items.get(move, 0)

    def decrement_tenure(self):
        """Decrement the tenure of all tabu moves and remove expired ones."""
        expired_moves = []

        for move, tenure in self.tabu_items.items():
            if tenure <= 1:
                expired_moves.append(move)
            else:
                self.tabu_items[move] = tenure - 1

        for move in expired_moves:
            del self.tabu_items[move]
            logger.debug(f"Removed expired move {move} from tabu list")

    def clear(self):
        """Clear the tabu list."""
        self.tabu_items.clear()
        logger.debug("Cleared tabu list")

    def increase_all_tenures(self, factor=1.5, duration=10):
        """
        Temporarily increase all tenures by a factor.

        Args:
            factor: Factor to increase tenures by
            duration: Number of iterations the increase should last
        """
        for move in self.tabu_items:
            self.tabu_items[move] = int(self.tabu_items[move] * factor)

        logger.debug(f"Increased all tabu tenures by factor {factor}")

        # Store the original min/max tenures
        self.original_min_tenure = self.min_tenure
        self.original_max_tenure = self.max_tenure

        # Increase min/max tenures for future moves
        self.min_tenure = int(self.min_tenure * factor)
        self.max_tenure = int(self.max_tenure * factor)

        # Schedule a reset after the specified duration
        self.reset_after = duration

    def reset_tenures(self):
        """Reset tenures to original values."""
        if hasattr(self, 'original_min_tenure') and hasattr(self, 'original_max_tenure'):
            self.min_tenure = self.original_min_tenure
            self.max_tenure = self.original_max_tenure
            logger.debug("Reset tabu tenures to original values")

class TabuOptimizer:
    """
    Tabu Search optimizer for surgery scheduling.

    This class implements a comprehensive Tabu Search algorithm for optimizing surgery schedules,
    using components for feasibility checking, neighborhood generation, and solution evaluation.
    """

    def __init__(
        self,
        db_session,
        surgeries=None,
        operating_rooms=None,
        sds_times_data=None,
        tabu_tenure=10,
        max_iterations=100,
        max_no_improvement=20,
        time_limit_seconds=300,
        evaluation_weights=None
    ):
        """
        Initialize the Tabu Search optimizer.

        Args:
            db_session: Database session for querying data
            surgeries: List of Surgery objects
            operating_rooms: List of OperatingRoom objects
            sds_times_data: Dictionary of sequence-dependent setup times
            tabu_tenure: Default tenure for tabu moves
            max_iterations: Maximum number of iterations
            max_no_improvement: Maximum number of iterations without improvement
            time_limit_seconds: Time limit in seconds
            evaluation_weights: Dictionary of weights for solution evaluation
        """
        self.db_session = db_session
        self.surgeries = surgeries if surgeries else []
        self.operating_rooms = operating_rooms if operating_rooms else []
        self.sds_times_data = sds_times_data if sds_times_data else {}

        # Load data from database if not provided
        if db_session and (not surgeries or not operating_rooms):
            self._load_data_from_db()

        # Initialize components
        self.feasibility_checker = FeasibilityChecker(db_session)
        self.solution_evaluator = SolutionEvaluator(db_session, evaluation_weights, sds_times_data)
        self.neighborhood_generator = NeighborhoodStrategies(
            db_session,
            self.surgeries,
            self.operating_rooms,
            self.feasibility_checker,
            sds_times_data
        )

        # Tabu Search parameters
        self.tabu_tenure = tabu_tenure
        self.max_iterations = max_iterations
        self.max_no_improvement = max_no_improvement
        self.time_limit_seconds = time_limit_seconds

        logger.info(f"TabuOptimizer initialized with {len(self.surgeries)} surgeries and {len(self.operating_rooms)} operating rooms")

    def _load_data_from_db(self):
        """Load surgeries and operating rooms from database."""
        try:
            if not self.surgeries:
                self.surgeries = self.db_session.query(Surgery).all()
                logger.info(f"Loaded {len(self.surgeries)} surgeries from database")

            if not self.operating_rooms:
                self.operating_rooms = self.db_session.query(OperatingRoom).all()
                logger.info(f"Loaded {len(self.operating_rooms)} operating rooms from database")
        except Exception as e:
            logger.error(f"Error loading data from database: {e}")

    def initialize_solution(self):
        """
        Generate an initial feasible solution.

        Returns:
            List of SurgeryRoomAssignment objects
        """
        logger.info("Generating initial solution")

        # Try to generate a random solution first
        solution = self.neighborhood_generator.initialize_solution_randomly()

        if solution:
            logger.info(f"Generated random initial solution with {len(solution)} assignments")
            return solution

        # If random solution fails, use a greedy approach
        logger.info("Random solution generation failed, using greedy approach")

        # Sort surgeries by urgency and duration
        sorted_surgeries = sorted(
            self.surgeries,
            key=lambda s: (
                {'High': 0, 'Medium': 1, 'Low': 2}.get(getattr(s, 'urgency_level', 'Medium'), 1),
                -getattr(s, 'duration_minutes', 60)
            )
        )

        # Initialize empty solution
        solution = []

        # Track room schedules
        room_schedules = {room.room_id: [] for room in self.operating_rooms}

        # Assign surgeries to rooms
        for surgery in sorted_surgeries:
            # Find the best room and time slot for this surgery
            best_room = None
            best_start_time = None

            for room in self.operating_rooms:
                # Determine start time based on room schedule
                if not room_schedules[room.room_id]:
                    # First surgery in this room, start at 8:00 AM
                    start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
                else:
                    # Get the end time of the last surgery in this room
                    last_end_time = room_schedules[room.room_id][-1].end_time

                    # Add setup time if we have SDST data
                    setup_time = 15  # Default setup time in minutes
                    if self.sds_times_data and room_schedules[room.room_id]:
                        last_surgery = room_schedules[room.room_id][-1].surgery_id
                        last_surgery_obj = next((s for s in self.surgeries if s.surgery_id == last_surgery), None)

                        if last_surgery_obj and hasattr(last_surgery_obj, 'surgery_type_id') and hasattr(surgery, 'surgery_type_id'):
                            last_type_id = last_surgery_obj.surgery_type_id
                            current_type_id = surgery.surgery_type_id
                            setup_time = self.sds_times_data.get((last_type_id, current_type_id), 15)

                    # Start time is the end time of the last surgery plus setup time
                    start_time = last_end_time + timedelta(minutes=setup_time)

                # Calculate end time
                duration = getattr(surgery, 'duration_minutes', 60)  # Default to 60 minutes if not specified
                end_time = start_time + timedelta(minutes=duration)

                # Check if this assignment is feasible
                if self.feasibility_checker.is_feasible(
                    surgery.surgery_id,
                    room.room_id,
                    start_time,
                    end_time,
                    solution
                ):
                    # If we don't have a best room yet, or this room allows an earlier start
                    if best_room is None or start_time < best_start_time:
                        best_room = room
                        best_start_time = start_time

            # If we found a feasible room, create the assignment
            if best_room:
                duration = getattr(surgery, 'duration_minutes', 60)
                end_time = best_start_time + timedelta(minutes=duration)

                assignment = SurgeryRoomAssignment(
                    surgery_id=surgery.surgery_id,
                    room_id=best_room.room_id,
                    start_time=best_start_time,
                    end_time=end_time
                )

                # Add to solution and room schedule
                solution.append(assignment)
                room_schedules[best_room.room_id].append(assignment)

                logger.debug(f"Assigned surgery {surgery.surgery_id} to room {best_room.room_id} at {best_start_time}")

        logger.info(f"Generated greedy initial solution with {len(solution)} assignments")
        return solution

    def optimize(self, initial_solution=None):
        """
        Run the Tabu Search optimization algorithm.

        Args:
            initial_solution: Optional initial solution

        Returns:
            Best solution found (list of SurgeryRoomAssignment objects)
        """
        # Generate initial solution if not provided
        if initial_solution is None:
            current_solution = self.initialize_solution()
        else:
            current_solution = copy.deepcopy(initial_solution)

        if not current_solution:
            logger.warning("Failed to generate an initial solution")
            return []

        # Evaluate initial solution
        current_score = self.solution_evaluator.evaluate_solution(current_solution)
        best_solution = copy.deepcopy(current_solution)
        best_score = current_score

        logger.info(f"Initial solution score: {best_score:.4f}")

        # Initialize tabu list
        tabu_list = TabuList(default_tenure=self.tabu_tenure)

        # Initialize counters and timers
        iterations_without_improvement = 0
        start_time = time.time()

        # Main optimization loop
        for iteration in range(self.max_iterations):
            # Check termination conditions
            if iterations_without_improvement >= self.max_no_improvement:
                logger.info(f"Stopping: {self.max_no_improvement} iterations without improvement")
                break

            if self.time_limit_seconds and time.time() - start_time > self.time_limit_seconds:
                logger.info(f"Stopping: time limit of {self.time_limit_seconds} seconds reached")
                break

            # Decrement tabu tenures
            tabu_list.decrement_tenure()

            # Generate neighbor solutions
            neighbors = self.neighborhood_generator.generate_neighbor_solutions(current_solution, tabu_list)

            if not neighbors:
                logger.warning("No feasible neighbors found")
                break

            # Find best non-tabu neighbor or best tabu neighbor that meets aspiration criterion
            best_neighbor = None
            best_neighbor_score = float('-inf')
            best_neighbor_move = None

            for neighbor in neighbors:
                neighbor_solution = neighbor['assignments']
                neighbor_move = neighbor['move']

                # Evaluate neighbor
                neighbor_score = self.solution_evaluator.evaluate_solution(neighbor_solution)

                # Check if move is tabu
                is_tabu = tabu_list.is_tabu(neighbor_move)

                # Apply aspiration criterion: accept tabu move if it's better than the best solution so far
                if not is_tabu or neighbor_score > best_score:
                    if neighbor_score > best_neighbor_score:
                        best_neighbor = neighbor_solution
                        best_neighbor_score = neighbor_score
                        best_neighbor_move = neighbor_move

            # If no non-tabu neighbor found, pick the best tabu neighbor
            if best_neighbor is None and neighbors:
                best_neighbor = max(neighbors, key=lambda n: self.solution_evaluator.evaluate_solution(n['assignments']))
                best_neighbor_solution = best_neighbor['assignments']
                best_neighbor_score = self.solution_evaluator.evaluate_solution(best_neighbor_solution)
                best_neighbor_move = best_neighbor['move']
                best_neighbor = best_neighbor_solution

            # Update current solution
            current_solution = best_neighbor
            current_score = best_neighbor_score

            # Add move to tabu list
            tabu_list.add(best_neighbor_move)

            # Update best solution if improved
            if current_score > best_score:
                best_solution = copy.deepcopy(current_solution)
                best_score = current_score
                iterations_without_improvement = 0
                logger.info(f"Iteration {iteration+1}: New best solution found with score {best_score:.4f}")
            else:
                iterations_without_improvement += 1
                logger.info(f"Iteration {iteration+1}: No improvement, current best score {best_score:.4f}")

            # Apply diversification if stuck
            if iterations_without_improvement == self.max_no_improvement // 2:
                logger.info("Applying diversification strategy")

                # Increase tabu tenures temporarily
                tabu_list.increase_all_tenures(factor=1.5, duration=10)

                # Generate a partially random solution
                diversified_solution = self._diversify_solution(current_solution)

                if diversified_solution:
                    current_solution = diversified_solution
                    current_score = self.solution_evaluator.evaluate_solution(current_solution)
                    logger.info(f"Diversified solution score: {current_score:.4f}")

        logger.info(f"Optimization complete. Best score: {best_score:.4f}")
        return best_solution

    def _diversify_solution(self, solution):
        """
        Apply diversification to a solution.

        Args:
            solution: Current solution

        Returns:
            Diversified solution
        """
        # Randomly select a subset of surgeries to reschedule
        if not solution:
            return None

        num_to_reschedule = max(1, len(solution) // 3)
        to_reschedule = random.sample(solution, num_to_reschedule)

        # Keep the assignments that we're not rescheduling
        kept_assignments = [a for a in solution if a not in to_reschedule]

        # Generate new assignments for the selected surgeries
        new_assignments = []

        for assignment in to_reschedule:
            surgery_id = assignment.surgery_id
            surgery = next((s for s in self.surgeries if s.surgery_id == surgery_id), None)

            if not surgery:
                continue

            # Randomly select a room
            room = random.choice(self.operating_rooms)

            # Generate a random start time between 8:00 AM and 4:00 PM
            base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
            max_start_hour = 16  # 4:00 PM
            random_hours = random.randint(0, max_start_hour - 8)
            random_minutes = random.choice([0, 15, 30, 45])
            start_time = base_time + timedelta(hours=random_hours, minutes=random_minutes)

            # Calculate end time
            duration = getattr(surgery, 'duration_minutes', 60)
            end_time = start_time + timedelta(minutes=duration)

            # Create new assignment
            new_assignment = SurgeryRoomAssignment(
                surgery_id=surgery_id,
                room_id=room.room_id,
                start_time=start_time,
                end_time=end_time
            )

            new_assignments.append(new_assignment)

        # Combine kept and new assignments
        diversified_solution = kept_assignments + new_assignments

        # Check if the solution is feasible
        if self.feasibility_checker.check_solution_feasibility(diversified_solution):
            return diversified_solution
        else:
            # If not feasible, try again with fewer surgeries
            if num_to_reschedule > 1:
                num_to_reschedule = num_to_reschedule // 2
                return self._diversify_solution(solution)
            else:
                # If we can't diversify, return the original solution
                return solution
