"""
Surgeons router for the FastAPI application.

This module provides API endpoints for surgeon management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_config import get_db
from models import Surgeon, User
from api.models import SurgeonCreate, Surgeon as SurgeonResponse, SurgeonUpdate
from api.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=SurgeonResponse, status_code=status.HTTP_201_CREATED)
async def create_surgeon(
    surgeon: SurgeonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new surgeon.

    Args:
        surgeon: Surgeon data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Surgeon: Created surgeon
    """
    db_surgeon = Surgeon(
        name=surgeon.name,
        contact_info=surgeon.contact_info,
        specialization=surgeon.specialization,
        credentials=surgeon.credentials,
        availability=surgeon.availability
    )

    try:
        db.add(db_surgeon)
        db.commit()
        db.refresh(db_surgeon)
        return db_surgeon
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating surgeon"
        )


@router.get("/", response_model=List[SurgeonResponse])
async def read_surgeons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all surgeons.

    Args:
        skip: Number of surgeons to skip
        limit: Maximum number of surgeons to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[Surgeon]: List of surgeons
    """
    surgeons = db.query(Surgeon).offset(skip).limit(limit).all()
    return surgeons


@router.get("/{surgeon_id}", response_model=SurgeonResponse)
async def read_surgeon(
    surgeon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get surgeon by ID.

    Args:
        surgeon_id: Surgeon ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Surgeon: Surgeon with specified ID

    Raises:
        HTTPException: If surgeon not found
    """
    surgeon = db.query(Surgeon).filter(Surgeon.surgeon_id == surgeon_id).first()
    if surgeon is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surgeon not found"
        )
    return surgeon


@router.put("/{surgeon_id}", response_model=SurgeonResponse)
async def update_surgeon(
    surgeon_id: int,
    surgeon: SurgeonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update surgeon.

    Args:
        surgeon_id: Surgeon ID
        surgeon: Surgeon data to update
        db: Database session
        current_user: Current authenticated user

    Returns:
        Surgeon: Updated surgeon

    Raises:
        HTTPException: If surgeon not found
    """
    db_surgeon = db.query(Surgeon).filter(Surgeon.surgeon_id == surgeon_id).first()
    if db_surgeon is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surgeon not found"
        )

    # Update surgeon fields
    update_data = surgeon.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_surgeon, key, value)

    try:
        db.commit()
        db.refresh(db_surgeon)
        return db_surgeon
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating surgeon"
        )


@router.delete("/{surgeon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_surgeon(
    surgeon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete surgeon.

    Args:
        surgeon_id: Surgeon ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If surgeon not found
    """
    db_surgeon = db.query(Surgeon).filter(Surgeon.surgeon_id == surgeon_id).first()
    if db_surgeon is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surgeon not found"
        )

    db.delete(db_surgeon)
    db.commit()
    return None
