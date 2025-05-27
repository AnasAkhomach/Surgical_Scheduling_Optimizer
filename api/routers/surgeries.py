"""
Surgeries router for the FastAPI application.

This module provides API endpoints for surgery management.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_config import get_db
from models import Surgery, SurgeryType, Surgeon, Patient, OperatingRoom, User
from api.models import SurgeryCreate, Surgery as SurgeryResponse, SurgeryUpdate
from api.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=SurgeryResponse, status_code=status.HTTP_201_CREATED)
async def create_surgery(
    surgery: SurgeryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new surgery.

    Args:
        surgery: Surgery data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Surgery: Created surgery

    Raises:
        HTTPException: If surgery type, surgeon, patient, or room not found
    """
    # Validate surgery type
    surgery_type = db.query(SurgeryType).filter(SurgeryType.type_id == surgery.surgery_type_id).first()
    if not surgery_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Surgery type with ID {surgery.surgery_type_id} not found"
        )

    # Validate surgeon if provided
    if surgery.surgeon_id:
        surgeon = db.query(Surgeon).filter(Surgeon.surgeon_id == surgery.surgeon_id).first()
        if not surgeon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Surgeon with ID {surgery.surgeon_id} not found"
            )

    # Validate patient if provided
    if surgery.patient_id:
        patient = db.query(Patient).filter(Patient.patient_id == surgery.patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {surgery.patient_id} not found"
            )

    # Validate room if provided
    if surgery.room_id:
        room = db.query(OperatingRoom).filter(OperatingRoom.room_id == surgery.room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Operating room with ID {surgery.room_id} not found"
            )

    # Create new surgery
    db_surgery = Surgery(
        scheduled_date=datetime.now(),  # Default to current date
        surgery_type_id=surgery.surgery_type_id,
        urgency_level=surgery.urgency_level,
        duration_minutes=surgery.duration_minutes,
        status=surgery.status,
        start_time=surgery.start_time,
        end_time=surgery.end_time,
        patient_id=surgery.patient_id,
        surgeon_id=surgery.surgeon_id,
        room_id=surgery.room_id
    )

    try:
        db.add(db_surgery)
        db.commit()
        db.refresh(db_surgery)
        return db_surgery
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating surgery: {str(e)}"
        )


@router.get("/", response_model=List[SurgeryResponse])
async def read_surgeries(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by surgery status"),
    surgeon_id: Optional[int] = Query(None, description="Filter by surgeon ID"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all surgeries with optional filtering.

    Args:
        skip: Number of surgeries to skip
        limit: Maximum number of surgeries to return
        status: Filter by surgery status
        surgeon_id: Filter by surgeon ID
        patient_id: Filter by patient ID
        room_id: Filter by room ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[Surgery]: List of surgeries
    """
    query = db.query(Surgery)

    # Apply filters if provided
    if status:
        query = query.filter(Surgery.status == status)
    if surgeon_id:
        query = query.filter(Surgery.surgeon_id == surgeon_id)
    if patient_id:
        query = query.filter(Surgery.patient_id == patient_id)
    if room_id:
        query = query.filter(Surgery.room_id == room_id)

    surgeries = query.offset(skip).limit(limit).all()
    return surgeries


@router.get("/{surgery_id}", response_model=SurgeryResponse)
async def read_surgery(
    surgery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get surgery by ID.

    Args:
        surgery_id: Surgery ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Surgery: Surgery with specified ID

    Raises:
        HTTPException: If surgery not found
    """
    surgery = db.query(Surgery).filter(Surgery.surgery_id == surgery_id).first()
    if surgery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surgery not found"
        )
    return surgery


@router.put("/{surgery_id}", response_model=SurgeryResponse)
async def update_surgery(
    surgery_id: int,
    surgery: SurgeryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update surgery.

    Args:
        surgery_id: Surgery ID
        surgery: Surgery data to update
        db: Database session
        current_user: Current authenticated user

    Returns:
        Surgery: Updated surgery

    Raises:
        HTTPException: If surgery not found
    """
    db_surgery = db.query(Surgery).filter(Surgery.surgery_id == surgery_id).first()
    if db_surgery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surgery not found"
        )

    # Update surgery fields
    update_data = surgery.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_surgery, key, value)

    try:
        db.commit()
        db.refresh(db_surgery)
        return db_surgery
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating surgery: {str(e)}"
        )


@router.delete("/{surgery_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_surgery(
    surgery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete surgery.

    Args:
        surgery_id: Surgery ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If surgery not found
    """
    db_surgery = db.query(Surgery).filter(Surgery.surgery_id == surgery_id).first()
    if db_surgery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surgery not found"
        )

    db.delete(db_surgery)
    db.commit()
    return None
