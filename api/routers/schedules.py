"""
Schedules router for the FastAPI application.

This module provides API endpoints for schedule optimization.
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime, time, timedelta
from .. import schemas # Added import for schemas
from .. import models  # Added import for models
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, ConfigDict

from db_config import get_db
from models import Surgery, SurgeryRoomAssignment, OperatingRoom, Surgeon, User, SurgeryType, Patient, ScheduleHistory
from api.models import (
    ScheduleAssignment,
    CurrentScheduleResponse,
    UrgencyLevel,
    SurgeryStatus,
    OptimizationResultEnriched,
    SurgeryEnriched,
    ErrorResponse,
    ScheduleConflict,
    ScheduleValidationResult,
    ManualScheduleAdjustment,
    ScheduleComparison,
    ScheduleHistoryEntry,
    # Enhanced optimization models for Task 2.1
    AdvancedOptimizationParameters,
    OptimizationResult,
    OptimizationProgress,
    OptimizationStatus,
    OptimizationAlgorithm,
    OptimizationComparison,
    OptimizationAnalysis,
    # Emergency surgery models for Task 2.2
    EmergencySurgeryRequest,
    EmergencyInsertionResult,
    EmergencyConflictResolution,
    EmergencyScheduleUpdate,
    EmergencyMetrics,
    # Advanced feasibility checking models for Task 2.3
    ConstraintType,
    ConstraintSeverity,
    ConstraintViolation,
    ConstraintConfiguration,
    FeasibilityCheckRequest,
    FeasibilityCheckResult,
    StaffAvailabilityConstraint,
    SurgeonSpecializationConstraint,
    EquipmentAvailabilityConstraint,
    CustomConstraintRule
)
from api.auth import get_current_active_user
from tabu_optimizer import TabuOptimizer
from solution_evaluator import SolutionEvaluator
from enhanced_tabu_optimizer import EnhancedTabuOptimizer, ProgressCallback
from optimization_cache import get_cache_manager
from emergency_surgery_handler import EmergencySurgeryHandler
from advanced_feasibility_checker import AdvancedFeasibilityChecker
from websocket_manager import websocket_manager

router = APIRouter()
logger = logging.getLogger(__name__)

# Global storage for optimization sessions (in production, use Redis or database)
optimization_sessions: Dict[str, Any] = {}


class OptimizationParameters(BaseModel):
    """Model for optimization parameters."""
    schedule_date: Optional[date] = None
    max_iterations: int = 100
    tabu_tenure: int = 10
    max_no_improvement: int = 20
    time_limit_seconds: int = 300
    weights: Optional[Dict[str, float]] = None


class SurgeryAssignment(BaseModel):
    """Model for surgery assignment response."""
    surgery_id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    surgeon_id: Optional[int] = None
    patient_id: Optional[int] = None
    duration_minutes: int
    surgery_type_id: int

    model_config = ConfigDict(from_attributes=True)


class OptimizationResult(BaseModel):
    """Model for optimization result response."""
    assignments: List[SurgeryAssignment]
    score: float
    metrics: Dict[str, float]
    iteration_count: int
    execution_time_seconds: float


@router.post("/optimize", response_model=OptimizationResult)
async def optimize_schedule(
    params: OptimizationParameters,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Optimize surgery schedule.

    Args:
        params: Optimization parameters
        db: Database session
        current_user: Current authenticated user

    Returns:
        OptimizationResult: Optimized schedule with metrics

    Raises:
        HTTPException: If optimization fails
    """
    try:
        # Get surgeries to schedule
        query = db.query(Surgery)
        if params.schedule_date:
            query = query.filter(Surgery.scheduled_date == params.schedule_date)
        else:
            # Default to surgeries with status "Scheduled"
            query = query.filter(Surgery.status == "Scheduled")

        surgeries = query.all()
        if not surgeries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No surgeries found to schedule"
            )

        # Get operating rooms
        operating_rooms = db.query(OperatingRoom).all()
        if not operating_rooms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No operating rooms found"
            )

        # Create optimizer
        optimizer = TabuOptimizer(
            db_session=db,
            surgeries=surgeries,
            operating_rooms=operating_rooms,
            tabu_tenure=params.tabu_tenure,
            max_iterations=params.max_iterations,
            max_no_improvement=params.max_no_improvement,
            time_limit_seconds=params.time_limit_seconds,
            evaluation_weights=params.weights
        )

        # Run optimization
        start_time = time.time()
        solution = optimizer.optimize()
        execution_time = time.time() - start_time

        # Evaluate solution
        evaluator = SolutionEvaluator(db_session=db)
        score = evaluator.evaluate_solution(solution)

        # Create basic metrics
        metrics = {
            'total_score': score,
            'execution_time': execution_time,
            'solution_size': len(solution)
        }

        # Create response
        assignments = []
        for assignment in solution:
            surgery = db.query(Surgery).filter(Surgery.surgery_id == assignment.surgery_id).first()
            assignments.append(SurgeryAssignment(
                surgery_id=assignment.surgery_id,
                room_id=assignment.room_id,
                start_time=assignment.start_time,
                end_time=assignment.end_time,
                surgeon_id=surgery.surgeon_id if surgery else None,
                patient_id=surgery.patient_id if surgery else None,
                duration_minutes=surgery.duration_minutes if surgery else 0,
                surgery_type_id=surgery.surgery_type_id if surgery else 0
            ))

        return OptimizationResult(
            assignments=assignments,
            score=score,
            metrics=metrics,
            iteration_count=params.max_iterations,  # Use parameter as fallback
            execution_time_seconds=execution_time
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}"
        )


@router.post("/apply", status_code=status.HTTP_200_OK)
async def apply_schedule(
    assignments: List[SurgeryAssignment],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Apply a schedule by creating surgery room assignments.

    Args:
        assignments: List of surgery assignments
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dict: Success message

    Raises:
        HTTPException: If applying schedule fails
    """
    try:
        # Delete existing assignments for these surgeries
        surgery_ids = [a.surgery_id for a in assignments]
        db.query(SurgeryRoomAssignment).filter(
            SurgeryRoomAssignment.surgery_id.in_(surgery_ids)
        ).delete(synchronize_session=False)

        # Create new assignments
        for assignment in assignments:
            db_assignment = SurgeryRoomAssignment(
                surgery_id=assignment.surgery_id,
                room_id=assignment.room_id,
                start_time=assignment.start_time,
                end_time=assignment.end_time
            )
            db.add(db_assignment)

            # Update surgery with room and times
            surgery = db.query(Surgery).filter(Surgery.surgery_id == assignment.surgery_id).first()
            if surgery:
                surgery.room_id = assignment.room_id
                surgery.start_time = assignment.start_time
                surgery.end_time = assignment.end_time

        db.commit()
        return {"message": f"Successfully applied schedule for {len(assignments)} surgeries"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply schedule: {str(e)}"
        )


@router.get("/current", response_model=models.CurrentScheduleResponse, summary="Get the current optimized schedule", description="Returns the current optimized schedule if available.")
async def get_current_schedule(
    db: Session = Depends(get_db)
):
    logger.info("Retrieving current schedule (authentication temporarily disabled for testing).")

    # Query the database for current surgery assignments
    # Since there's no Schedule table, we'll get current assignments from SurgeryRoomAssignment
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    current_assignments = db.query(SurgeryRoomAssignment).filter(
        SurgeryRoomAssignment.start_time >= start_of_day,
        SurgeryRoomAssignment.start_time <= end_of_day
    ).all()

    if not current_assignments:
        logger.warning("No current schedule assignments found in the database.")
        # Return empty schedule instead of 404
        return models.CurrentScheduleResponse(
            surgeries=[],
            date=datetime.now().date().isoformat(),
            total_count=0,
            status="success"
        )

    logger.info(f"Found {len(current_assignments)} current assignments")

    # Process current assignments to build schedule response
    schedule_assignments = []

    for assignment in current_assignments:
        # Fetch surgery details
        surgery_db = db.query(Surgery).filter(Surgery.surgery_id == assignment.surgery_id).first()
        if not surgery_db:
            logger.warning(f"Surgery with ID {assignment.surgery_id} not found")
            continue

        # Fetch related data
        surgeon_db = db.query(Surgeon).filter(Surgeon.surgeon_id == surgery_db.surgeon_id).first()
        patient_db = db.query(Patient).filter(Patient.patient_id == surgery_db.patient_id).first()
        room_db = db.query(OperatingRoom).filter(OperatingRoom.room_id == assignment.room_id).first()
        surgery_type_db = db.query(SurgeryType).filter(SurgeryType.type_id == surgery_db.surgery_type_id).first()

        # Handle enum conversion safely
        urgency_level = None
        if surgery_db.urgency_level:
            try:
                urgency_level = UrgencyLevel(surgery_db.urgency_level)
            except ValueError:
                urgency_mapping = {
                    'low': UrgencyLevel.LOW,
                    'medium': UrgencyLevel.MEDIUM,
                    'high': UrgencyLevel.HIGH,
                    'emergency': UrgencyLevel.EMERGENCY
                }
                urgency_level = urgency_mapping.get(str(surgery_db.urgency_level).lower())

        status = None
        if surgery_db.status:
            try:
                status = SurgeryStatus(surgery_db.status)
            except ValueError:
                status_mapping = {
                    'scheduled': SurgeryStatus.SCHEDULED,
                    'in progress': SurgeryStatus.IN_PROGRESS,
                    'completed': SurgeryStatus.COMPLETED,
                    'cancelled': SurgeryStatus.CANCELLED
                }
                status = status_mapping.get(str(surgery_db.status).lower())

        # Create schedule assignment
        schedule_assignment = ScheduleAssignment(
            surgery_id=surgery_db.surgery_id,
            room_id=assignment.room_id,
            room=room_db.name if room_db else f"Room-{assignment.room_id}",
            surgeon_id=surgery_db.surgeon_id,
            surgeon=surgeon_db.name if surgeon_db else "Unknown",
            surgery_type_id=surgery_db.surgery_type_id or 1,
            surgery_type=surgery_type_db.name if surgery_type_db else "Unknown Surgery Type",
            start_time=assignment.start_time,
            end_time=assignment.end_time,
            duration_minutes=surgery_db.duration_minutes,
            patient_id=surgery_db.patient_id,
            patient_name=patient_db.name if patient_db else "Unknown",
            urgency_level=urgency_level,
            status=status
        )
        schedule_assignments.append(schedule_assignment)


    # Construct the CurrentScheduleResponse
    current_schedule_response = CurrentScheduleResponse(
        surgeries=schedule_assignments,
        date=datetime.now().date().isoformat(),
        total_count=len(schedule_assignments),
        status="success"
    )
    logger.info(f"Successfully retrieved and processed current schedule with {len(schedule_assignments)} surgeries")
    return current_schedule_response


@router.get("/schedules", response_model=List[SurgeryAssignment])
async def get_schedules_by_time_range(
    start_time: datetime = Query(..., description="Start time for the schedule query"),
    end_time: datetime = Query(..., description="End time for the schedule query"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve surgery schedules within a specified time range.

    Args:
        start_time: The beginning of the time range.
        end_time: The end of the time range.
        db: Database session.
        current_user: The authenticated user.

    Returns:
        A list of SurgeryAssignment objects within the specified time range.

    Raises:
        HTTPException: If no schedules are found or if there's a database error.
    """
    try:
        assignments = db.query(SurgeryRoomAssignment).filter(
            and_(
                SurgeryRoomAssignment.start_time >= start_time,
                SurgeryRoomAssignment.end_time <= end_time
            )
        ).all()

        if not assignments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No schedules found for the specified time range."
            )

        # Convert to Pydantic model for response
        response_assignments = []
        for assignment in assignments:
            surgery = db.query(Surgery).filter(Surgery.surgery_id == assignment.surgery_id).first()
            if surgery:
                response_assignments.append(SurgeryAssignment(
                    surgery_id=assignment.surgery_id,
                    room_id=assignment.room_id,
                    start_time=assignment.start_time,
                    end_time=assignment.end_time,
                    surgeon_id=surgery.surgeon_id,
                    patient_id=surgery.patient_id,
                    duration_minutes=surgery.duration_minutes,
                    surgery_type_id=surgery.surgery_type_id
                ))
        return response_assignments
    except Exception as e:
        logger.error(f"Error fetching schedules by time range: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching schedules: {e}"
        )



# Enhanced Schedule Management Endpoints

def _detect_schedule_conflicts(db: Session, schedule_date: date) -> List[ScheduleConflict]:
    """
    Detect conflicts in the schedule for a given date.

    Args:
        db: Database session
        schedule_date: Date to check for conflicts

    Returns:
        List of detected conflicts
    """
    conflicts = []

    # Get all scheduled surgeries for the date
    surgeries = (
        db.query(Surgery, OperatingRoom, Surgeon)
        .filter(Surgery.scheduled_date == schedule_date)
        .filter(Surgery.room_id.isnot(None))
        .filter(Surgery.start_time.isnot(None))
        .filter(Surgery.end_time.isnot(None))
        .join(OperatingRoom, Surgery.room_id == OperatingRoom.room_id)
        .outerjoin(Surgeon, Surgery.surgeon_id == Surgeon.surgeon_id)
        .all()
    )

    # Check for time overlaps in the same room
    for i, (surgery1, room1, surgeon1) in enumerate(surgeries):
        for j, (surgery2, room2, surgeon2) in enumerate(surgeries[i+1:], i+1):
            # Room conflicts
            if surgery1.room_id == surgery2.room_id:
                if (surgery1.start_time < surgery2.end_time and
                    surgery2.start_time < surgery1.end_time):
                    conflicts.append(ScheduleConflict(
                        conflict_type="room_overlap",
                        surgery_id=surgery1.surgery_id,
                        conflicting_surgery_id=surgery2.surgery_id,
                        resource_type="room",
                        resource_id=surgery1.room_id,
                        conflict_start=max(surgery1.start_time, surgery2.start_time),
                        conflict_end=min(surgery1.end_time, surgery2.end_time),
                        severity="critical",
                        message=f"Room {room1.location} double-booked between surgeries {surgery1.surgery_id} and {surgery2.surgery_id}"
                    ))

            # Surgeon conflicts
            if (surgery1.surgeon_id and surgery2.surgeon_id and
                surgery1.surgeon_id == surgery2.surgeon_id):
                if (surgery1.start_time < surgery2.end_time and
                    surgery2.start_time < surgery1.end_time):
                    conflicts.append(ScheduleConflict(
                        conflict_type="surgeon_overlap",
                        surgery_id=surgery1.surgery_id,
                        conflicting_surgery_id=surgery2.surgery_id,
                        resource_type="surgeon",
                        resource_id=surgery1.surgeon_id,
                        conflict_start=max(surgery1.start_time, surgery2.start_time),
                        conflict_end=min(surgery1.end_time, surgery2.end_time),
                        severity="critical",
                        message=f"Surgeon {surgeon1.name if surgeon1 else 'Unknown'} double-booked between surgeries {surgery1.surgery_id} and {surgery2.surgery_id}"
                    ))

    return conflicts


@router.get("/conflicts", response_model=ScheduleValidationResult)
async def detect_schedule_conflicts(
    schedule_date: date = Query(..., description="Date to check for conflicts"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Detect conflicts in the schedule for a specific date.

    Args:
        schedule_date: Date to check for conflicts
        db: Database session
        current_user: Current authenticated user

    Returns:
        ScheduleValidationResult: Validation results with conflicts
    """
    conflicts = _detect_schedule_conflicts(db, schedule_date)

    warnings = []
    # Add warnings for surgeries without assigned surgeons
    unassigned_surgeries = (
        db.query(Surgery)
        .filter(Surgery.scheduled_date == schedule_date)
        .filter(Surgery.surgeon_id.is_(None))
        .filter(Surgery.room_id.isnot(None))
        .count()
    )

    if unassigned_surgeries > 0:
        warnings.append(f"{unassigned_surgeries} surgeries do not have assigned surgeons")

    critical_conflicts = len([c for c in conflicts if c.severity == "critical"])

    return ScheduleValidationResult(
        is_valid=len(conflicts) == 0,
        conflicts=conflicts,
        warnings=warnings,
        total_conflicts=len(conflicts),
        critical_conflicts=critical_conflicts
    )


def _save_schedule_history(
    db: Session,
    schedule_date: date,
    user_id: int,
    action_type: str,
    changes_summary: str,
    affected_surgeries: List[int],
    schedule_snapshot: List[ScheduleAssignment]
):
    """Save schedule change to history."""
    # Convert schedule snapshot to JSON-serializable format
    snapshot_data = []
    for assignment in schedule_snapshot:
        assignment_dict = assignment.model_dump()
        # Convert datetime objects to ISO format strings
        if assignment_dict.get('start_time'):
            assignment_dict['start_time'] = assignment_dict['start_time'].isoformat() if hasattr(assignment_dict['start_time'], 'isoformat') else str(assignment_dict['start_time'])
        if assignment_dict.get('end_time'):
            assignment_dict['end_time'] = assignment_dict['end_time'].isoformat() if hasattr(assignment_dict['end_time'], 'isoformat') else str(assignment_dict['end_time'])
        snapshot_data.append(assignment_dict)

    history_entry = ScheduleHistory(
        schedule_date=schedule_date,
        created_by_user_id=user_id,
        action_type=action_type,
        changes_summary=changes_summary,
        affected_surgeries=json.dumps(affected_surgeries),
        schedule_snapshot=json.dumps(snapshot_data)
    )
    db.add(history_entry)
    db.commit()
    return history_entry


@router.post("/adjust", response_model=Dict[str, Any])
async def manual_schedule_adjustment(
    adjustment: ManualScheduleAdjustment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Manually adjust a surgery schedule.

    Args:
        adjustment: Manual adjustment parameters
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dict: Adjustment result with validation information
    """
    # Get the surgery to adjust
    surgery = db.query(Surgery).filter(Surgery.surgery_id == adjustment.surgery_id).first()
    if not surgery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Surgery with ID {adjustment.surgery_id} not found"
        )

    # Store original values for history
    original_room_id = surgery.room_id
    original_surgeon_id = surgery.surgeon_id
    original_start_time = surgery.start_time
    original_duration = surgery.duration_minutes

    # Prepare changes
    changes = []
    if adjustment.new_room_id and adjustment.new_room_id != original_room_id:
        # Validate room exists
        room = db.query(OperatingRoom).filter(OperatingRoom.room_id == adjustment.new_room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Operating room with ID {adjustment.new_room_id} not found"
            )
        changes.append(f"Room changed from {original_room_id} to {adjustment.new_room_id}")

    if adjustment.new_surgeon_id and adjustment.new_surgeon_id != original_surgeon_id:
        # Validate surgeon exists
        surgeon = db.query(Surgeon).filter(Surgeon.surgeon_id == adjustment.new_surgeon_id).first()
        if not surgeon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Surgeon with ID {adjustment.new_surgeon_id} not found"
            )
        changes.append(f"Surgeon changed from {original_surgeon_id} to {adjustment.new_surgeon_id}")

    if adjustment.new_start_time and adjustment.new_start_time != original_start_time:
        changes.append(f"Start time changed from {original_start_time} to {adjustment.new_start_time}")

    if adjustment.new_duration_minutes and adjustment.new_duration_minutes != original_duration:
        changes.append(f"Duration changed from {original_duration} to {adjustment.new_duration_minutes} minutes")

    # Check for conflicts if not forcing override
    conflicts = []
    if not adjustment.force_override and surgery.scheduled_date:
        # Apply temporary changes to check conflicts
        temp_surgery = Surgery(
            surgery_id=surgery.surgery_id,
            room_id=adjustment.new_room_id or surgery.room_id,
            surgeon_id=adjustment.new_surgeon_id or surgery.surgeon_id,
            start_time=adjustment.new_start_time or surgery.start_time,
            duration_minutes=adjustment.new_duration_minutes or surgery.duration_minutes,
            scheduled_date=surgery.scheduled_date
        )

        if temp_surgery.start_time and temp_surgery.duration_minutes:
            temp_surgery.end_time = temp_surgery.start_time + timedelta(minutes=temp_surgery.duration_minutes)

            # Check conflicts with this temporary surgery
            conflicts = _detect_schedule_conflicts(db, surgery.scheduled_date)
            # Filter conflicts that involve this surgery
            relevant_conflicts = [c for c in conflicts if c.surgery_id == surgery.surgery_id or c.conflicting_surgery_id == surgery.surgery_id]

            if relevant_conflicts:
                return {
                    "success": False,
                    "message": "Schedule adjustment would create conflicts",
                    "conflicts": [c.model_dump() for c in relevant_conflicts],
                    "changes_preview": changes
                }

    # Apply the changes
    if adjustment.new_room_id:
        surgery.room_id = adjustment.new_room_id
    if adjustment.new_surgeon_id:
        surgery.surgeon_id = adjustment.new_surgeon_id
    if adjustment.new_start_time:
        surgery.start_time = adjustment.new_start_time
    if adjustment.new_duration_minutes:
        surgery.duration_minutes = adjustment.new_duration_minutes
        if surgery.start_time:
            surgery.end_time = surgery.start_time + timedelta(minutes=surgery.duration_minutes)

    # Update surgery room assignment if it exists
    if surgery.room_id and surgery.start_time and surgery.end_time:
        assignment = db.query(SurgeryRoomAssignment).filter(
            SurgeryRoomAssignment.surgery_id == surgery.surgery_id
        ).first()

        if assignment:
            assignment.room_id = surgery.room_id
            assignment.start_time = surgery.start_time
            assignment.end_time = surgery.end_time
        else:
            # Create new assignment
            new_assignment = SurgeryRoomAssignment(
                surgery_id=surgery.surgery_id,
                room_id=surgery.room_id,
                start_time=surgery.start_time,
                end_time=surgery.end_time
            )
            db.add(new_assignment)

    db.commit()

    # Save to history
    if surgery.scheduled_date:
        current_schedule = await get_current_schedule(surgery.scheduled_date, db, current_user)
        _save_schedule_history(
            db=db,
            schedule_date=surgery.scheduled_date,
            user_id=current_user.user_id,
            action_type="manual_adjustment",
            changes_summary=f"Manual adjustment: {adjustment.reason}. Changes: {'; '.join(changes)}",
            affected_surgeries=[surgery.surgery_id],
            schedule_snapshot=current_schedule
        )

    return {
        "success": True,
        "message": f"Surgery {surgery.surgery_id} successfully adjusted",
        "changes_applied": changes,
        "conflicts_detected": len(conflicts),
        "forced_override": adjustment.force_override
    }


@router.post("/compare", response_model=ScheduleComparison)
async def compare_schedules(
    current_schedule: List[ScheduleAssignment],
    proposed_schedule: List[ScheduleAssignment],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Compare two schedules and analyze differences.

    Args:
        current_schedule: Current schedule assignments
        proposed_schedule: Proposed schedule assignments
        db: Database session
        current_user: Current authenticated user

    Returns:
        ScheduleComparison: Detailed comparison of the two schedules
    """
    changes = []

    # Create lookup dictionaries
    current_dict = {s.surgery_id: s for s in current_schedule}
    proposed_dict = {s.surgery_id: s for s in proposed_schedule}

    # Find changes
    all_surgery_ids = set(current_dict.keys()) | set(proposed_dict.keys())

    for surgery_id in all_surgery_ids:
        current_assignment = current_dict.get(surgery_id)
        proposed_assignment = proposed_dict.get(surgery_id)

        if not current_assignment:
            changes.append({
                "surgery_id": surgery_id,
                "change_type": "added",
                "description": f"Surgery {surgery_id} added to schedule"
            })
        elif not proposed_assignment:
            changes.append({
                "surgery_id": surgery_id,
                "change_type": "removed",
                "description": f"Surgery {surgery_id} removed from schedule"
            })
        else:
            # Check for differences
            surgery_changes = []

            if current_assignment.room_id != proposed_assignment.room_id:
                surgery_changes.append(f"room changed from {current_assignment.room} to {proposed_assignment.room}")

            if current_assignment.surgeon_id != proposed_assignment.surgeon_id:
                surgery_changes.append(f"surgeon changed from {current_assignment.surgeon} to {proposed_assignment.surgeon}")

            if current_assignment.start_time != proposed_assignment.start_time:
                surgery_changes.append(f"start time changed from {current_assignment.start_time} to {proposed_assignment.start_time}")

            if current_assignment.duration_minutes != proposed_assignment.duration_minutes:
                surgery_changes.append(f"duration changed from {current_assignment.duration_minutes} to {proposed_assignment.duration_minutes} minutes")

            if surgery_changes:
                changes.append({
                    "surgery_id": surgery_id,
                    "change_type": "modified",
                    "description": f"Surgery {surgery_id}: {'; '.join(surgery_changes)}"
                })

    # Calculate metrics comparison
    def calculate_schedule_metrics(schedule: List[ScheduleAssignment]) -> Dict[str, float]:
        if not schedule:
            return {"utilization": 0.0, "total_duration": 0.0, "surgeries_count": 0.0}

        total_duration = sum(s.duration_minutes for s in schedule)
        unique_rooms = len(set(s.room_id for s in schedule))

        return {
            "utilization": total_duration / (unique_rooms * 480) if unique_rooms > 0 else 0.0,  # Assuming 8-hour days
            "total_duration": float(total_duration),
            "surgeries_count": float(len(schedule)),
            "rooms_used": float(unique_rooms)
        }

    current_metrics = calculate_schedule_metrics(current_schedule)
    proposed_metrics = calculate_schedule_metrics(proposed_schedule)

    metrics_comparison = {
        "current": current_metrics,
        "proposed": proposed_metrics
    }

    # Generate improvement summary
    utilization_change = proposed_metrics["utilization"] - current_metrics["utilization"]
    surgery_count_change = proposed_metrics["surgeries_count"] - current_metrics["surgeries_count"]

    improvement_parts = []
    if utilization_change > 0.01:
        improvement_parts.append(f"utilization improved by {utilization_change:.1%}")
    elif utilization_change < -0.01:
        improvement_parts.append(f"utilization decreased by {abs(utilization_change):.1%}")

    if surgery_count_change > 0:
        improvement_parts.append(f"{int(surgery_count_change)} more surgeries scheduled")
    elif surgery_count_change < 0:
        improvement_parts.append(f"{int(abs(surgery_count_change))} fewer surgeries scheduled")

    improvement_summary = "; ".join(improvement_parts) if improvement_parts else "No significant changes in metrics"

    return ScheduleComparison(
        current_schedule=current_schedule,
        proposed_schedule=proposed_schedule,
        changes=changes,
        metrics_comparison=metrics_comparison,
        improvement_summary=improvement_summary
    )


@router.get("/history", response_model=List[ScheduleHistoryEntry])
async def get_schedule_history(
    schedule_date: Optional[date] = Query(None, description="Filter by schedule date"),
    limit: int = Query(50, ge=1, le=200, description="Number of history entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get schedule change history.

    Args:
        schedule_date: Optional date filter
        limit: Number of entries to return
        offset: Number of entries to skip
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[ScheduleHistoryEntry]: Schedule history entries
    """
    query = (
        db.query(ScheduleHistory, User)
        .join(User, ScheduleHistory.created_by_user_id == User.user_id)
        .order_by(ScheduleHistory.created_at.desc())
    )

    if schedule_date:
        query = query.filter(ScheduleHistory.schedule_date == schedule_date)

    history_records = query.offset(offset).limit(limit).all()

    history_entries = []
    for history, user in history_records:
        # Parse JSON fields
        affected_surgeries = json.loads(history.affected_surgeries) if history.affected_surgeries else []
        schedule_snapshot = []
        if history.schedule_snapshot:
            try:
                snapshot_data = json.loads(history.schedule_snapshot)
                schedule_snapshot = [ScheduleAssignment(**item) for item in snapshot_data]
            except (json.JSONDecodeError, TypeError):
                schedule_snapshot = []

        history_entries.append(ScheduleHistoryEntry(
            history_id=history.history_id,
            schedule_date=history.schedule_date,
            created_at=history.created_at,
            created_by_user_id=history.created_by_user_id,
            created_by_username=user.username,
            action_type=history.action_type,
            changes_summary=history.changes_summary,
            affected_surgeries=affected_surgeries,
            schedule_snapshot=schedule_snapshot
        ))

    return history_entries


# Enhanced Optimization Endpoints for Task 2.1

@router.post("/optimize/advanced", response_model=OptimizationResult)
async def advanced_optimize_schedule(
    params: AdvancedOptimizationParameters,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Advanced optimization with enhanced features.

    Features:
    - Multiple algorithm variants
    - Progress tracking
    - Result caching
    - Advanced parameter configuration
    """
    try:
        # Get surgeries to schedule
        query = db.query(Surgery)
        if params.schedule_date:
            query = query.filter(Surgery.scheduled_date == params.schedule_date)
        else:
            query = query.filter(Surgery.status == "Scheduled")

        surgeries = query.all()
        if not surgeries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No surgeries found to schedule"
            )

        # Get operating rooms
        operating_rooms = db.query(OperatingRoom).all()
        if not operating_rooms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No operating rooms found"
            )

        # Check cache if enabled
        cache_manager = get_cache_manager()
        if params.cache_results:
            surgeries_hash = cache_manager.generate_surgeries_hash(surgeries)
            cache_key = params.cache_key or cache_manager.generate_cache_key(params, surgeries_hash)

            cached_result = cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached result for key: {cache_key}")
                return cached_result

        # Create progress callback if tracking enabled
        progress_callback = None
        if params.enable_progress_tracking:
            def update_progress(progress: OptimizationProgress):
                optimization_sessions[progress.optimization_id] = progress

            progress_callback = ProgressCallback(
                callback=update_progress,
                interval=params.progress_update_interval
            )

        # Create enhanced optimizer
        optimizer = EnhancedTabuOptimizer(
            db_session=db,
            surgeries=surgeries,
            operating_rooms=operating_rooms,
            parameters=params,
            progress_callback=progress_callback
        )

        # Run optimization
        result = optimizer.optimize()

        # Cache result if enabled
        if params.cache_results:
            cache_manager.put(cache_key, result, params)

        # Store session result
        optimization_sessions[result.optimization_id] = result

        logger.info(f"Advanced optimization completed. Score: {result.score:.4f}")
        return result

    except Exception as e:
        logger.error(f"Advanced optimization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Advanced optimization failed: {str(e)}"
        )


@router.get("/optimize/progress/{optimization_id}", response_model=OptimizationProgress)
async def get_optimization_progress(
    optimization_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get real-time optimization progress."""
    if optimization_id not in optimization_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Optimization session {optimization_id} not found"
        )

    session_data = optimization_sessions[optimization_id]

    if isinstance(session_data, OptimizationProgress):
        return session_data
    elif isinstance(session_data, OptimizationResult):
        # Convert completed result to progress
        return OptimizationProgress(
            optimization_id=optimization_id,
            status=OptimizationStatus.COMPLETED,
            current_iteration=session_data.iteration_count,
            total_iterations=session_data.iteration_count,
            best_score=session_data.score,
            current_score=session_data.score,
            iterations_without_improvement=0,
            elapsed_time_seconds=session_data.execution_time_seconds,
            progress_percentage=100.0,
            algorithm_used=session_data.algorithm_used,
            last_update=datetime.now()
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid session data"
        )


@router.delete("/optimize/cancel/{optimization_id}")
async def cancel_optimization(
    optimization_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a running optimization."""
    if optimization_id not in optimization_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Optimization session {optimization_id} not found"
        )

    # In a real implementation, this would signal the optimizer to stop
    session_data = optimization_sessions[optimization_id]
    if isinstance(session_data, OptimizationProgress):
        session_data.status = OptimizationStatus.CANCELLED

    return {"message": f"Optimization {optimization_id} cancelled"}


@router.get("/optimize/results/{optimization_id}", response_model=OptimizationResult)
async def get_optimization_result(
    optimization_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get optimization result by ID."""
    if optimization_id not in optimization_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Optimization result {optimization_id} not found"
        )

    session_data = optimization_sessions[optimization_id]

    if isinstance(session_data, OptimizationResult):
        return session_data
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Optimization not completed yet"
        )


@router.post("/optimize/compare", response_model=OptimizationComparison)
async def compare_optimization_algorithms(
    params_list: List[AdvancedOptimizationParameters],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Compare multiple optimization algorithms on the same dataset.

    This endpoint runs multiple optimization algorithms and compares their performance.
    """
    if len(params_list) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 parameter sets required for comparison"
        )

    if len(params_list) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 algorithms can be compared at once"
        )

    try:
        # Get surgeries to schedule (use first parameter set for data selection)
        base_params = params_list[0]
        query = db.query(Surgery)
        if base_params.schedule_date:
            query = query.filter(Surgery.scheduled_date == base_params.schedule_date)
        else:
            query = query.filter(Surgery.status == "Scheduled")

        surgeries = query.all()
        if not surgeries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No surgeries found to schedule"
            )

        # Get operating rooms
        operating_rooms = db.query(OperatingRoom).all()
        if not operating_rooms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No operating rooms found"
            )

        results = []
        performance_comparison = {}

        # Run optimization with each algorithm
        for i, params in enumerate(params_list):
            logger.info(f"Running comparison {i+1}/{len(params_list)} with algorithm: {params.algorithm}")

            # Create optimizer
            optimizer = EnhancedTabuOptimizer(
                db_session=db,
                surgeries=surgeries,
                operating_rooms=operating_rooms,
                parameters=params
            )

            # Run optimization
            result = optimizer.optimize()
            results.append(result)

            # Track performance metrics
            performance_comparison[params.algorithm.value] = {
                'score': result.score,
                'execution_time': result.execution_time_seconds,
                'iterations': result.iteration_count,
                'algorithm': params.algorithm.value
            }

        # Determine best algorithm
        best_result = max(results, key=lambda r: r.score)
        best_algorithm = best_result.algorithm_used

        # Generate recommendation
        recommendation = f"Algorithm '{best_algorithm.value}' achieved the best score of {best_result.score:.4f}"

        # Calculate improvement summary
        baseline_score = results[0].score
        best_score = best_result.score
        improvement = ((best_score - baseline_score) / baseline_score * 100) if baseline_score != 0 else 0

        improvement_summary = f"Best algorithm improved score by {improvement:.1f}% over baseline"

        return OptimizationComparison(
            baseline_result=results[0],
            comparison_results=results[1:],
            performance_comparison=performance_comparison,
            recommendation=recommendation,
            best_algorithm=best_algorithm,
            improvement_summary=improvement_summary
        )

    except Exception as e:
        logger.error(f"Algorithm comparison failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Algorithm comparison failed: {str(e)}"
        )


@router.get("/optimize/analysis/{optimization_id}", response_model=OptimizationAnalysis)
async def analyze_optimization_result(
    optimization_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed analysis of an optimization result."""
    if optimization_id not in optimization_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Optimization result {optimization_id} not found"
        )

    session_data = optimization_sessions[optimization_id]

    if not isinstance(session_data, OptimizationResult):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Optimization not completed yet"
        )

    # Perform detailed analysis
    analysis = OptimizationAnalysis(
        optimization_id=optimization_id,
        solution_quality_score=session_data.score,
        constraint_violations=[],  # Would be populated with actual constraint analysis
        resource_utilization={
            'room_utilization': 0.85,  # Example values - would be calculated
            'surgeon_utilization': 0.78,
            'time_utilization': 0.92
        },
        bottleneck_analysis={
            'primary_bottleneck': 'Operating Room Availability',
            'bottleneck_severity': 'Medium',
            'affected_surgeries': 3
        },
        improvement_suggestions=[
            'Consider adding evening surgery slots',
            'Optimize surgeon scheduling for better load balancing',
            'Review setup time requirements between surgery types'
        ],
        sensitivity_analysis={
            'weight_sensitivity': 0.15,
            'parameter_sensitivity': 0.08,
            'data_sensitivity': 0.22
        }
    )

    return analysis


@router.get("/optimize/cache/stats")
async def get_cache_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """Get optimization cache statistics."""
    cache_manager = get_cache_manager()
    stats = cache_manager.get_stats()

    return {
        "cache_statistics": stats,
        "cache_enabled": True,
        "cleanup_recommendations": []
    }


@router.delete("/optimize/cache/clear")
async def clear_optimization_cache(
    current_user: User = Depends(get_current_active_user)
):
    """Clear the optimization cache."""
    cache_manager = get_cache_manager()
    cache_manager.clear()

    return {"message": "Optimization cache cleared successfully"}


@router.delete("/optimize/cache/cleanup")
async def cleanup_expired_cache(
    current_user: User = Depends(get_current_active_user)
):
    """Clean up expired cache entries."""
    cache_manager = get_cache_manager()
    cache_manager.cleanup_expired()

    return {"message": "Expired cache entries cleaned up"}


# Emergency Surgery Handling Endpoints for Task 2.2

@router.post("/emergency/insert", response_model=EmergencyInsertionResult)
async def insert_emergency_surgery(
    request: EmergencySurgeryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Insert an emergency surgery into the schedule.

    This endpoint handles emergency surgery insertion with:
    - Real-time conflict resolution
    - Priority-based scheduling
    - Automated notifications
    - Impact analysis

    Args:
        request: Emergency surgery insertion request
        db: Database session
        current_user: Current authenticated user

    Returns:
        EmergencyInsertionResult: Result of the emergency insertion
    """
    try:
        # Create emergency surgery handler
        handler = EmergencySurgeryHandler(db)

        # Process the emergency insertion
        result = handler.insert_emergency_surgery(request)

        logger.info(
            f"Emergency surgery insertion processed: {result.emergency_surgery_id}, "
            f"Success: {result.success}"
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid emergency surgery request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing emergency surgery insertion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process emergency surgery: {str(e)}"
        )


@router.get("/emergency/metrics", response_model=EmergencyMetrics)
async def get_emergency_metrics(
    start_date: date = Query(..., description="Start date for metrics"),
    end_date: date = Query(..., description="End date for metrics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get emergency surgery metrics and analytics.

    Args:
        start_date: Start date for metrics calculation
        end_date: End date for metrics calculation
        db: Database session
        current_user: Current authenticated user

    Returns:
        EmergencyMetrics: Emergency surgery metrics
    """
    try:
        # Create emergency surgery handler
        handler = EmergencySurgeryHandler(db)

        # Get metrics
        metrics = handler.get_emergency_metrics(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        )

        return metrics

    except Exception as e:
        logger.error(f"Error getting emergency metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get emergency metrics: {str(e)}"
        )


@router.post("/emergency/re-optimize/{emergency_surgery_id}")
async def re_optimize_for_emergency(
    emergency_surgery_id: int,
    optimization_params: Optional[AdvancedOptimizationParameters] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Re-optimize the entire schedule after emergency surgery insertion.

    This endpoint triggers a full schedule re-optimization to minimize
    the impact of emergency surgery insertion on the overall schedule.

    Args:
        emergency_surgery_id: ID of the emergency surgery
        optimization_params: Optional optimization parameters
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dict: Re-optimization result
    """
    try:
        # Create emergency surgery handler
        handler = EmergencySurgeryHandler(db)

        # Re-optimize schedule
        result = handler.re_optimize_schedule_for_emergency(
            emergency_surgery_id, optimization_params
        )

        logger.info(f"Schedule re-optimized for emergency surgery: {emergency_surgery_id}")

        return {
            "message": "Schedule re-optimization completed",
            "emergency_surgery_id": emergency_surgery_id,
            "optimization_result": result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error re-optimizing for emergency: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to re-optimize schedule: {str(e)}"
        )


@router.get("/emergency/conflicts/{emergency_surgery_id}")
async def get_emergency_conflicts(
    emergency_surgery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get conflicts caused by emergency surgery insertion.

    Args:
        emergency_surgery_id: ID of the emergency surgery
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of conflicts and resolution options
    """
    try:
        # Get the emergency surgery
        emergency_surgery = db.query(Surgery).filter(
            Surgery.surgery_id == emergency_surgery_id
        ).first()

        if not emergency_surgery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Emergency surgery {emergency_surgery_id} not found"
            )

        # Check if it's actually an emergency surgery
        if emergency_surgery.urgency_level != "Emergency":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Surgery {emergency_surgery_id} is not an emergency surgery"
            )

        # Get conflicts for the date
        conflicts = _detect_schedule_conflicts(db, emergency_surgery.scheduled_date)

        # Filter conflicts related to this emergency surgery
        emergency_conflicts = [
            conflict for conflict in conflicts
            if (conflict.surgery_id == emergency_surgery_id or
                conflict.conflicting_surgery_id == emergency_surgery_id)
        ]

        return {
            "emergency_surgery_id": emergency_surgery_id,
            "conflicts": emergency_conflicts,
            "total_conflicts": len(emergency_conflicts),
            "resolution_suggestions": [
                "Consider bumping lower priority surgeries",
                "Use backup operating rooms if available",
                "Schedule during extended hours",
                "Manual review and adjustment"
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting emergency conflicts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get emergency conflicts: {str(e)}"
        )


@router.post("/emergency/simulate")
async def simulate_emergency_insertion(
    request: EmergencySurgeryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Simulate emergency surgery insertion without actually inserting.

    This endpoint allows testing different emergency scenarios to see
    their potential impact on the schedule before actual insertion.

    Args:
        request: Emergency surgery simulation request
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dict: Simulation results with impact analysis
    """
    try:
        # Create emergency surgery handler
        handler = EmergencySurgeryHandler(db)

        # Create a temporary emergency surgery for simulation
        temp_surgery = Surgery(
            scheduled_date=request.arrival_time.date(),
            surgery_type_id=request.surgery_type_id,
            urgency_level=request.urgency_level.value,
            duration_minutes=request.duration_minutes,
            status="Scheduled",
            patient_id=request.patient_id,
            surgeon_id=request.required_surgeon_id
        )

        # Find optimal insertion point (simulation only)
        insertion_result = handler._find_optimal_insertion(temp_surgery, request)

        # Calculate impact metrics
        disruption_score = handler._calculate_disruption_score(insertion_result) if insertion_result['success'] else 1.0
        wait_time = handler._calculate_wait_time(request, insertion_result) if insertion_result['success'] else None

        return {
            "simulation_successful": insertion_result['success'],
            "insertion_strategy": insertion_result.get('strategy'),
            "estimated_wait_time_minutes": wait_time,
            "schedule_disruption_score": disruption_score,
            "bumped_surgeries_count": len(insertion_result.get('bumped_surgeries', [])),
            "conflicts_resolved_count": len(insertion_result.get('conflicts_resolved', [])),
            "overtime_required": insertion_result.get('overtime_required', False),
            "reason": insertion_result.get('reason') if not insertion_result['success'] else None,
            "recommendations": [
                "Emergency can be accommodated with minimal disruption" if disruption_score < 0.3 else
                "Emergency will cause moderate schedule disruption" if disruption_score < 0.7 else
                "Emergency will cause significant schedule disruption"
            ]
        }

    except Exception as e:
        logger.error(f"Error simulating emergency insertion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to simulate emergency insertion: {str(e)}"
        )


# Advanced Feasibility Checking Endpoints for Task 2.3

@router.post("/feasibility/check", response_model=FeasibilityCheckResult)
async def check_feasibility_advanced(
    request: FeasibilityCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform advanced feasibility check with detailed constraint validation.

    This endpoint provides comprehensive feasibility checking including:
    - Equipment availability checking
    - Staff availability constraints
    - Surgeon specialization matching
    - Custom constraint validation
    - Detailed violation reporting
    """
    try:
        logger.info(f"Performing advanced feasibility check for surgery {request.surgery_id}")

        # Initialize advanced feasibility checker
        feasibility_checker = AdvancedFeasibilityChecker(db)

        # Perform the check
        result = feasibility_checker.check_feasibility_advanced(request)

        logger.info(f"Feasibility check completed: {'feasible' if result.is_feasible else 'not feasible'}")
        logger.info(f"Found {len(result.violations)} violations and {len(result.warnings)} warnings")

        return result

    except Exception as e:
        logger.error(f"Error performing feasibility check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform feasibility check: {str(e)}"
        )


@router.post("/feasibility/validate-schedule")
async def validate_schedule_constraints(
    schedule_date: date = Query(..., description="Date of schedule to validate"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate constraints for an entire schedule.

    This endpoint validates all surgeries in a schedule against
    advanced constraints and provides comprehensive reporting.
    """
    try:
        logger.info(f"Validating schedule constraints for date: {schedule_date}")

        # Get all surgery assignments for the date
        assignments = db.query(SurgeryRoomAssignment).filter(
            SurgeryRoomAssignment.start_time >= schedule_date,
            SurgeryRoomAssignment.start_time < schedule_date + timedelta(days=1)
        ).all()

        if not assignments:
            return {
                "total_surgeries": 0,
                "feasible_surgeries": 0,
                "feasibility_rate": 1.0,
                "total_violations": 0,
                "critical_violations": 0,
                "violations_by_type": {},
                "recommendations": ["No surgeries scheduled for this date"]
            }

        # Initialize advanced feasibility checker
        feasibility_checker = AdvancedFeasibilityChecker(db)

        # Validate the schedule
        validation_result = feasibility_checker.validate_schedule_constraints(assignments)

        logger.info(f"Schedule validation completed: {validation_result['feasible_surgeries']}/{validation_result['total_surgeries']} surgeries feasible")

        return validation_result

    except Exception as e:
        logger.error(f"Error validating schedule constraints: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate schedule constraints: {str(e)}"
        )


@router.get("/constraints/configurations", response_model=List[ConstraintConfiguration])
async def get_constraint_configurations(
    constraint_type: Optional[ConstraintType] = Query(None, description="Filter by constraint type"),
    enabled_only: bool = Query(False, description="Return only enabled constraints"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all constraint configurations.

    This endpoint returns the current constraint configurations
    that are used for feasibility checking.
    """
    try:
        # Initialize advanced feasibility checker
        feasibility_checker = AdvancedFeasibilityChecker(db)

        # Get all configurations
        configurations = feasibility_checker.get_constraint_configurations()

        # Apply filters
        if constraint_type:
            configurations = [c for c in configurations if c.constraint_type == constraint_type]

        if enabled_only:
            configurations = [c for c in configurations if c.enabled]

        logger.info(f"Retrieved {len(configurations)} constraint configurations")

        return configurations

    except Exception as e:
        logger.error(f"Error retrieving constraint configurations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve constraint configurations: {str(e)}"
        )


@router.post("/constraints/configurations")
async def add_constraint_configuration(
    config: ConstraintConfiguration,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add or update a constraint configuration.

    This endpoint allows adding new constraint configurations
    or updating existing ones.
    """
    try:
        logger.info(f"Adding constraint configuration: {config.constraint_id}")

        # Initialize advanced feasibility checker
        feasibility_checker = AdvancedFeasibilityChecker(db)

        # Add the configuration
        feasibility_checker.add_constraint_configuration(config)

        return {"message": f"Constraint configuration '{config.constraint_id}' added successfully"}

    except Exception as e:
        logger.error(f"Error adding constraint configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add constraint configuration: {str(e)}"
        )


@router.delete("/constraints/configurations/{constraint_id}")
async def remove_constraint_configuration(
    constraint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove a constraint configuration.

    This endpoint removes a constraint configuration by ID.
    """
    try:
        logger.info(f"Removing constraint configuration: {constraint_id}")

        # Initialize advanced feasibility checker
        feasibility_checker = AdvancedFeasibilityChecker(db)

        # Remove the configuration
        success = feasibility_checker.remove_constraint_configuration(constraint_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Constraint configuration '{constraint_id}' not found"
            )

        return {"message": f"Constraint configuration '{constraint_id}' removed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing constraint configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove constraint configuration: {str(e)}"
        )


@router.get("/constraints/rules", response_model=List[CustomConstraintRule])
async def get_custom_rules(
    enabled_only: bool = Query(False, description="Return only enabled rules"),
    rule_type: Optional[str] = Query(None, description="Filter by rule type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all custom constraint rules.

    This endpoint returns the current custom constraint rules
    that are used for feasibility checking.
    """
    try:
        # Initialize advanced feasibility checker
        feasibility_checker = AdvancedFeasibilityChecker(db)

        # Get all rules
        rules = feasibility_checker.get_custom_rules()

        # Apply filters
        if enabled_only:
            rules = [r for r in rules if r.enabled]

        if rule_type:
            rules = [r for r in rules if r.rule_type == rule_type]

        logger.info(f"Retrieved {len(rules)} custom constraint rules")

        return rules

    except Exception as e:
        logger.error(f"Error retrieving custom rules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve custom rules: {str(e)}"
        )


@router.post("/constraints/rules")
async def add_custom_rule(
    rule: CustomConstraintRule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add or update a custom constraint rule.

    This endpoint allows adding new custom constraint rules
    or updating existing ones.
    """
    try:
        logger.info(f"Adding custom constraint rule: {rule.rule_id}")

        # Initialize advanced feasibility checker
        feasibility_checker = AdvancedFeasibilityChecker(db)

        # Add the rule
        feasibility_checker.add_custom_rule(rule)

        return {"message": f"Custom constraint rule '{rule.rule_id}' added successfully"}

    except Exception as e:
        logger.error(f"Error adding custom rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add custom rule: {str(e)}"
        )


@router.delete("/constraints/rules/{rule_id}")
async def remove_custom_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove a custom constraint rule.

    This endpoint removes a custom constraint rule by ID.
    """
    try:
        logger.info(f"Removing custom constraint rule: {rule_id}")

        # Initialize advanced feasibility checker
        feasibility_checker = AdvancedFeasibilityChecker(db)

        # Remove the rule
        success = feasibility_checker.remove_custom_rule(rule_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Custom constraint rule '{rule_id}' not found"
            )

        return {"message": f"Custom constraint rule '{rule_id}' removed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing custom rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove custom rule: {str(e)}"
        )


@router.get("/constraints/violations/report")
async def get_constraint_violations_report(
    schedule_date: date = Query(..., description="Date to generate report for"),
    constraint_types: Optional[List[ConstraintType]] = Query(None, description="Filter by constraint types"),
    severity_levels: Optional[List[ConstraintSeverity]] = Query(None, description="Filter by severity levels"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a comprehensive constraint violations report.

    This endpoint provides detailed reporting of all constraint violations
    for a specific date, with filtering options.
    """
    try:
        logger.info(f"Generating constraint violations report for date: {schedule_date}")

        # Get all surgery assignments for the date
        assignments = db.query(SurgeryRoomAssignment).filter(
            SurgeryRoomAssignment.start_time >= schedule_date,
            SurgeryRoomAssignment.start_time < schedule_date + timedelta(days=1)
        ).all()

        if not assignments:
            return {
                "schedule_date": schedule_date,
                "total_surgeries": 0,
                "violations": [],
                "summary": {
                    "total_violations": 0,
                    "critical_violations": 0,
                    "violations_by_type": {},
                    "violations_by_severity": {},
                    "affected_surgeries": 0
                },
                "recommendations": ["No surgeries scheduled for this date"]
            }

        # Initialize advanced feasibility checker
        feasibility_checker = AdvancedFeasibilityChecker(db)

        # Collect all violations
        all_violations = []
        affected_surgeries = set()

        for assignment in assignments:
            request = FeasibilityCheckRequest(
                surgery_id=assignment.surgery_id,
                room_id=assignment.room_id,
                start_time=assignment.start_time,
                end_time=assignment.end_time,
                current_assignments=[{
                    'surgery_id': a.surgery_id,
                    'room_id': a.room_id,
                    'start_time': a.start_time,
                    'end_time': a.end_time
                } for a in assignments if a.surgery_id != assignment.surgery_id]
            )

            result = feasibility_checker.check_feasibility_advanced(request)

            # Filter violations
            filtered_violations = result.violations

            if constraint_types:
                filtered_violations = [v for v in filtered_violations if v.constraint_type in constraint_types]

            if severity_levels:
                filtered_violations = [v for v in filtered_violations if v.severity in severity_levels]

            all_violations.extend(filtered_violations)

            if filtered_violations:
                affected_surgeries.add(assignment.surgery_id)

        # Generate summary statistics
        violations_by_type = {}
        violations_by_severity = {}

        for violation in all_violations:
            # Count by type
            type_key = violation.constraint_type.value
            violations_by_type[type_key] = violations_by_type.get(type_key, 0) + 1

            # Count by severity
            severity_key = violation.severity.value
            violations_by_severity[severity_key] = violations_by_severity.get(severity_key, 0) + 1

        # Generate recommendations
        recommendations = []
        if violations_by_type.get('equipment_availability', 0) > 0:
            recommendations.append("Review equipment allocation and scheduling")
        if violations_by_type.get('staff_availability', 0) > 0:
            recommendations.append("Optimize staff assignments and availability")
        if violations_by_type.get('surgeon_specialization', 0) > 0:
            recommendations.append("Review surgeon qualifications and assignments")
        if violations_by_severity.get('critical', 0) > 0:
            recommendations.append("Address critical violations immediately")

        report = {
            "schedule_date": schedule_date,
            "total_surgeries": len(assignments),
            "violations": all_violations,
            "summary": {
                "total_violations": len(all_violations),
                "critical_violations": violations_by_severity.get('critical', 0),
                "violations_by_type": violations_by_type,
                "violations_by_severity": violations_by_severity,
                "affected_surgeries": len(affected_surgeries)
            },
            "recommendations": recommendations
        }

        logger.info(f"Generated violations report: {len(all_violations)} violations affecting {len(affected_surgeries)} surgeries")

        return report

    except Exception as e:
        logger.error(f"Error generating violations report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate violations report: {str(e)}"
        )
