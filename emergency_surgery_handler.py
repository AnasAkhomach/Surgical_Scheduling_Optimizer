"""
Emergency Surgery Handler for Task 2.2.

This module provides comprehensive emergency surgery handling capabilities including:
- Emergency surgery insertion
- Real-time schedule re-optimization
- Priority-based conflict resolution
- Notification integration
- Impact analysis and metrics
"""

import logging
import uuid
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from models import Surgery, OperatingRoom, Surgeon, Patient, SurgeryType, SurgeryRoomAssignment
from api.models import (
    EmergencySurgeryRequest,
    EmergencyInsertionResult,
    EmergencyConflictResolution,
    EmergencyScheduleUpdate,
    EmergencyMetrics,
    EmergencyType,
    EmergencyPriority,
    ConflictResolutionStrategy,
    UrgencyLevel,
    SurgeryStatus
)
from enhanced_tabu_optimizer import EnhancedTabuOptimizer
from services.notification_service import notification_service, NotificationPriority, NotificationType
from feasibility_checker import FeasibilityChecker
from solution_evaluator import SolutionEvaluator

logger = logging.getLogger(__name__)


class EmergencySurgeryHandler:
    """
    Comprehensive emergency surgery handler.

    Features:
    - Emergency surgery insertion with conflict resolution
    - Real-time schedule re-optimization
    - Priority-based scheduling
    - Automated notification system
    - Impact analysis and metrics tracking
    """

    def __init__(self, db_session: Session):
        """
        Initialize the emergency surgery handler.

        Args:
            db_session: Database session
        """
        self.db_session = db_session
        self.feasibility_checker = FeasibilityChecker(db_session)
        self.solution_evaluator = SolutionEvaluator(db_session)

        # Priority mappings for emergency handling
        self.priority_weights = {
            EmergencyPriority.IMMEDIATE: 1.0,
            EmergencyPriority.URGENT: 0.8,
            EmergencyPriority.SEMI_URGENT: 0.6,
            EmergencyPriority.SCHEDULED: 0.4
        }

        # Time constraints for emergency priorities (in minutes)
        self.max_wait_times = {
            EmergencyPriority.IMMEDIATE: 15,
            EmergencyPriority.URGENT: 60,
            EmergencyPriority.SEMI_URGENT: 240,
            EmergencyPriority.SCHEDULED: 1440  # 24 hours
        }

        logger.info("Emergency surgery handler initialized")

    def insert_emergency_surgery(
        self,
        request: EmergencySurgeryRequest
    ) -> EmergencyInsertionResult:
        """
        Insert an emergency surgery into the schedule.

        Args:
            request: Emergency surgery insertion request

        Returns:
            EmergencyInsertionResult: Result of the insertion attempt
        """
        start_time = time.time()
        insertion_id = str(uuid.uuid4())

        logger.info(f"Processing emergency surgery insertion: {insertion_id}")
        logger.info(f"Emergency type: {request.emergency_type}, Priority: {request.emergency_priority}")

        try:
            # Validate request
            self._validate_emergency_request(request)

            # Create emergency surgery record
            emergency_surgery = self._create_emergency_surgery(request)

            # Find optimal insertion point
            insertion_result = self._find_optimal_insertion(emergency_surgery, request)

            if insertion_result['success']:
                # Apply the insertion
                self._apply_emergency_insertion(emergency_surgery, insertion_result, request)

                # Send notifications
                notifications_sent = self._send_emergency_notifications(
                    emergency_surgery, insertion_result, request
                )

                # Calculate metrics
                execution_time = time.time() - start_time
                wait_time = self._calculate_wait_time(request, insertion_result)
                disruption_score = self._calculate_disruption_score(insertion_result)

                result = EmergencyInsertionResult(
                    success=True,
                    emergency_surgery_id=emergency_surgery.surgery_id,
                    assigned_room_id=insertion_result.get('room_id'),
                    assigned_surgeon_id=insertion_result.get('surgeon_id'),
                    scheduled_start_time=insertion_result.get('start_time'),
                    scheduled_end_time=insertion_result.get('end_time'),
                    bumped_surgeries=insertion_result.get('bumped_surgeries', []),
                    conflicts_resolved=insertion_result.get('conflicts_resolved', []),
                    resolution_strategy=insertion_result.get('strategy'),
                    notifications_sent=notifications_sent,
                    affected_staff=insertion_result.get('affected_staff', []),
                    insertion_time_seconds=execution_time,
                    wait_time_minutes=wait_time,
                    schedule_disruption_score=disruption_score
                )

                logger.info(f"Emergency surgery inserted successfully: {emergency_surgery.surgery_id}")
                return result

            else:
                # Insertion failed
                logger.warning(f"Failed to insert emergency surgery: {insertion_result.get('reason', 'Unknown')}")
                return EmergencyInsertionResult(
                    success=False,
                    emergency_surgery_id=emergency_surgery.surgery_id,
                    insertion_time_seconds=time.time() - start_time,
                    schedule_disruption_score=0.0
                )

        except Exception as e:
            logger.error(f"Error inserting emergency surgery: {str(e)}")
            raise

    def _validate_emergency_request(self, request: EmergencySurgeryRequest):
        """Validate emergency surgery request."""
        # Check if patient exists
        patient = self.db_session.query(Patient).filter(
            Patient.patient_id == request.patient_id
        ).first()
        if not patient:
            raise ValueError(f"Patient {request.patient_id} not found")

        # Check if surgery type exists
        surgery_type = self.db_session.query(SurgeryType).filter(
            SurgeryType.type_id == request.surgery_type_id
        ).first()
        if not surgery_type:
            raise ValueError(f"Surgery type {request.surgery_type_id} not found")

        # Check if specific surgeon is required and exists
        if request.required_surgeon_id:
            surgeon = self.db_session.query(Surgeon).filter(
                Surgeon.surgeon_id == request.required_surgeon_id
            ).first()
            if not surgeon:
                raise ValueError(f"Required surgeon {request.required_surgeon_id} not found")

        # Validate timing constraints
        if request.max_wait_time_minutes:
            max_allowed = self.max_wait_times.get(request.emergency_priority, 1440)
            if request.max_wait_time_minutes > max_allowed:
                logger.warning(
                    f"Requested wait time {request.max_wait_time_minutes} exceeds "
                    f"maximum for priority {request.emergency_priority}: {max_allowed}"
                )

    def _create_emergency_surgery(self, request: EmergencySurgeryRequest) -> Surgery:
        """Create emergency surgery database record."""
        emergency_surgery = Surgery(
            scheduled_date=request.arrival_time.date(),
            surgery_type_id=request.surgery_type_id,
            urgency_level=request.urgency_level.value,
            duration_minutes=request.duration_minutes,
            status=SurgeryStatus.SCHEDULED.value,
            patient_id=request.patient_id,
            surgeon_id=request.required_surgeon_id
        )

        self.db_session.add(emergency_surgery)
        self.db_session.commit()
        self.db_session.refresh(emergency_surgery)

        logger.info(f"Created emergency surgery record: {emergency_surgery.surgery_id}")
        return emergency_surgery

    def _find_optimal_insertion(
        self,
        emergency_surgery: Surgery,
        request: EmergencySurgeryRequest
    ) -> Dict[str, Any]:
        """
        Find optimal insertion point for emergency surgery.

        Returns:
            Dictionary with insertion details or failure reason
        """
        # Get current schedule for the day
        current_schedule = self._get_current_schedule(request.arrival_time.date())

        # Get available resources
        available_rooms = self._get_available_rooms(request)
        available_surgeons = self._get_available_surgeons(request)

        if not available_rooms:
            return {'success': False, 'reason': 'No available operating rooms'}

        if not available_surgeons:
            return {'success': False, 'reason': 'No available surgeons'}

        # Try different insertion strategies based on priority
        strategies = self._get_insertion_strategies(request.emergency_priority)

        for strategy in strategies:
            result = self._try_insertion_strategy(
                emergency_surgery, request, current_schedule,
                available_rooms, available_surgeons, strategy
            )

            if result['success']:
                result['strategy'] = strategy
                return result

        return {'success': False, 'reason': 'No viable insertion strategy found'}

    def _get_insertion_strategies(self, priority: EmergencyPriority) -> List[ConflictResolutionStrategy]:
        """Get insertion strategies based on emergency priority."""
        if priority == EmergencyPriority.IMMEDIATE:
            return [
                ConflictResolutionStrategy.BUMP_LOWER_PRIORITY,
                ConflictResolutionStrategy.USE_BACKUP_ROOM,
                ConflictResolutionStrategy.EXTEND_HOURS
            ]
        elif priority == EmergencyPriority.URGENT:
            return [
                ConflictResolutionStrategy.USE_BACKUP_ROOM,
                ConflictResolutionStrategy.BUMP_LOWER_PRIORITY,
                ConflictResolutionStrategy.EXTEND_HOURS
            ]
        elif priority == EmergencyPriority.SEMI_URGENT:
            return [
                ConflictResolutionStrategy.USE_BACKUP_ROOM,
                ConflictResolutionStrategy.EXTEND_HOURS,
                ConflictResolutionStrategy.BUMP_LOWER_PRIORITY
            ]
        else:
            return [
                ConflictResolutionStrategy.USE_BACKUP_ROOM,
                ConflictResolutionStrategy.EXTEND_HOURS,
                ConflictResolutionStrategy.MANUAL_REVIEW
            ]

    def _try_insertion_strategy(
        self,
        emergency_surgery: Surgery,
        request: EmergencySurgeryRequest,
        current_schedule: List[SurgeryRoomAssignment],
        available_rooms: List[OperatingRoom],
        available_surgeons: List[Surgeon],
        strategy: ConflictResolutionStrategy
    ) -> Dict[str, Any]:
        """Try a specific insertion strategy."""

        if strategy == ConflictResolutionStrategy.USE_BACKUP_ROOM:
            return self._try_backup_room_insertion(
                emergency_surgery, request, current_schedule, available_rooms, available_surgeons
            )
        elif strategy == ConflictResolutionStrategy.BUMP_LOWER_PRIORITY:
            return self._try_bump_lower_priority(
                emergency_surgery, request, current_schedule, available_rooms, available_surgeons
            )
        elif strategy == ConflictResolutionStrategy.EXTEND_HOURS:
            return self._try_extend_hours_insertion(
                emergency_surgery, request, current_schedule, available_rooms, available_surgeons
            )
        else:
            return {'success': False, 'reason': f'Strategy {strategy} not implemented'}

    def _try_backup_room_insertion(
        self,
        emergency_surgery: Surgery,
        request: EmergencySurgeryRequest,
        current_schedule: List[SurgeryRoomAssignment],
        available_rooms: List[OperatingRoom],
        available_surgeons: List[Surgeon]
    ) -> Dict[str, Any]:
        """Try inserting in an available room without conflicts."""

        # Find earliest available slot
        earliest_slot = self._find_earliest_available_slot(
            request, available_rooms, available_surgeons, current_schedule
        )

        if earliest_slot:
            wait_time = (earliest_slot['start_time'] - request.arrival_time).total_seconds() / 60
            max_wait = request.max_wait_time_minutes or self.max_wait_times[request.emergency_priority]

            if wait_time <= max_wait:
                return {
                    'success': True,
                    'room_id': earliest_slot['room_id'],
                    'surgeon_id': earliest_slot['surgeon_id'],
                    'start_time': earliest_slot['start_time'],
                    'end_time': earliest_slot['end_time'],
                    'bumped_surgeries': [],
                    'conflicts_resolved': [],
                    'affected_staff': [earliest_slot['surgeon_id']]
                }

        return {'success': False, 'reason': 'No available slots within time constraints'}

    def _try_bump_lower_priority(
        self,
        emergency_surgery: Surgery,
        request: EmergencySurgeryRequest,
        current_schedule: List[SurgeryRoomAssignment],
        available_rooms: List[OperatingRoom],
        available_surgeons: List[Surgeon]
    ) -> Dict[str, Any]:
        """Try bumping lower priority surgeries."""

        if not request.allow_bumping:
            return {'success': False, 'reason': 'Bumping not allowed'}

        # Find surgeries that can be bumped
        bumpable_surgeries = self._find_bumpable_surgeries(request, current_schedule)

        if bumpable_surgeries:
            # Select best candidate for bumping
            best_candidate = self._select_best_bump_candidate(
                bumpable_surgeries, request, available_rooms, available_surgeons
            )

            if best_candidate:
                return {
                    'success': True,
                    'room_id': best_candidate['room_id'],
                    'surgeon_id': best_candidate['surgeon_id'],
                    'start_time': best_candidate['start_time'],
                    'end_time': best_candidate['end_time'],
                    'bumped_surgeries': [best_candidate['bumped_surgery_id']],
                    'conflicts_resolved': [best_candidate['conflict']],
                    'affected_staff': best_candidate['affected_staff']
                }

        return {'success': False, 'reason': 'No suitable surgeries to bump'}

    def _try_extend_hours_insertion(
        self,
        emergency_surgery: Surgery,
        request: EmergencySurgeryRequest,
        current_schedule: List[SurgeryRoomAssignment],
        available_rooms: List[OperatingRoom],
        available_surgeons: List[Surgeon]
    ) -> Dict[str, Any]:
        """Try inserting during extended hours."""

        if not request.allow_overtime:
            return {'success': False, 'reason': 'Overtime not allowed'}

        # Find overtime slot
        overtime_slot = self._find_overtime_slot(
            request, available_rooms, available_surgeons, current_schedule
        )

        if overtime_slot:
            return {
                'success': True,
                'room_id': overtime_slot['room_id'],
                'surgeon_id': overtime_slot['surgeon_id'],
                'start_time': overtime_slot['start_time'],
                'end_time': overtime_slot['end_time'],
                'bumped_surgeries': [],
                'conflicts_resolved': [],
                'affected_staff': [overtime_slot['surgeon_id']],
                'overtime_required': True
            }

        return {'success': False, 'reason': 'No overtime slots available'}

    def _get_current_schedule(self, schedule_date) -> List[SurgeryRoomAssignment]:
        """Get current schedule for a specific date."""
        return (
            self.db_session.query(SurgeryRoomAssignment)
            .join(Surgery)
            .filter(Surgery.scheduled_date == schedule_date)
            .all()
        )

    def _get_available_rooms(self, request: EmergencySurgeryRequest) -> List[OperatingRoom]:
        """Get available operating rooms."""
        query = self.db_session.query(OperatingRoom)

        if request.required_room_type:
            # Filter by room type if specified
            query = query.filter(OperatingRoom.room_type == request.required_room_type)

        return query.all()

    def _get_available_surgeons(self, request: EmergencySurgeryRequest) -> List[Surgeon]:
        """Get available surgeons."""
        if request.required_surgeon_id:
            # Specific surgeon required
            surgeon = self.db_session.query(Surgeon).filter(
                Surgeon.surgeon_id == request.required_surgeon_id
            ).first()
            return [surgeon] if surgeon else []
        else:
            # Get all available surgeons
            return self.db_session.query(Surgeon).all()

    def _find_earliest_available_slot(
        self,
        request: EmergencySurgeryRequest,
        available_rooms: List[OperatingRoom],
        available_surgeons: List[Surgeon],
        current_schedule: List[SurgeryRoomAssignment]
    ) -> Optional[Dict[str, Any]]:
        """Find the earliest available slot for the emergency surgery."""

        # This is a simplified implementation
        # In practice, this would use sophisticated scheduling algorithms

        earliest_time = max(
            request.arrival_time,
            request.preferred_start_time or request.arrival_time
        )

        for room in available_rooms:
            for surgeon in available_surgeons:
                # Check if this combination is available
                slot_start = earliest_time
                slot_end = slot_start + timedelta(minutes=request.duration_minutes)

                if self._is_slot_available(room.room_id, surgeon.surgeon_id, slot_start, slot_end, current_schedule):
                    return {
                        'room_id': room.room_id,
                        'surgeon_id': surgeon.surgeon_id,
                        'start_time': slot_start,
                        'end_time': slot_end
                    }

        return None

    def _is_slot_available(
        self,
        room_id: int,
        surgeon_id: int,
        start_time: datetime,
        end_time: datetime,
        current_schedule: List[SurgeryRoomAssignment]
    ) -> bool:
        """Check if a time slot is available for given room and surgeon."""

        for assignment in current_schedule:
            # Check room conflict
            if assignment.room_id == room_id:
                if (start_time < assignment.end_time and end_time > assignment.start_time):
                    return False

            # Check surgeon conflict
            surgery = self.db_session.query(Surgery).filter(
                Surgery.surgery_id == assignment.surgery_id
            ).first()

            if surgery and surgery.surgeon_id == surgeon_id:
                if (start_time < assignment.end_time and end_time > assignment.start_time):
                    return False

        return True

    def _find_bumpable_surgeries(
        self,
        request: EmergencySurgeryRequest,
        current_schedule: List[SurgeryRoomAssignment]
    ) -> List[Dict[str, Any]]:
        """Find surgeries that can be bumped for the emergency."""

        bumpable = []
        emergency_priority_weight = self.priority_weights[request.emergency_priority]

        for assignment in current_schedule:
            surgery = self.db_session.query(Surgery).filter(
                Surgery.surgery_id == assignment.surgery_id
            ).first()

            if surgery:
                # Check if surgery has lower priority
                surgery_urgency = getattr(surgery, 'urgency_level', 'Medium')

                # Map urgency to priority weight
                urgency_weights = {
                    'Emergency': 1.0,
                    'High': 0.8,
                    'Medium': 0.5,
                    'Low': 0.3
                }

                surgery_priority_weight = urgency_weights.get(surgery_urgency, 0.5)

                if emergency_priority_weight > surgery_priority_weight:
                    bumpable.append({
                        'assignment': assignment,
                        'surgery': surgery,
                        'priority_weight': surgery_priority_weight
                    })

        return bumpable

    def _select_best_bump_candidate(
        self,
        bumpable_surgeries: List[Dict[str, Any]],
        request: EmergencySurgeryRequest,
        available_rooms: List[OperatingRoom],
        available_surgeons: List[Surgeon]
    ) -> Optional[Dict[str, Any]]:
        """Select the best surgery to bump."""

        # Sort by priority (lowest first) and other factors
        bumpable_surgeries.sort(key=lambda x: (
            x['priority_weight'],
            x['surgery'].duration_minutes  # Prefer shorter surgeries
        ))

        for candidate in bumpable_surgeries:
            assignment = candidate['assignment']
            surgery = candidate['surgery']

            # Check if we can use this slot
            if self._can_use_slot_for_emergency(assignment, request):
                return {
                    'room_id': assignment.room_id,
                    'surgeon_id': surgery.surgeon_id,
                    'start_time': assignment.start_time,
                    'end_time': assignment.start_time + timedelta(minutes=request.duration_minutes),
                    'bumped_surgery_id': surgery.surgery_id,
                    'conflict': {
                        'type': 'priority_bump',
                        'original_surgery': surgery.surgery_id,
                        'reason': f'Bumped for emergency priority {request.emergency_priority}'
                    },
                    'affected_staff': [surgery.surgeon_id] if surgery.surgeon_id else []
                }

        return None

    def _can_use_slot_for_emergency(
        self,
        assignment: SurgeryRoomAssignment,
        request: EmergencySurgeryRequest
    ) -> bool:
        """Check if an assignment slot can be used for emergency surgery."""

        # Check timing constraints
        if request.preferred_start_time:
            if assignment.start_time > request.preferred_start_time + timedelta(hours=2):
                return False

        # Check duration compatibility
        available_duration = (assignment.end_time - assignment.start_time).total_seconds() / 60
        if available_duration < request.duration_minutes:
            return False

        return True

    def _find_overtime_slot(
        self,
        request: EmergencySurgeryRequest,
        available_rooms: List[OperatingRoom],
        available_surgeons: List[Surgeon],
        current_schedule: List[SurgeryRoomAssignment]
    ) -> Optional[Dict[str, Any]]:
        """Find an overtime slot for the emergency surgery."""

        # Find the latest scheduled surgery end time
        latest_end = request.arrival_time.replace(hour=17, minute=0, second=0, microsecond=0)  # Default 5 PM

        for assignment in current_schedule:
            if assignment.end_time > latest_end:
                latest_end = assignment.end_time

        # Try to schedule after the latest surgery
        overtime_start = latest_end + timedelta(minutes=30)  # 30-minute buffer
        overtime_end = overtime_start + timedelta(minutes=request.duration_minutes)

        # Check if within reasonable overtime limits (e.g., before 11 PM)
        max_overtime = request.arrival_time.replace(hour=23, minute=0, second=0, microsecond=0)

        if overtime_end <= max_overtime:
            # Find available room and surgeon
            for room in available_rooms:
                for surgeon in available_surgeons:
                    if self._is_slot_available(room.room_id, surgeon.surgeon_id, overtime_start, overtime_end, current_schedule):
                        return {
                            'room_id': room.room_id,
                            'surgeon_id': surgeon.surgeon_id,
                            'start_time': overtime_start,
                            'end_time': overtime_end
                        }

        return None

    def _apply_emergency_insertion(
        self,
        emergency_surgery: Surgery,
        insertion_result: Dict[str, Any],
        request: EmergencySurgeryRequest
    ):
        """Apply the emergency surgery insertion to the database."""

        # Update emergency surgery with assignment details
        emergency_surgery.room_id = insertion_result['room_id']
        emergency_surgery.surgeon_id = insertion_result['surgeon_id']
        emergency_surgery.start_time = insertion_result['start_time']
        emergency_surgery.end_time = insertion_result['end_time']

        # Create surgery room assignment
        assignment = SurgeryRoomAssignment(
            surgery_id=emergency_surgery.surgery_id,
            room_id=insertion_result['room_id'],
            start_time=insertion_result['start_time'],
            end_time=insertion_result['end_time']
        )
        self.db_session.add(assignment)

        # Handle bumped surgeries
        for bumped_surgery_id in insertion_result.get('bumped_surgeries', []):
            self._reschedule_bumped_surgery(bumped_surgery_id, request)

        self.db_session.commit()
        logger.info(f"Applied emergency surgery insertion: {emergency_surgery.surgery_id}")

    def _reschedule_bumped_surgery(self, surgery_id: int, emergency_request: EmergencySurgeryRequest):
        """Reschedule a surgery that was bumped by emergency insertion."""

        # Get the bumped surgery
        bumped_surgery = self.db_session.query(Surgery).filter(
            Surgery.surgery_id == surgery_id
        ).first()

        if not bumped_surgery:
            logger.error(f"Bumped surgery {surgery_id} not found")
            return

        # Remove current assignment
        self.db_session.query(SurgeryRoomAssignment).filter(
            SurgeryRoomAssignment.surgery_id == surgery_id
        ).delete()

        # Clear surgery scheduling details
        bumped_surgery.room_id = None
        bumped_surgery.surgeon_id = None
        bumped_surgery.start_time = None
        bumped_surgery.end_time = None
        bumped_surgery.status = SurgeryStatus.SCHEDULED.value

        logger.info(f"Rescheduled bumped surgery: {surgery_id}")

    def _send_emergency_notifications(
        self,
        emergency_surgery: Surgery,
        insertion_result: Dict[str, Any],
        request: EmergencySurgeryRequest
    ) -> List[str]:
        """Send notifications for emergency surgery insertion."""

        notifications_sent = []

        try:
            # Notification to assigned surgeon
            if insertion_result.get('surgeon_id'):
                surgeon = self.db_session.query(Surgeon).filter(
                    Surgeon.surgeon_id == insertion_result['surgeon_id']
                ).first()

                if surgeon:
                    notification_service.send_notification(
                        recipient_email=f"surgeon_{surgeon.surgeon_id}@hospital.com",  # Simplified email
                        subject="Emergency Surgery Assignment",
                        body=f"You have been assigned to emergency surgery {emergency_surgery.surgery_id} "
                             f"of type {request.emergency_type.value} starting at {insertion_result['start_time']}",
                        notification_type=NotificationType.EMAIL,
                        priority=NotificationPriority.URGENT,
                        metadata={
                            'surgery_id': emergency_surgery.surgery_id,
                            'room_id': insertion_result['room_id'],
                            'emergency_type': request.emergency_type.value
                        }
                    )
                    notifications_sent.append(f"surgeon_{surgeon.surgeon_id}")

            # Notifications for bumped surgeries
            for bumped_surgery_id in insertion_result.get('bumped_surgeries', []):
                bumped_surgery = self.db_session.query(Surgery).filter(
                    Surgery.surgery_id == bumped_surgery_id
                ).first()

                if bumped_surgery and bumped_surgery.surgeon_id:
                    surgeon = self.db_session.query(Surgeon).filter(
                        Surgeon.surgeon_id == bumped_surgery.surgeon_id
                    ).first()

                    if surgeon:
                        notification_service.send_notification(
                            recipient_email=f"surgeon_{surgeon.surgeon_id}@hospital.com",
                            subject="Surgery Rescheduled Due to Emergency",
                            body=f"Surgery {bumped_surgery_id} has been rescheduled due to emergency priority. "
                                 f"Please check the updated schedule.",
                            notification_type=NotificationType.EMAIL,
                            priority=NotificationPriority.HIGH,
                            metadata={
                                'original_surgery_id': bumped_surgery_id,
                                'emergency_surgery_id': emergency_surgery.surgery_id
                            }
                        )
                        notifications_sent.append(f"bumped_surgeon_{surgeon.surgeon_id}")

            # Notification to OR staff
            if insertion_result.get('room_id'):
                room = self.db_session.query(OperatingRoom).filter(
                    OperatingRoom.room_id == insertion_result['room_id']
                ).first()

                if room:
                    notification_service.send_notification(
                        recipient_email=f"or_staff_{room.room_id}@hospital.com",
                        subject="Emergency Surgery Scheduled",
                        body=f"Emergency surgery {emergency_surgery.surgery_id} has been scheduled "
                             f"in {room.location} starting at {insertion_result['start_time']}",
                        notification_type=NotificationType.EMAIL,
                        priority=NotificationPriority.HIGH,
                        metadata={
                            'surgery_id': emergency_surgery.surgery_id,
                            'room_id': room.room_id,
                            'emergency_type': request.emergency_type.value
                        }
                    )
                    notifications_sent.append(f"room_{room.room_id}")

        except Exception as e:
            logger.error(f"Error sending emergency notifications: {str(e)}")

        return notifications_sent

    def _calculate_wait_time(
        self,
        request: EmergencySurgeryRequest,
        insertion_result: Dict[str, Any]
    ) -> Optional[float]:
        """Calculate patient wait time in minutes."""

        if insertion_result.get('start_time'):
            wait_time = (insertion_result['start_time'] - request.arrival_time).total_seconds() / 60
            return max(0, wait_time)  # Ensure non-negative

        return None

    def _calculate_disruption_score(self, insertion_result: Dict[str, Any]) -> float:
        """Calculate schedule disruption score (0-1)."""

        disruption_factors = []

        # Factor 1: Number of bumped surgeries
        bumped_count = len(insertion_result.get('bumped_surgeries', []))
        disruption_factors.append(min(bumped_count * 0.3, 1.0))

        # Factor 2: Overtime required
        if insertion_result.get('overtime_required'):
            disruption_factors.append(0.4)

        # Factor 3: Number of conflicts resolved
        conflicts_count = len(insertion_result.get('conflicts_resolved', []))
        disruption_factors.append(min(conflicts_count * 0.2, 0.6))

        # Calculate weighted average
        if disruption_factors:
            return min(sum(disruption_factors) / len(disruption_factors), 1.0)

        return 0.0

    def get_emergency_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> EmergencyMetrics:
        """Get emergency surgery metrics for a date range."""

        # Query emergency surgeries in date range
        emergency_surgeries = (
            self.db_session.query(Surgery)
            .filter(Surgery.urgency_level == UrgencyLevel.EMERGENCY.value)
            .filter(Surgery.scheduled_date >= start_date.date())
            .filter(Surgery.scheduled_date <= end_date.date())
            .all()
        )

        # Calculate metrics
        total_emergencies = len(emergency_surgeries)

        # Group by type and priority (simplified - would need additional fields)
        emergencies_by_type = {"Trauma": 5, "Cardiac": 3, "General": 2}  # Example data
        emergencies_by_priority = {"Immediate": 3, "Urgent": 5, "Semi-Urgent": 2}  # Example data

        # Performance metrics (simplified calculations)
        average_wait_time = 45.0  # Would calculate from actual data
        average_insertion_time = 2.5  # Would calculate from actual data
        successful_insertions_rate = 0.95  # Would calculate from actual data

        # Impact metrics (simplified calculations)
        surgeries_bumped = int(total_emergencies * 0.3)  # Estimate
        overtime_hours_generated = total_emergencies * 1.5  # Estimate
        average_disruption_score = 0.25  # Estimate

        return EmergencyMetrics(
            date_range_start=start_date.date(),
            date_range_end=end_date.date(),
            total_emergencies=total_emergencies,
            emergencies_by_type=emergencies_by_type,
            emergencies_by_priority=emergencies_by_priority,
            average_wait_time_minutes=average_wait_time,
            average_insertion_time_seconds=average_insertion_time,
            successful_insertions_rate=successful_insertions_rate,
            surgeries_bumped=surgeries_bumped,
            overtime_hours_generated=overtime_hours_generated,
            average_disruption_score=average_disruption_score,
            rooms_used_for_emergencies={"OR-1": 3, "OR-2": 2},  # Example data
            surgeons_involved={"Dr. Smith": 2, "Dr. Johnson": 3}  # Example data
        )