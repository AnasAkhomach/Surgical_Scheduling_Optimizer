"""
Solution evaluator for surgery scheduling.

This module provides a comprehensive solution evaluator that works with the full models
and evaluates schedules based on multiple criteria.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union

from models import (
    Surgery,
    OperatingRoom,
    Surgeon,
    SurgeryRoomAssignment,
    SurgeryType,
    SurgeonPreference
)

logger = logging.getLogger(__name__)

class SolutionEvaluator:
    """
    Solution evaluator for surgery scheduling.

    This class evaluates surgery schedules based on multiple criteria, including:
    - Operating room utilization
    - Sequence-dependent setup times
    - Surgeon preference satisfaction
    - Workload balance
    - Patient wait time
    - Emergency surgery priority
    - Operational costs
    """

    def __init__(self, db_session, weights=None, sds_times_data=None):
        """
        Initialize the solution evaluator.

        Args:
            db_session: Database session for querying data
            weights: Dictionary of weights for each evaluation criterion
            sds_times_data: Dictionary of sequence-dependent setup times
        """
        self.db_session = db_session
        self.weights = weights if weights else self._default_weights()
        self.sds_times_data = sds_times_data if sds_times_data else {}

        # Cache for database objects
        self.surgeries_cache = {}
        self.surgeons_cache = {}
        self.rooms_cache = {}
        self.surgery_types_cache = {}
        self.surgeon_preferences_cache = {}

        # Load data into cache if db_session is provided
        if self.db_session:
            self._load_cache_data()

        logger.info(f"SolutionEvaluator initialized with weights: {self.weights}")

    def _load_cache_data(self):
        """Load data from database into cache for faster access."""
        try:
            # Load surgeries
            surgeries = self.db_session.query(Surgery).all()
            self.surgeries_cache = {surgery.surgery_id: surgery for surgery in surgeries}

            # Load surgeons
            surgeons = self.db_session.query(Surgeon).all()
            self.surgeons_cache = {surgeon.surgeon_id: surgeon for surgeon in surgeons}

            # Load operating rooms
            rooms = self.db_session.query(OperatingRoom).all()
            self.rooms_cache = {room.room_id: room for room in rooms}

            # Load surgery types
            surgery_types = self.db_session.query(SurgeryType).all()
            self.surgery_types_cache = {st.type_id: st for st in surgery_types}

            # Load surgeon preferences
            surgeon_prefs = self.db_session.query(SurgeonPreference).all()
            self.surgeon_preferences_cache = {}
            for pref in surgeon_prefs:
                if pref.surgeon_id not in self.surgeon_preferences_cache:
                    self.surgeon_preferences_cache[pref.surgeon_id] = []
                self.surgeon_preferences_cache[pref.surgeon_id].append(pref)

            logger.info("Cache data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading cache data: {e}")

    def _default_weights(self):
        """
        Get default weights for evaluation criteria.

        Returns:
            Dictionary of weights
        """
        return {
            "or_utilization": 0.20,  # Maximize OR utilization
            "sds_time_penalty": -0.15,  # Minimize sequence-dependent setup time
            "surgeon_preference_satisfaction": 0.15,  # Maximize surgeon preference satisfaction
            "workload_balance": 0.15,  # Maximize workload balance
            "patient_wait_time": -0.10,  # Minimize patient wait time
            "emergency_surgery_priority": 0.15,  # Prioritize emergency surgeries
            "operational_cost": -0.10,  # Minimize operational costs
            "staff_overtime": -0.10,  # Minimize staff overtime
            "feasibility_penalty": -100.0  # Large penalty for infeasible solutions
        }

    def evaluate_solution(self, solution, schedule_start_time=None, schedule_end_time=None):
        """
        Evaluate a solution based on multiple criteria.

        Args:
            solution: List of SurgeryRoomAssignment objects
            schedule_start_time: Optional start time of the schedule window
            schedule_end_time: Optional end time of the schedule window

        Returns:
            Total score for the solution
        """
        if not solution:
            logger.warning("Empty solution provided for evaluation")
            return 0

        # If schedule window not provided, determine from solution
        if not schedule_start_time or not schedule_end_time:
            start_times = [a.start_time for a in solution if a.start_time]
            end_times = [a.end_time for a in solution if a.end_time]

            if not start_times or not end_times:
                logger.warning("Solution has no valid start/end times")
                return 0

            schedule_start_time = min(start_times)
            schedule_end_time = max(end_times)

        # Calculate scores for each criterion
        scores = {}

        # 1. Operating room utilization
        scores["or_utilization"] = self._calculate_or_utilization(solution, schedule_start_time, schedule_end_time)

        # 2. Sequence-dependent setup time
        scores["sds_time_penalty"] = self._calculate_sds_time(solution)

        # 3. Surgeon preference satisfaction
        scores["surgeon_preference_satisfaction"] = self._calculate_surgeon_preference_satisfaction(solution)

        # 4. Workload balance
        scores["workload_balance"] = self._calculate_workload_balance(solution)

        # 5. Patient wait time
        scores["patient_wait_time"] = self._calculate_patient_wait_time(solution)

        # 6. Emergency surgery priority
        scores["emergency_surgery_priority"] = self._calculate_emergency_priority(solution)

        # 7. Operational cost
        scores["operational_cost"] = self._calculate_operational_cost(solution)

        # 8. Staff overtime
        scores["staff_overtime"] = self._calculate_staff_overtime(solution, schedule_start_time, schedule_end_time)

        # Calculate total score
        total_score = 0
        for criterion, score in scores.items():
            weighted_score = self.weights.get(criterion, 0) * score
            total_score += weighted_score
            logger.debug(f"{criterion}: {score:.4f} * {self.weights.get(criterion, 0):.2f} = {weighted_score:.4f}")

        logger.info(f"Total evaluation score: {total_score:.4f}")
        return total_score

    def _calculate_or_utilization(self, solution, schedule_start_time, schedule_end_time):
        """
        Calculate operating room utilization.

        Args:
            solution: List of SurgeryRoomAssignment objects
            schedule_start_time: Start time of the schedule window
            schedule_end_time: End time of the schedule window

        Returns:
            OR utilization score (0-1, higher is better)
        """
        # Get all operating rooms
        if self.db_session:
            rooms = list(self.rooms_cache.values())
            if not rooms:
                rooms = self.db_session.query(OperatingRoom).all()
                self.rooms_cache = {room.room_id: room for room in rooms}
        else:
            # Extract unique room IDs from solution
            room_ids = set(a.room_id for a in solution)
            rooms = [{"room_id": room_id} for room_id in room_ids]

        # Calculate total available time across all rooms
        schedule_duration = (schedule_end_time - schedule_start_time).total_seconds() / 60  # in minutes
        total_available_time = schedule_duration * len(rooms)

        # Calculate total used time
        total_used_time = 0
        for assignment in solution:
            if assignment.start_time and assignment.end_time:
                duration = (assignment.end_time - assignment.start_time).total_seconds() / 60
                total_used_time += duration

        # Calculate utilization
        if total_available_time > 0:
            utilization = total_used_time / total_available_time
            logger.debug(f"OR utilization: {utilization:.2%} ({total_used_time:.0f}/{total_available_time:.0f} minutes)")
            return utilization
        else:
            logger.warning("Total available time is zero, cannot calculate OR utilization")
            return 0

    def _calculate_sds_time(self, solution):
        """
        Calculate sequence-dependent setup time penalty.

        Args:
            solution: List of SurgeryRoomAssignment objects

        Returns:
            SDST penalty score (normalized, lower is better)
        """
        if not self.sds_times_data:
            logger.debug("No SDST data available, skipping SDST calculation")
            return 0

        # Group assignments by room
        room_assignments = {}
        for assignment in solution:
            if assignment.room_id not in room_assignments:
                room_assignments[assignment.room_id] = []
            room_assignments[assignment.room_id].append(assignment)

        # Sort assignments in each room by start time
        for room_id, assignments in room_assignments.items():
            assignments.sort(key=lambda a: a.start_time)

        # Calculate total SDST
        total_sds_time = 0
        for room_id, assignments in room_assignments.items():
            for i in range(1, len(assignments)):
                prev_assignment = assignments[i-1]
                curr_assignment = assignments[i]

                # Get surgery type IDs
                prev_surgery_id = prev_assignment.surgery_id
                curr_surgery_id = curr_assignment.surgery_id

                prev_surgery = None
                curr_surgery = None

                # Try to get surgeries from cache or database
                if self.db_session:
                    prev_surgery = self.surgeries_cache.get(prev_surgery_id)
                    if not prev_surgery:
                        prev_surgery = self.db_session.query(Surgery).filter_by(surgery_id=prev_surgery_id).first()
                        if prev_surgery:
                            self.surgeries_cache[prev_surgery_id] = prev_surgery

                    curr_surgery = self.surgeries_cache.get(curr_surgery_id)
                    if not curr_surgery:
                        curr_surgery = self.db_session.query(Surgery).filter_by(surgery_id=curr_surgery_id).first()
                        if curr_surgery:
                            self.surgeries_cache[curr_surgery_id] = curr_surgery

                # Skip if we can't get surgery type IDs
                if not prev_surgery or not curr_surgery:
                    continue

                prev_type_id = getattr(prev_surgery, 'surgery_type_id', None)
                curr_type_id = getattr(curr_surgery, 'surgery_type_id', None)

                if prev_type_id is not None and curr_type_id is not None:
                    # Get SDST from data
                    sds_time = self.sds_times_data.get((prev_type_id, curr_type_id), 15)  # Default to 15 minutes
                    total_sds_time += sds_time

        # Normalize SDST penalty (assuming max 30 minutes per transition, max 10 transitions)
        max_expected_sds_time = 30 * 10
        normalized_penalty = min(1.0, total_sds_time / max_expected_sds_time)

        logger.debug(f"Total SDST: {total_sds_time} minutes, normalized penalty: {normalized_penalty:.4f}")
        return normalized_penalty

    def _calculate_surgeon_preference_satisfaction(self, solution):
        """
        Calculate surgeon preference satisfaction.

        Args:
            solution: List of SurgeryRoomAssignment objects

        Returns:
            Preference satisfaction score (0-1, higher is better)
        """
        if not self.db_session:
            logger.debug("No database session available, skipping surgeon preference calculation")
            return 0.5  # Neutral score

        total_preferences = 0
        satisfied_preferences = 0

        for assignment in solution:
            # Get the surgery
            surgery_id = assignment.surgery_id
            surgery = self.surgeries_cache.get(surgery_id)
            if not surgery:
                surgery = self.db_session.query(Surgery).filter_by(surgery_id=surgery_id).first()
                if surgery:
                    self.surgeries_cache[surgery_id] = surgery

            if not surgery:
                continue

            # Get the surgeon
            surgeon_id = getattr(surgery, 'surgeon_id', None)
            if not surgeon_id:
                continue

            # Get surgeon preferences
            preferences = self.surgeon_preferences_cache.get(surgeon_id, [])
            if not preferences:
                preferences = self.db_session.query(SurgeonPreference).filter_by(surgeon_id=surgeon_id).all()
                self.surgeon_preferences_cache[surgeon_id] = preferences

            for pref in preferences:
                total_preferences += 1

                # Check if preference is satisfied
                if pref.preference_type == 'room_id' and str(assignment.room_id) == pref.preference_value:
                    satisfied_preferences += 1
                elif pref.preference_type == 'day_of_week' and assignment.start_time.strftime('%A') == pref.preference_value:
                    satisfied_preferences += 1
                elif pref.preference_type == 'time_of_day':
                    hour = assignment.start_time.hour
                    if (pref.preference_value == 'morning' and 8 <= hour < 12) or \
                       (pref.preference_value == 'afternoon' and 12 <= hour < 17) or \
                       (pref.preference_value == 'evening' and 17 <= hour < 20):
                        satisfied_preferences += 1

        # Calculate satisfaction rate
        if total_preferences > 0:
            satisfaction_rate = satisfied_preferences / total_preferences
            logger.debug(f"Surgeon preference satisfaction: {satisfaction_rate:.2%} ({satisfied_preferences}/{total_preferences})")
            return satisfaction_rate
        else:
            logger.debug("No surgeon preferences found")
            return 1.0  # If no preferences, consider them all satisfied

    def _calculate_workload_balance(self, solution):
        """
        Calculate workload balance among surgeons.

        Args:
            solution: List of SurgeryRoomAssignment objects

        Returns:
            Workload balance score (0-1, higher is better)
        """
        # Group surgeries by surgeon
        surgeon_workloads = {}

        for assignment in solution:
            # Get the surgery
            surgery_id = assignment.surgery_id
            surgery = None

            if self.db_session:
                surgery = self.surgeries_cache.get(surgery_id)
                if not surgery:
                    surgery = self.db_session.query(Surgery).filter_by(surgery_id=surgery_id).first()
                    if surgery:
                        self.surgeries_cache[surgery_id] = surgery

            if not surgery:
                continue

            # Get the surgeon
            surgeon_id = getattr(surgery, 'surgeon_id', None)
            if not surgeon_id:
                continue

            # Calculate duration
            if assignment.start_time and assignment.end_time:
                duration = (assignment.end_time - assignment.start_time).total_seconds() / 60

                if surgeon_id not in surgeon_workloads:
                    surgeon_workloads[surgeon_id] = 0
                surgeon_workloads[surgeon_id] += duration

        # Calculate workload balance
        if len(surgeon_workloads) <= 1:
            logger.debug("Only one or zero surgeons in the solution, perfect balance")
            return 1.0  # Perfect balance with only one surgeon

        # Calculate standard deviation of workloads
        workloads = list(surgeon_workloads.values())
        mean_workload = sum(workloads) / len(workloads)
        variance = sum((w - mean_workload) ** 2 for w in workloads) / len(workloads)
        std_dev = variance ** 0.5

        # Normalize to a 0-1 score (higher is better)
        # Assuming max reasonable std_dev is mean_workload
        if mean_workload > 0:
            normalized_balance = 1.0 - min(1.0, std_dev / mean_workload)
        else:
            normalized_balance = 1.0

        logger.debug(f"Workload balance: {normalized_balance:.4f} (std_dev: {std_dev:.0f}, mean: {mean_workload:.0f})")
        return normalized_balance

    def _calculate_patient_wait_time(self, solution):
        """
        Calculate patient wait time penalty.

        Args:
            solution: List of SurgeryRoomAssignment objects

        Returns:
            Wait time penalty score (0-1, lower is better)
        """
        # For a complete implementation, we would need request dates for surgeries
        # For now, use a simplified approach based on urgency levels

        if not self.db_session:
            logger.debug("No database session available, skipping patient wait time calculation")
            return 0.5  # Neutral score

        total_wait_score = 0
        count = 0

        for assignment in solution:
            # Get the surgery
            surgery_id = assignment.surgery_id
            surgery = self.surgeries_cache.get(surgery_id)
            if not surgery:
                surgery = self.db_session.query(Surgery).filter_by(surgery_id=surgery_id).first()
                if surgery:
                    self.surgeries_cache[surgery_id] = surgery

            if not surgery:
                continue

            # Get urgency level
            urgency_level = getattr(surgery, 'urgency_level', 'Medium')

            # Calculate wait time score based on urgency and time of day
            # Higher urgency should be scheduled earlier in the day
            hour = assignment.start_time.hour

            if urgency_level == 'High':
                # High urgency surgeries should be early in the day
                wait_score = hour / 24.0  # 0 for midnight, 0.5 for noon
            elif urgency_level == 'Medium':
                # Medium urgency is neutral
                wait_score = 0.5
            else:  # Low urgency
                # Low urgency surgeries can be later in the day
                wait_score = 1.0 - (hour / 24.0)  # Higher score for later hours

            total_wait_score += wait_score
            count += 1

        # Calculate average wait score
        if count > 0:
            avg_wait_score = total_wait_score / count
            logger.debug(f"Patient wait time score: {avg_wait_score:.4f}")
            return avg_wait_score
        else:
            logger.debug("No valid surgeries for wait time calculation")
            return 0.5  # Neutral score

    def _calculate_emergency_priority(self, solution):
        """
        Calculate emergency surgery priority score.

        Args:
            solution: List of SurgeryRoomAssignment objects

        Returns:
            Emergency priority score (0-1, higher is better)
        """
        if not self.db_session:
            logger.debug("No database session available, skipping emergency priority calculation")
            return 0.5  # Neutral score

        # Map urgency levels to priority scores
        urgency_scores = {
            'High': 1.0,
            'Medium': 0.5,
            'Low': 0.0
        }

        total_score = 0
        count = 0

        for assignment in solution:
            # Get the surgery
            surgery_id = assignment.surgery_id
            surgery = self.surgeries_cache.get(surgery_id)
            if not surgery:
                surgery = self.db_session.query(Surgery).filter_by(surgery_id=surgery_id).first()
                if surgery:
                    self.surgeries_cache[surgery_id] = surgery

            if not surgery:
                continue

            # Get urgency level
            urgency_level = getattr(surgery, 'urgency_level', 'Medium')

            # Calculate priority score
            # Higher urgency surgeries should be scheduled earlier in the day
            hour = assignment.start_time.hour
            base_score = urgency_scores.get(urgency_level, 0.5)

            # Adjust score based on time of day (earlier is better for high urgency)
            if urgency_level == 'High':
                time_factor = max(0, 1.0 - (hour / 12.0))  # 1.0 at midnight, 0.0 at noon or later
                priority_score = base_score * (0.5 + 0.5 * time_factor)  # Weighted average
            else:
                priority_score = base_score

            total_score += priority_score
            count += 1

        # Calculate average priority score
        if count > 0:
            avg_priority_score = total_score / count
            logger.debug(f"Emergency priority score: {avg_priority_score:.4f}")
            return avg_priority_score
        else:
            logger.debug("No valid surgeries for emergency priority calculation")
            return 0.5  # Neutral score

    def _calculate_operational_cost(self, solution):
        """
        Calculate operational cost penalty.

        Args:
            solution: List of SurgeryRoomAssignment objects

        Returns:
            Operational cost penalty score (0-1, lower is better)
        """
        # For a complete implementation, we would need cost data for rooms, equipment, etc.
        # For now, use a simplified approach based on room utilization

        # Group assignments by room
        room_utilization = {}

        for assignment in solution:
            room_id = assignment.room_id

            if room_id not in room_utilization:
                room_utilization[room_id] = 0

            if assignment.start_time and assignment.end_time:
                duration = (assignment.end_time - assignment.start_time).total_seconds() / 60
                room_utilization[room_id] += duration

        # Calculate cost based on utilization (more balanced utilization is better)
        if not room_utilization:
            logger.debug("No room utilization data available")
            return 0.5  # Neutral score

        # Calculate standard deviation of utilization
        utilizations = list(room_utilization.values())
        mean_utilization = sum(utilizations) / len(utilizations)

        if mean_utilization == 0:
            logger.debug("Zero mean utilization")
            return 0.5  # Neutral score

        variance = sum((u - mean_utilization) ** 2 for u in utilizations) / len(utilizations)
        std_dev = variance ** 0.5

        # Normalize to a 0-1 score (lower is better for cost)
        normalized_cost = min(1.0, std_dev / mean_utilization)

        logger.debug(f"Operational cost score: {normalized_cost:.4f}")
        return normalized_cost

    def _calculate_staff_overtime(self, solution, schedule_start_time, schedule_end_time):
        """
        Calculate staff overtime penalty.

        Args:
            solution: List of SurgeryRoomAssignment objects
            schedule_start_time: Start time of the schedule window
            schedule_end_time: End time of the schedule window

        Returns:
            Overtime penalty score (0-1, lower is better)
        """
        # Define normal working hours (e.g., 8:00 AM to 5:00 PM)
        normal_start_hour = 8
        normal_end_hour = 17

        total_overtime_minutes = 0

        for assignment in solution:
            if not assignment.start_time or not assignment.end_time:
                continue

            # Check if assignment extends beyond normal hours
            day_start = assignment.start_time.replace(hour=normal_start_hour, minute=0, second=0, microsecond=0)
            day_end = assignment.start_time.replace(hour=normal_end_hour, minute=0, second=0, microsecond=0)

            # Calculate overtime before normal hours
            if assignment.start_time < day_start:
                early_overtime = (day_start - assignment.start_time).total_seconds() / 60
                total_overtime_minutes += early_overtime

            # Calculate overtime after normal hours
            if assignment.end_time > day_end:
                late_overtime = (assignment.end_time - day_end).total_seconds() / 60
                total_overtime_minutes += late_overtime

        # Normalize overtime penalty (assuming max 8 hours of overtime)
        max_expected_overtime = 8 * 60  # 8 hours in minutes
        normalized_penalty = min(1.0, total_overtime_minutes / max_expected_overtime)

        logger.debug(f"Staff overtime: {total_overtime_minutes:.0f} minutes, normalized penalty: {normalized_penalty:.4f}")
        return normalized_penalty
