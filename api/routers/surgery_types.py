"""
Surgery Types router for the FastAPI application.

This module provides API endpoints for surgery type management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_config import get_db
from models import SurgeryType as SurgeryTypeModel, User
from api.models import (
    SurgeryTypeCreate, 
    SurgeryType as SurgeryTypeResponse, 
    SurgeryTypeUpdate
)
from api.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=SurgeryTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_surgery_type(
    surgery_type: SurgeryTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new surgery type.

    Args:
        surgery_type: Surgery type data
        db: Database session
        current_user: Current authenticated user

    Returns:
        SurgeryType: Created surgery type

    Raises:
        HTTPException: If surgery type name already exists
    """
    try:
        db_surgery_type = SurgeryTypeModel(
            name=surgery_type.name,
            description=surgery_type.description,
            average_duration=surgery_type.average_duration
        )
        db.add(db_surgery_type)
        db.commit()
        db.refresh(db_surgery_type)
        return db_surgery_type
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Surgery type with name '{surgery_type.name}' already exists"
        )


@router.get("/", response_model=List[SurgeryTypeResponse])
async def read_surgery_types(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    name: Optional[str] = Query(None, description="Filter by surgery type name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve surgery types with optional filtering and pagination.

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        name: Optional name filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[SurgeryType]: List of surgery types
    """
    query = db.query(SurgeryTypeModel)
    
    if name:
        query = query.filter(SurgeryTypeModel.name.ilike(f"%{name}%"))
    
    surgery_types = query.offset(skip).limit(limit).all()
    return surgery_types


@router.get("/{surgery_type_id}", response_model=SurgeryTypeResponse)
async def read_surgery_type(
    surgery_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a specific surgery type by ID.

    Args:
        surgery_type_id: Surgery type ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        SurgeryType: Surgery type details

    Raises:
        HTTPException: If surgery type not found
    """
    surgery_type = db.query(SurgeryTypeModel).filter(
        SurgeryTypeModel.type_id == surgery_type_id
    ).first()
    
    if surgery_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Surgery type with ID {surgery_type_id} not found"
        )
    
    return surgery_type


@router.put("/{surgery_type_id}", response_model=SurgeryTypeResponse)
async def update_surgery_type(
    surgery_type_id: int,
    surgery_type: SurgeryTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a surgery type.

    Args:
        surgery_type_id: Surgery type ID
        surgery_type: Updated surgery type data
        db: Database session
        current_user: Current authenticated user

    Returns:
        SurgeryType: Updated surgery type

    Raises:
        HTTPException: If surgery type not found or name already exists
    """
    db_surgery_type = db.query(SurgeryTypeModel).filter(
        SurgeryTypeModel.type_id == surgery_type_id
    ).first()
    
    if db_surgery_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Surgery type with ID {surgery_type_id} not found"
        )
    
    try:
        update_data = surgery_type.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_surgery_type, field, value)
        
        db.commit()
        db.refresh(db_surgery_type)
        return db_surgery_type
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Surgery type with name '{surgery_type.name}' already exists"
        )


@router.delete("/{surgery_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_surgery_type(
    surgery_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a surgery type.

    Args:
        surgery_type_id: Surgery type ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If surgery type not found or has associated surgeries
    """
    db_surgery_type = db.query(SurgeryTypeModel).filter(
        SurgeryTypeModel.type_id == surgery_type_id
    ).first()
    
    if db_surgery_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Surgery type with ID {surgery_type_id} not found"
        )
    
    # Check if surgery type has associated surgeries
    if db_surgery_type.surgeries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete surgery type with associated surgeries"
        )
    
    try:
        db.delete(db_surgery_type)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete surgery type due to existing references"
        )
