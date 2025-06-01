"""
Staff router for the FastAPI application.

This module provides API endpoints for staff management.
"""

import json # Added for specializations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_config import get_db
from models import Staff, User # SQLAlchemy model
from api.models import StaffCreate, StaffUpdate # Pydantic models
from api.models import Staff as StaffResponse # Pydantic response model
from api.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
async def create_staff(
    staff: StaffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new staff member.

    Args:
        staff: Staff data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Staff: Created staff member
    """
    db_staff = Staff(
        name=staff.name,
        role=staff.role,
        contact_info=staff.contact_info,
        specializations=json.dumps(staff.specializations) if staff.specializations is not None else None, # Updated for specializations list
        status=staff.status, # Added status
        availability=staff.availability
    )

    try:
        db.add(db_staff)
        db.commit()
        db.refresh(db_staff)
        return db_staff
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating staff member"
        )


@router.get("/", response_model=List[StaffResponse])
async def read_staff(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all staff members.

    Args:
        skip: Number of staff members to skip
        limit: Maximum number of staff members to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[Staff]: List of staff members
    """
    staff = db.query(Staff).offset(skip).limit(limit).all()
    return staff


@router.get("/{staff_id}", response_model=StaffResponse)
async def read_staff_member(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get staff member by ID.

    Args:
        staff_id: Staff ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Staff: Staff member with specified ID

    Raises:
        HTTPException: If staff member not found
    """
    staff = db.query(Staff).filter(Staff.staff_id == staff_id).first()
    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    return staff


@router.put("/{staff_id}", response_model=StaffResponse)
async def update_staff(
    staff_id: int,
    staff: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update staff member.

    Args:
        staff_id: Staff ID
        staff: Staff data to update
        db: Database session
        current_user: Current authenticated user

    Returns:
        Staff: Updated staff member

    Raises:
        HTTPException: If staff member not found
    """
    db_staff = db.query(Staff).filter(Staff.staff_id == staff_id).first()
    if db_staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    # Update staff fields
    update_data = staff.model_dump(exclude_unset=True) # Changed to model_dump for Pydantic v2
    if 'specializations' in update_data and update_data['specializations'] is not None:
        update_data['specializations'] = json.dumps(update_data['specializations'])
    elif 'specializations' in update_data and update_data['specializations'] is None:
        # Explicitly set to None if provided as None, otherwise it might be excluded by exclude_unset=True
        # and not updated if the Pydantic model field has a default_factory=list
        pass # Let setattr handle it if key is present

    for key, value in update_data.items():
        setattr(db_staff, key, value)

    try:
        db.commit()
        db.refresh(db_staff)
        return db_staff
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating staff member"
        )


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete staff member.

    Args:
        staff_id: Staff ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If staff member not found
    """
    db_staff = db.query(Staff).filter(Staff.staff_id == staff_id).first()
    if db_staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    db.delete(db_staff)
    db.commit()
    return None
