"""
Schedules router for the FastAPI application.

This module provides API endpoints for schedule optimization.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db_config import get_db
from models import Surgery, SurgeryRoomAssignment, OperatingRoom, Surgeon, User
from api.auth import get_current_active_user
from tabu_optimizer import TabuOptimizer
from solution_evaluator import SolutionEvaluator

router = APIRouter()


class OptimizationParameters(BaseModel):
    """Model for optimization parameters."""
    date: Optional[date] = None
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

    class Config:
        orm_mode = True


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
        if params.date:
            query = query.filter(Surgery.scheduled_date == params.date)
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
            weights=params.weights
        )
        
        # Run optimization
        solution = optimizer.optimize()
        
        # Evaluate solution
        evaluator = SolutionEvaluator(db_session=db)
        score, metrics = evaluator.evaluate(solution)
        
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
            iteration_count=optimizer.iteration_count,
            execution_time_seconds=optimizer.execution_time
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


@router.get("/current", response_model=List[SurgeryAssignment])
async def get_current_schedule(
    date: Optional[date] = Query(None, description="Filter by date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current schedule.

    Args:
        date: Filter by date
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[SurgeryAssignment]: Current schedule
    """
    query = db.query(Surgery).filter(Surgery.room_id.isnot(None))
    
    if date:
        query = query.filter(Surgery.scheduled_date == date)
    
    surgeries = query.all()
    
    assignments = []
    for surgery in surgeries:
        assignments.append(SurgeryAssignment(
            surgery_id=surgery.surgery_id,
            room_id=surgery.room_id,
            start_time=surgery.start_time,
            end_time=surgery.end_time,
            surgeon_id=surgery.surgeon_id,
            patient_id=surgery.patient_id,
            duration_minutes=surgery.duration_minutes,
            surgery_type_id=surgery.surgery_type_id
        ))
    
    return assignments
