"""
Neighborhood generation strategies for the Tabu Search optimizer.

This module provides sophisticated neighborhood generation strategies
for the Tabu Search optimizer, working with the full models.
"""

import logging
import random
import itertools
import copy
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from models import (
    Surgery,
    OperatingRoom,
    Surgeon,
    SurgeryRoomAssignment,
    SurgeryType
)
from feasibility_checker import FeasibilityChecker

logger = logging.getLogger(__name__)

class NeighborhoodStrategies:
    """
    Neighborhood generation strategies for the Tabu Search optimizer.

    This class provides sophisticated neighborhood generation strategies
    for the Tabu Search optimizer, working with the full models.
    """

    def __init__(
        self,
        db_session,
        surgeries,
        operating_rooms,
        feasibility_checker,
        sds_times_data=None,
        max_neighbors_per_strategy=10,
        strategy_weights=None
    ):
        """
        Initialize the neighborhood generation strategies.

        Args:
            db_session: Database session for querying data
            surgeries: List of Surgery objects
            operating_rooms: List of OperatingRoom objects
            feasibility_checker: Instance of FeasibilityChecker
            sds_times_data: Dictionary of sequence-dependent setup times
            max_neighbors_per_strategy: Maximum number of neighbors to generate per strategy
            strategy_weights: Dictionary of weights for each strategy
        """
        self.db_session = db_session
        self.surgeries = surgeries
        self.operating_rooms = operating_rooms
        self.feasibility_checker = feasibility_checker
        self.sds_times_data = sds_times_data if sds_times_data else {}
        self.max_neighbors_per_strategy = max_neighbors_per_strategy

        # Default strategy weights
        self.strategy_weights = {
            "move_to_different_room": 1.0,
            "swap_surgeries": 1.0,
            "shift_surgery_time": 1.0,
            "reschedule_to_specific_time": 0.8,
            "change_surgery_order": 0.8,
            "batch_similar_surgeries": 0.6,
            "optimize_surgeon_schedule": 0.7
        }

        # Override with provided weights if any
        if strategy_weights:
            self.strategy_weights.update(strategy_weights)

        # Map of surgery IDs to surgery type IDs for quick lookup
        self.surgery_id_to_type_id_map = {}
        for surgery in self.surgeries:
            if hasattr(surgery, 'surgery_type_id'):
                self.surgery_id_to_type_id_map[surgery.surgery_id] = surgery.surgery_type_id

    def initialize_solution_randomly(self):
        """
        Generate a random initial solution.

        Returns:
            List of SurgeryRoomAssignment objects
        """
        logger.info("Generating random initial solution")

        if not self.surgeries or not self.operating_rooms:
            logger.warning("Cannot generate random solution: missing surgeries or rooms data")
            return []

        # Shuffle surgeries to randomize the order
        shuffled_surgeries = random.sample(self.surgeries, len(self.surgeries))

        # Initialize empty solution
        solution = []

        # Track room schedules
        room_schedules = {room.room_id: [] for room in self.operating_rooms}

        # Assign surgeries to rooms
        for surgery in shuffled_surgeries:
            # Randomly select a room
            room = random.choice(self.operating_rooms)

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
                    last_surgery_id = room_schedules[room.room_id][-1].surgery_id
                    last_surgery = next((s for s in self.surgeries if s.surgery_id == last_surgery_id), None)
                    if last_surgery and hasattr(last_surgery, 'surgery_type_id') and hasattr(surgery, 'surgery_type_id'):
                        last_type_id = last_surgery.surgery_type_id
                        current_type_id = surgery.surgery_type_id
                        setup_time = self.sds_times_data.get((last_type_id, current_type_id), 15)

                # Start time is the end time of the last surgery plus setup time
                start_time = last_end_time + timedelta(minutes=setup_time)

            # Calculate end time
            duration = getattr(surgery, 'duration_minutes', 60)  # Default to 60 minutes if not specified
            end_time = start_time + timedelta(minutes=duration)

            # Create assignment
            assignment = SurgeryRoomAssignment(
                surgery_id=surgery.surgery_id,
                room_id=room.room_id,
                start_time=start_time,
                end_time=end_time
            )

            # Add to solution and room schedule
            solution.append(assignment)
            room_schedules[room.room_id].append(assignment)

        # Check if the solution is feasible
        if self.feasibility_checker.check_solution_feasibility(solution):
            logger.info(f"Generated feasible random solution with {len(solution)} assignments")
            return solution
        else:
            logger.warning("Generated random solution is not feasible, returning empty solution")
            return []

    def generate_neighbor_solutions(self, current_solution, tabu_list=None):
        """
        Generate neighbor solutions from the current solution.

        Args:
            current_solution: Current solution (list of SurgeryRoomAssignment objects)
            tabu_list: Optional tabu list to avoid generating tabu moves

        Returns:
            List of dictionaries with 'assignments' and 'move' keys
        """
        if not current_solution:
            logger.warning("Cannot generate neighbors: empty current solution")
            return []

        neighbors = []

        # Determine which strategies to use based on weights
        strategies = []
        for strategy_name, weight in self.strategy_weights.items():
            if random.random() < weight:
                strategies.append(strategy_name)

        # If no strategies were selected, use all of them
        if not strategies:
            strategies = list(self.strategy_weights.keys())

        # Apply selected strategies
        for strategy in strategies:
            strategy_method = getattr(self, f"_strategy_{strategy}", None)
            if strategy_method:
                strategy_neighbors = strategy_method(current_solution, tabu_list)
                neighbors.extend(strategy_neighbors)
            else:
                logger.warning(f"Strategy method not found: _strategy_{strategy}")

        # Shuffle neighbors to avoid bias
        random.shuffle(neighbors)

        return neighbors

    def _strategy_move_to_different_room(self, current_solution, tabu_list=None):
        """
        Strategy: Move a surgery to a different room.

        Args:
            current_solution: Current solution
            tabu_list: Optional tabu list

        Returns:
            List of neighbor solutions
        """
        neighbors = []

        # Sample a subset of surgeries to consider
        surgeries_to_consider = random.sample(
            current_solution,
            min(len(current_solution), self.max_neighbors_per_strategy)
        )

        for assignment in surgeries_to_consider:
            current_room_id = assignment.room_id

            # Try each other room
            for room in self.operating_rooms:
                if room.room_id == current_room_id:
                    continue

                # Create a new assignment with the different room
                new_assignment = copy.deepcopy(assignment)
                new_assignment.room_id = room.room_id

                # Check if the move is tabu
                move = ('move_room', assignment.surgery_id, current_room_id, room.room_id)
                if tabu_list and tabu_list.is_tabu(move):
                    continue

                # Create a new solution with the modified assignment
                new_solution = [a if a.surgery_id != assignment.surgery_id else new_assignment for a in current_solution]

                # Check if the new solution is feasible
                if self.feasibility_checker.check_solution_feasibility(new_solution):
                    neighbors.append({
                        'assignments': new_solution,
                        'move': move
                    })

                    # Limit the number of neighbors per strategy
                    if len(neighbors) >= self.max_neighbors_per_strategy:
                        return neighbors

        return neighbors

    def _strategy_swap_surgeries(self, current_solution, tabu_list=None):
        """
        Strategy: Swap two surgeries between rooms or time slots.

        Args:
            current_solution: Current solution
            tabu_list: Optional tabu list

        Returns:
            List of neighbor solutions
        """
        neighbors = []

        # Need at least 2 surgeries to swap
        if len(current_solution) < 2:
            return neighbors

        # Generate all possible pairs of assignments
        pairs = list(itertools.combinations(current_solution, 2))

        # Sample a subset of pairs to consider
        pairs_to_consider = random.sample(
            pairs,
            min(len(pairs), self.max_neighbors_per_strategy)
        )

        for assignment1, assignment2 in pairs_to_consider:
            # Swap rooms
            new_assignment1 = copy.deepcopy(assignment1)
            new_assignment2 = copy.deepcopy(assignment2)

            new_assignment1.room_id, new_assignment2.room_id = new_assignment2.room_id, new_assignment1.room_id

            # Check if the move is tabu
            move = ('swap_rooms', assignment1.surgery_id, assignment2.surgery_id)
            if tabu_list and tabu_list.is_tabu(move):
                continue

            # Create a new solution with the swapped assignments
            new_solution = []
            for a in current_solution:
                if a.surgery_id == assignment1.surgery_id:
                    new_solution.append(new_assignment1)
                elif a.surgery_id == assignment2.surgery_id:
                    new_solution.append(new_assignment2)
                else:
                    new_solution.append(a)

            # Check if the new solution is feasible
            if self.feasibility_checker.check_solution_feasibility(new_solution):
                neighbors.append({
                    'assignments': new_solution,
                    'move': move
                })

                # Limit the number of neighbors per strategy
                if len(neighbors) >= self.max_neighbors_per_strategy:
                    return neighbors

        return neighbors

    def _strategy_shift_surgery_time(self, current_solution, tabu_list=None):
        """
        Strategy: Shift a surgery's time earlier or later.

        Args:
            current_solution: Current solution
            tabu_list: Optional tabu list

        Returns:
            List of neighbor solutions
        """
        neighbors = []

        # Sample a subset of surgeries to consider
        surgeries_to_consider = random.sample(
            current_solution,
            min(len(current_solution), self.max_neighbors_per_strategy)
        )

        # Time shifts to try (in minutes)
        time_shifts = [-60, -30, -15, 15, 30, 60]

        for assignment in surgeries_to_consider:
            for shift in time_shifts:
                # Create a new assignment with shifted times
                new_assignment = copy.deepcopy(assignment)
                new_assignment.start_time += timedelta(minutes=shift)
                new_assignment.end_time += timedelta(minutes=shift)

                # Check if the move is tabu
                move = ('shift_time', assignment.surgery_id, shift)
                if tabu_list and tabu_list.is_tabu(move):
                    continue

                # Create a new solution with the modified assignment
                new_solution = [a if a.surgery_id != assignment.surgery_id else new_assignment for a in current_solution]

                # Check if the new solution is feasible
                if self.feasibility_checker.check_solution_feasibility(new_solution):
                    neighbors.append({
                        'assignments': new_solution,
                        'move': move
                    })

                    # Limit the number of neighbors per strategy
                    if len(neighbors) >= self.max_neighbors_per_strategy:
                        return neighbors

        return neighbors

    def _strategy_reschedule_to_specific_time(self, current_solution, tabu_list=None):
        """
        Strategy: Reschedule a surgery to a specific time slot.

        Args:
            current_solution: Current solution
            tabu_list: Optional tabu list

        Returns:
            List of neighbor solutions
        """
        neighbors = []

        # Sample a subset of surgeries to consider
        surgeries_to_consider = random.sample(
            current_solution,
            min(len(current_solution), self.max_neighbors_per_strategy)
        )

        # Generate specific time slots throughout the day
        base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        time_slots = [base_time + timedelta(minutes=30*i) for i in range(20)]  # 8:00 AM to 6:00 PM in 30-min increments

        for assignment in surgeries_to_consider:
            # Get the surgery duration
            duration_minutes = (assignment.end_time - assignment.start_time).total_seconds() / 60

            for start_time in time_slots:
                # Skip if it's the same start time
                if start_time == assignment.start_time:
                    continue

                # Create a new assignment with the new time slot
                new_assignment = copy.deepcopy(assignment)
                new_assignment.start_time = start_time
                new_assignment.end_time = start_time + timedelta(minutes=duration_minutes)

                # Check if the move is tabu
                move = ('reschedule', assignment.surgery_id, start_time.isoformat())
                if tabu_list and tabu_list.is_tabu(move):
                    continue

                # Create a new solution with the modified assignment
                new_solution = [a if a.surgery_id != assignment.surgery_id else new_assignment for a in current_solution]

                # Check if the new solution is feasible
                if self.feasibility_checker.check_solution_feasibility(new_solution):
                    neighbors.append({
                        'assignments': new_solution,
                        'move': move
                    })

                    # Limit the number of neighbors per strategy
                    if len(neighbors) >= self.max_neighbors_per_strategy:
                        return neighbors

        return neighbors

    def _strategy_change_surgery_order(self, current_solution, tabu_list=None):
        """
        Strategy: Change the order of surgeries in a room.

        Args:
            current_solution: Current solution
            tabu_list: Optional tabu list

        Returns:
            List of neighbor solutions
        """
        neighbors = []

        # Group assignments by room
        room_assignments = {}
        for assignment in current_solution:
            if assignment.room_id not in room_assignments:
                room_assignments[assignment.room_id] = []
            room_assignments[assignment.room_id].append(assignment)

        # Sort assignments in each room by start time
        for room_id, assignments in room_assignments.items():
            assignments.sort(key=lambda a: a.start_time)

        # Sample a subset of rooms to consider
        rooms_to_consider = random.sample(
            list(room_assignments.keys()),
            min(len(room_assignments), self.max_neighbors_per_strategy)
        )

        for room_id in rooms_to_consider:
            assignments = room_assignments[room_id]

            # Need at least 2 surgeries in the room to change order
            if len(assignments) < 2:
                continue

            # Try swapping adjacent surgeries
            for i in range(len(assignments) - 1):
                # Create new assignments with swapped order
                new_assignments = copy.deepcopy(assignments)

                # Swap start and end times
                duration1 = (new_assignments[i].end_time - new_assignments[i].start_time).total_seconds() / 60
                duration2 = (new_assignments[i+1].end_time - new_assignments[i+1].start_time).total_seconds() / 60

                new_start1 = new_assignments[i+1].start_time
                new_end1 = new_start1 + timedelta(minutes=duration1)

                new_start2 = new_assignments[i].start_time
                new_end2 = new_start2 + timedelta(minutes=duration2)

                new_assignments[i].start_time = new_start1
                new_assignments[i].end_time = new_end1

                new_assignments[i+1].start_time = new_start2
                new_assignments[i+1].end_time = new_end2

                # Check if the move is tabu
                move = ('change_order', assignments[i].surgery_id, assignments[i+1].surgery_id)
                if tabu_list and tabu_list.is_tabu(move):
                    continue

                # Create a new solution with the modified assignments
                new_solution = []
                for a in current_solution:
                    if a.room_id == room_id:
                        # Find the corresponding new assignment
                        for new_a in new_assignments:
                            if a.surgery_id == new_a.surgery_id:
                                new_solution.append(new_a)
                                break
                    else:
                        new_solution.append(a)

                # Check if the new solution is feasible
                if self.feasibility_checker.check_solution_feasibility(new_solution):
                    neighbors.append({
                        'assignments': new_solution,
                        'move': move
                    })

                    # Limit the number of neighbors per strategy
                    if len(neighbors) >= self.max_neighbors_per_strategy:
                        return neighbors

        return neighbors

    def _strategy_batch_similar_surgeries(self, current_solution, tabu_list=None):
        """
        Strategy: Batch similar surgeries together to minimize setup times.

        Args:
            current_solution: Current solution
            tabu_list: Optional tabu list

        Returns:
            List of neighbor solutions
        """
        neighbors = []

        # Need SDST data for this strategy
        if not self.sds_times_data:
            return neighbors

        # Group assignments by room
        room_assignments = {}
        for assignment in current_solution:
            if assignment.room_id not in room_assignments:
                room_assignments[assignment.room_id] = []
            room_assignments[assignment.room_id].append(assignment)

        # Sort assignments in each room by start time
        for room_id, assignments in room_assignments.items():
            assignments.sort(key=lambda a: a.start_time)

        # Sample a subset of rooms to consider
        rooms_to_consider = random.sample(
            list(room_assignments.keys()),
            min(len(room_assignments), self.max_neighbors_per_strategy)
        )

        for room_id in rooms_to_consider:
            assignments = room_assignments[room_id]

            # Need at least 2 surgeries in the room to batch
            if len(assignments) < 2:
                continue

            # Try different permutations of surgeries to minimize setup times
            original_order = [a.surgery_id for a in assignments]

            # Generate a few random permutations
            for _ in range(min(5, self.max_neighbors_per_strategy)):
                # Create a new permutation
                new_order = original_order.copy()
                random.shuffle(new_order)

                # Skip if it's the same order
                if new_order == original_order:
                    continue

                # Check if the move is tabu
                move = ('batch', room_id, tuple(new_order))
                if tabu_list and tabu_list.is_tabu(move):
                    continue

                # Create new assignments with the new order
                new_assignments = []
                current_time = assignments[0].start_time

                for surgery_id in new_order:
                    # Find the original assignment for this surgery
                    original_assignment = next(a for a in assignments if a.surgery_id == surgery_id)

                    # Create a new assignment with the new time
                    new_assignment = copy.deepcopy(original_assignment)
                    duration = (original_assignment.end_time - original_assignment.start_time).total_seconds() / 60

                    # Add setup time if not the first surgery
                    if new_assignments:
                        last_surgery_id = new_assignments[-1].surgery_id
                        last_type_id = self.surgery_id_to_type_id_map.get(last_surgery_id)
                        current_type_id = self.surgery_id_to_type_id_map.get(surgery_id)

                        if last_type_id is not None and current_type_id is not None:
                            setup_time = self.sds_times_data.get((last_type_id, current_type_id), 15)
                            current_time += timedelta(minutes=setup_time)

                    new_assignment.start_time = current_time
                    new_assignment.end_time = current_time + timedelta(minutes=duration)
                    new_assignments.append(new_assignment)

                    # Update current time for next surgery
                    current_time = new_assignment.end_time

                # Create a new solution with the modified assignments
                new_solution = []
                for a in current_solution:
                    if a.room_id == room_id:
                        # Find the corresponding new assignment
                        for new_a in new_assignments:
                            if a.surgery_id == new_a.surgery_id:
                                new_solution.append(new_a)
                                break
                    else:
                        new_solution.append(a)

                # Check if the new solution is feasible
                if self.feasibility_checker.check_solution_feasibility(new_solution):
                    neighbors.append({
                        'assignments': new_solution,
                        'move': move
                    })

                    # Limit the number of neighbors per strategy
                    if len(neighbors) >= self.max_neighbors_per_strategy:
                        return neighbors

        return neighbors

    def _strategy_optimize_surgeon_schedule(self, current_solution, tabu_list=None):
        """
        Strategy: Optimize a surgeon's schedule to minimize idle time.

        Args:
            current_solution: Current solution
            tabu_list: Optional tabu list

        Returns:
            List of neighbor solutions
        """
        neighbors = []

        # Group assignments by surgeon
        surgeon_assignments = {}
        for assignment in current_solution:
            # Get the surgery
            surgery_id = assignment.surgery_id
            surgery = next((s for s in self.surgeries if s.surgery_id == surgery_id), None)

            if not surgery or not hasattr(surgery, 'surgeon_id'):
                continue

            surgeon_id = surgery.surgeon_id
            if surgeon_id not in surgeon_assignments:
                surgeon_assignments[surgeon_id] = []
            surgeon_assignments[surgeon_id].append(assignment)

        # Sort assignments for each surgeon by start time
        for surgeon_id, assignments in surgeon_assignments.items():
            assignments.sort(key=lambda a: a.start_time)

        # Sample a subset of surgeons to consider
        surgeons_to_consider = random.sample(
            list(surgeon_assignments.keys()),
            min(len(surgeon_assignments), self.max_neighbors_per_strategy)
        )

        for surgeon_id in surgeons_to_consider:
            assignments = surgeon_assignments[surgeon_id]

            # Need at least 2 surgeries for the surgeon to optimize
            if len(assignments) < 2:
                continue

            # Check for idle time between surgeries
            for i in range(len(assignments) - 1):
                idle_time = (assignments[i+1].start_time - assignments[i].end_time).total_seconds() / 60

                # If there's significant idle time, try to move the next surgery earlier
                if idle_time > 30:
                    # Create a new assignment with an earlier start time
                    new_assignment = copy.deepcopy(assignments[i+1])
                    new_start = assignments[i].end_time + timedelta(minutes=15)  # 15-minute buffer
                    duration = (new_assignment.end_time - new_assignment.start_time).total_seconds() / 60
                    new_assignment.start_time = new_start
                    new_assignment.end_time = new_start + timedelta(minutes=duration)

                    # Check if the move is tabu
                    move = ('optimize_surgeon', surgeon_id, assignments[i+1].surgery_id)
                    if tabu_list and tabu_list.is_tabu(move):
                        continue

                    # Create a new solution with the modified assignment
                    new_solution = [a if a.surgery_id != new_assignment.surgery_id else new_assignment for a in current_solution]

                    # Check if the new solution is feasible
                    if self.feasibility_checker.check_solution_feasibility(new_solution):
                        neighbors.append({
                            'assignments': new_solution,
                            'move': move
                        })

                        # Limit the number of neighbors per strategy
                        if len(neighbors) >= self.max_neighbors_per_strategy:
                            return neighbors

        return neighbors
