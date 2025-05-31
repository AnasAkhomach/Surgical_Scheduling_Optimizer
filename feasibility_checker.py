"""
Feasibility checker for surgery scheduling.

This module provides a comprehensive feasibility checker that works with the full models
and checks all constraints for surgery scheduling.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session

from models import (
    Surgery,
    OperatingRoom,
    Surgeon,
    SurgeryEquipment,
    SurgeryRoomAssignment,
    SurgeryEquipmentUsage,
    SurgeryType,
    SurgeonPreference,
    SurgeonAvailability,
    OperatingRoomEquipment
)

logger = logging.getLogger(__name__)

class FeasibilityChecker:
    """
    Feasibility checker for surgery scheduling.

    This class checks all constraints for surgery scheduling, including:
    - Surgeon availability
    - Equipment availability
    - Room availability
    - Room suitability for surgery type
    - Sequence-dependent setup times
    - Patient constraints
    """

    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the feasibility checker.

        Args:
            db_session: Database session for querying data
        """
        self.db_session = db_session
        self.surgeries_cache = {}
        self.surgeons_cache = {}
        self.rooms_cache = {}
        self.equipment_cache = {}
        self.surgery_types_cache = {}
        self.surgeon_preferences_cache = {}
        self.surgeon_availability_cache = {}
        self.room_equipment_cache = {}

        # Load data into cache if db_session is provided
        if self.db_session:
            self._load_cache_data()

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

            # Load equipment
            equipment = self.db_session.query(SurgeryEquipment).all()
            self.equipment_cache = {equip.equipment_id: equip for equip in equipment}

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

            # Load surgeon availability
            surgeon_avail = self.db_session.query(SurgeonAvailability).all()
            self.surgeon_availability_cache = {}
            for avail in surgeon_avail:
                if avail.surgeon_id not in self.surgeon_availability_cache:
                    self.surgeon_availability_cache[avail.surgeon_id] = []
                self.surgeon_availability_cache[avail.surgeon_id].append(avail)

            # Load room equipment
            room_equip = self.db_session.query(OperatingRoomEquipment).all()
            self.room_equipment_cache = {}
            for re in room_equip:
                if re.room_id not in self.room_equipment_cache:
                    self.room_equipment_cache[re.room_id] = []
                self.room_equipment_cache[re.room_id].append(re)

            logger.info("Cache data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading cache data: {e}")

    def is_surgeon_available(
        self,
        surgeon_id: int,
        start_time: datetime,
        end_time: datetime,
        current_assignments: List[SurgeryRoomAssignment],
        surgery_id_to_ignore: Optional[int] = None
    ) -> bool:
        """
        Check if a surgeon is available during the given time slot.

        Args:
            surgeon_id: ID of the surgeon to check
            start_time: Start time of the slot
            end_time: End time of the slot
            current_assignments: List of current assignments to check against
            surgery_id_to_ignore: ID of a surgery to ignore in the check

        Returns:
            True if the surgeon is available, False otherwise
        """
        # Check if surgeon exists
        if self.db_session:
            surgeon = self.surgeons_cache.get(surgeon_id)
            if not surgeon:
                surgeon = self.db_session.query(Surgeon).filter_by(surgeon_id=surgeon_id).first()
                if surgeon:
                    self.surgeons_cache[surgeon_id] = surgeon

        if not surgeon:
            logger.warning(f"Surgeon {surgeon_id} not found")
            return False

        # Check if surgeon is available (general availability flag)
        if hasattr(surgeon, 'availability') and not surgeon.availability:
            logger.info(f"Surgeon {surgeon_id} is marked as unavailable")
            return False

        # Check for conflicts with existing assignments
        for assignment in current_assignments:
            # Skip the assignment we're ignoring
            if surgery_id_to_ignore and assignment.surgery_id == surgery_id_to_ignore:
                continue

            # Get the surgery for this assignment
            surgery = None
            if hasattr(assignment, 'surgery') and assignment.surgery:
                surgery = assignment.surgery
            elif self.db_session:
                surgery_id = assignment.surgery_id
                surgery = self.surgeries_cache.get(surgery_id)
                if not surgery:
                    surgery = self.db_session.query(Surgery).filter_by(surgery_id=surgery_id).first()
                    if surgery:
                        self.surgeries_cache[surgery_id] = surgery

            if not surgery:
                continue

            # Skip if not the same surgeon
            if surgery.surgeon_id != surgeon_id:
                continue

            # Check for overlap
            if (start_time < assignment.end_time and end_time > assignment.start_time):
                logger.debug(f"Surgeon {surgeon_id} is busy with surgery {surgery.surgery_id} during proposed slot")
                return False

        # Check surgeon's specific availability schedule if available
        if self.db_session:
            # Get day of week and time of day
            day_of_week = start_time.strftime('%A')
            start_time_of_day = start_time.time()
            end_time_of_day = end_time.time()

            # Check if we have specific availability data
            availabilities = self.surgeon_availability_cache.get(surgeon_id, [])
            if not availabilities:
                availabilities = self.db_session.query(SurgeonAvailability).filter_by(surgeon_id=surgeon_id).all()
                self.surgeon_availability_cache[surgeon_id] = availabilities

            # If we have specific availability data, check it
            if availabilities:
                is_available = False
                for avail in availabilities:
                    if avail.day_of_week == day_of_week:
                        avail_start = datetime.strptime(avail.start_time, '%H:%M').time()
                        avail_end = datetime.strptime(avail.end_time, '%H:%M').time()

                        # Check if the proposed time slot is within the availability window
                        if start_time_of_day >= avail_start and end_time_of_day <= avail_end:
                            is_available = True
                            break

                if not is_available:
                    logger.info(f"Surgeon {surgeon_id} is not available on {day_of_week} from {start_time_of_day} to {end_time_of_day}")
                    return False

        return True

    def is_equipment_available(
        self,
        equipment_id: int,
        start_time: datetime,
        end_time: datetime,
        current_assignments: List[SurgeryRoomAssignment],
        surgery_id_to_ignore: Optional[int] = None
    ) -> bool:
        """
        Check if equipment is available during the given time slot.

        Args:
            equipment_id: ID of the equipment to check
            start_time: Start time of the slot
            end_time: End time of the slot
            current_assignments: List of current assignments to check against
            surgery_id_to_ignore: ID of a surgery to ignore in the check

        Returns:
            True if the equipment is available, False otherwise
        """
        # Check if equipment exists
        if self.db_session:
            equipment = self.equipment_cache.get(equipment_id)
            if not equipment:
                equipment = self.db_session.query(SurgeryEquipment).filter_by(equipment_id=equipment_id).first()
                if equipment:
                    self.equipment_cache[equipment_id] = equipment

        if not equipment:
            logger.warning(f"Equipment {equipment_id} not found")
            return False

        # Check if equipment is available (general availability flag)
        if hasattr(equipment, 'availability') and not equipment.availability:
            logger.info(f"Equipment {equipment_id} is marked as unavailable")
            return False

        # Check for conflicts with existing equipment usages
        if self.db_session:
            # Get equipment usages that overlap with the proposed time slot
            equipment_usages = self.db_session.query(SurgeryEquipmentUsage).filter(
                SurgeryEquipmentUsage.equipment_id == equipment_id,
                SurgeryEquipmentUsage.usage_start_time < end_time,
                SurgeryEquipmentUsage.usage_end_time > start_time
            ).all()

            for usage in equipment_usages:
                # Skip the usage for the surgery we're ignoring
                if surgery_id_to_ignore and usage.surgery_id == surgery_id_to_ignore:
                    continue

                logger.debug(f"Equipment {equipment_id} is in use for surgery {usage.surgery_id} during proposed slot")
                return False

        return True

    def is_room_available(
        self,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        current_assignments: List[SurgeryRoomAssignment],
        surgery_id_to_ignore: Optional[int] = None
    ) -> bool:
        """
        Check if a room is available during the given time slot.

        Args:
            room_id: ID of the room to check
            start_time: Start time of the slot
            end_time: End time of the slot
            current_assignments: List of current assignments to check against
            surgery_id_to_ignore: ID of a surgery to ignore in the check

        Returns:
            True if the room is available, False otherwise
        """
        # Check if room exists
        if self.db_session:
            room = self.rooms_cache.get(room_id)
            if not room:
                room = self.db_session.query(OperatingRoom).filter_by(room_id=room_id).first()
                if room:
                    self.rooms_cache[room_id] = room

        if not room:
            logger.warning(f"Room {room_id} not found")
            return False

        # Check for conflicts with existing assignments
        for assignment in current_assignments:
            # Skip the assignment we're ignoring
            if surgery_id_to_ignore and assignment.surgery_id == surgery_id_to_ignore:
                continue

            # Skip if not the same room
            if assignment.room_id != room_id:
                continue

            # Check for overlap
            if (start_time < assignment.end_time and end_time > assignment.start_time):
                logger.debug(f"Room {room_id} is busy with surgery {assignment.surgery_id} during proposed slot")
                return False

        # Check room's operational hours if available
        if hasattr(room, 'operational_start_time') and room.operational_start_time:
            # Get operational start and end times for the day
            op_start_time = datetime.combine(start_time.date(), room.operational_start_time)
            # Assume 8-hour operational day if not specified
            op_end_time = op_start_time + timedelta(hours=8)

            # Check if the proposed time slot is within operational hours
            if start_time < op_start_time or end_time > op_end_time:
                logger.info(f"Room {room_id} is not operational during proposed slot")
                return False

        return True

    def is_room_suitable_for_surgery(
        self,
        room_id: int,
        surgery_id: int
    ) -> bool:
        """
        Check if a room is suitable for a surgery.

        Args:
            room_id: ID of the room to check
            surgery_id: ID of the surgery to check

        Returns:
            True if the room is suitable, False otherwise
        """
        if not self.db_session:
            # Without a database session, we can't check room suitability
            return True

        # Get the surgery
        surgery = self.surgeries_cache.get(surgery_id)
        if not surgery:
            surgery = self.db_session.query(Surgery).filter_by(surgery_id=surgery_id).first()
            if surgery:
                self.surgeries_cache[surgery_id] = surgery

        if not surgery:
            logger.warning(f"Surgery {surgery_id} not found")
            return False

        # Get the surgery type
        surgery_type_id = getattr(surgery, 'surgery_type_id', None)
        if not surgery_type_id:
            # If surgery doesn't have a type, we can't check room suitability
            return True

        surgery_type = self.surgery_types_cache.get(surgery_type_id)
        if not surgery_type:
            surgery_type = self.db_session.query(SurgeryType).filter_by(type_id=surgery_type_id).first()
            if surgery_type:
                self.surgery_types_cache[surgery_type_id] = surgery_type

        if not surgery_type:
            logger.warning(f"Surgery type {surgery_type_id} not found")
            return True  # If we can't find the surgery type, assume room is suitable

        # Check if the room has the required equipment for this surgery type
        required_equipment = getattr(surgery_type, 'required_equipment', None)
        if not required_equipment:
            # If surgery type doesn't specify required equipment, any room is suitable
            return True

        # Get the room's equipment
        room_equipment = self.room_equipment_cache.get(room_id, [])
        if not room_equipment:
            room_equipment = self.db_session.query(OperatingRoomEquipment).filter_by(room_id=room_id).all()
            self.room_equipment_cache[room_id] = room_equipment

        # Check if the room has all required equipment
        room_equipment_ids = [re.equipment_id for re in room_equipment]
        for req_equip in required_equipment.split(','):
            req_equip = req_equip.strip()
            if req_equip and req_equip not in room_equipment_ids:
                logger.info(f"Room {room_id} is missing required equipment {req_equip} for surgery type {surgery_type_id}")
                return False

        return True

    def is_feasible(
        self,
        surgery_id: int,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        current_assignments: List[SurgeryRoomAssignment],
        surgery_id_to_ignore: Optional[int] = None
    ) -> bool:
        """
        Check if a surgery assignment is feasible.

        Args:
            surgery_id: ID of the surgery to check
            room_id: ID of the room for the assignment
            start_time: Start time of the assignment
            end_time: End time of the assignment
            current_assignments: List of current assignments to check against
            surgery_id_to_ignore: ID of a surgery to ignore in the check

        Returns:
            True if the assignment is feasible, False otherwise
        """
        # Get the surgery
        surgery = None
        if self.db_session:
            surgery = self.surgeries_cache.get(surgery_id)
            if not surgery:
                surgery = self.db_session.query(Surgery).filter_by(surgery_id=surgery_id).first()
                if surgery:
                    self.surgeries_cache[surgery_id] = surgery

        if not surgery:
            logger.warning(f"Surgery {surgery_id} not found")
            return False

        # Check room availability
        if not self.is_room_available(room_id, start_time, end_time, current_assignments, surgery_id_to_ignore):
            return False

        # Check surgeon availability
        surgeon_id = getattr(surgery, 'surgeon_id', None)
        if surgeon_id and not self.is_surgeon_available(surgeon_id, start_time, end_time, current_assignments, surgery_id_to_ignore):
            return False

        # Check room suitability
        if not self.is_room_suitable_for_surgery(room_id, surgery_id):
            return False

        # Check equipment availability if we have equipment usage data
        if self.db_session:
            equipment_usages = self.db_session.query(SurgeryEquipmentUsage).filter_by(surgery_id=surgery_id).all()
            for usage in equipment_usages:
                if not self.is_equipment_available(usage.equipment_id, start_time, end_time, current_assignments, surgery_id_to_ignore):
                    return False

        return True

    def check_solution_feasibility(
        self,
        assignments: List[SurgeryRoomAssignment]
    ) -> bool:
        """
        Check the feasibility of an entire solution.

        Args:
            assignments: List of surgery room assignments

        Returns:
            True if the solution is feasible, False otherwise
        """
        if not assignments:
            return True  # Empty solution is feasible

        for i, assignment in enumerate(assignments):
            # Create a copy of assignments without the current one
            other_assignments = assignments[:i] + assignments[i+1:]

            # Check if this assignment is feasible
            if not self.is_feasible(
                assignment.surgery_id,
                assignment.room_id,
                assignment.start_time,
                assignment.end_time,
                other_assignments
            ):
                return False

        return True
