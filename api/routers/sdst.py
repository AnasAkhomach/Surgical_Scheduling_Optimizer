"""
SDST (Sequence-Dependent Setup Time) router for the FastAPI application.

This module provides API endpoints for sequence-dependent setup time management.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_config import get_db
from models import (
    SequenceDependentSetupTime as SDSTModel,
    SurgeryType as SurgeryTypeModel,
    User
)
from api.models import (
    SequenceDependentSetupTimeCreate,
    SequenceDependentSetupTime as SDSTResponse,
    SequenceDependentSetupTimeUpdate,
    BulkSDSTImport,
    BulkSDSTExport,
    SDSTMatrix,
    SurgeryType as SurgeryTypeResponse
)
from api.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=SDSTResponse, status_code=status.HTTP_201_CREATED)
async def create_sdst(
    sdst: SequenceDependentSetupTimeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new sequence-dependent setup time.

    Args:
        sdst: SDST data
        db: Database session
        current_user: Current authenticated user

    Returns:
        SequenceDependentSetupTime: Created SDST

    Raises:
        HTTPException: If surgery types not found or SDST already exists
    """
    # Validate surgery types exist
    from_type = db.query(SurgeryTypeModel).filter(
        SurgeryTypeModel.type_id == sdst.from_surgery_type_id
    ).first()
    if not from_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"From surgery type with ID {sdst.from_surgery_type_id} not found"
        )

    to_type = db.query(SurgeryTypeModel).filter(
        SurgeryTypeModel.type_id == sdst.to_surgery_type_id
    ).first()
    if not to_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"To surgery type with ID {sdst.to_surgery_type_id} not found"
        )

    # Check if SDST already exists for this combination
    existing_sdst = db.query(SDSTModel).filter(
        SDSTModel.from_surgery_type_id == sdst.from_surgery_type_id,
        SDSTModel.to_surgery_type_id == sdst.to_surgery_type_id
    ).first()

    if existing_sdst:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SDST already exists for transition from type {sdst.from_surgery_type_id} to {sdst.to_surgery_type_id}"
        )

    try:
        db_sdst = SDSTModel(
            from_surgery_type_id=sdst.from_surgery_type_id,
            to_surgery_type_id=sdst.to_surgery_type_id,
            setup_time_minutes=sdst.setup_time_minutes
        )
        db.add(db_sdst)
        db.commit()
        db.refresh(db_sdst)
        return db_sdst
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create SDST due to database constraint violation"
        )


@router.get("/", response_model=List[SDSTResponse])
async def read_sdst_list(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    from_surgery_type_id: Optional[int] = Query(None, description="Filter by from surgery type ID"),
    to_surgery_type_id: Optional[int] = Query(None, description="Filter by to surgery type ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve SDST records with optional filtering and pagination.

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        from_surgery_type_id: Optional from surgery type filter
        to_surgery_type_id: Optional to surgery type filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[SequenceDependentSetupTime]: List of SDST records
    """
    query = db.query(SDSTModel)

    if from_surgery_type_id:
        query = query.filter(SDSTModel.from_surgery_type_id == from_surgery_type_id)

    if to_surgery_type_id:
        query = query.filter(SDSTModel.to_surgery_type_id == to_surgery_type_id)

    sdst_records = query.offset(skip).limit(limit).all()
    return sdst_records


@router.get("/matrix", response_model=SDSTMatrix)
async def get_sdst_matrix(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve SDST data as a matrix representation.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        SDSTMatrix: Matrix representation of SDST data
    """
    # Get all surgery types
    surgery_types = db.query(SurgeryTypeModel).all()

    # Get all SDST records
    setup_times = db.query(SDSTModel).all()

    # Build matrix
    matrix = {}
    for from_type in surgery_types:
        matrix[str(from_type.type_id)] = {}
        for to_type in surgery_types:
            matrix[str(from_type.type_id)][str(to_type.type_id)] = 0

    # Fill in actual setup times
    for sdst in setup_times:
        matrix[str(sdst.from_surgery_type_id)][str(sdst.to_surgery_type_id)] = sdst.setup_time_minutes

    # Convert SQLAlchemy models to Pydantic models
    surgery_types_pydantic = [SurgeryTypeResponse.model_validate(st) for st in surgery_types]
    setup_times_pydantic = [SDSTResponse.model_validate(st) for st in setup_times]

    return SDSTMatrix(
        surgery_types=surgery_types_pydantic,
        setup_times=setup_times_pydantic,
        matrix=matrix
    )


@router.get("/{sdst_id}", response_model=SDSTResponse)
async def read_sdst(
    sdst_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a specific SDST record by ID.

    Args:
        sdst_id: SDST ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        SequenceDependentSetupTime: SDST details

    Raises:
        HTTPException: If SDST not found
    """
    sdst = db.query(SDSTModel).filter(SDSTModel.id == sdst_id).first()

    if sdst is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SDST with ID {sdst_id} not found"
        )

    return sdst


@router.put("/{sdst_id}", response_model=SDSTResponse)
async def update_sdst(
    sdst_id: int,
    sdst: SequenceDependentSetupTimeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an SDST record.

    Args:
        sdst_id: SDST ID
        sdst: Updated SDST data
        db: Database session
        current_user: Current authenticated user

    Returns:
        SequenceDependentSetupTime: Updated SDST

    Raises:
        HTTPException: If SDST not found or surgery types not found
    """
    db_sdst = db.query(SDSTModel).filter(SDSTModel.id == sdst_id).first()

    if db_sdst is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SDST with ID {sdst_id} not found"
        )

    # Validate surgery types if they are being updated
    update_data = sdst.model_dump(exclude_unset=True)

    if 'from_surgery_type_id' in update_data:
        from_type = db.query(SurgeryTypeModel).filter(
            SurgeryTypeModel.type_id == update_data['from_surgery_type_id']
        ).first()
        if not from_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"From surgery type with ID {update_data['from_surgery_type_id']} not found"
            )

    if 'to_surgery_type_id' in update_data:
        to_type = db.query(SurgeryTypeModel).filter(
            SurgeryTypeModel.type_id == update_data['to_surgery_type_id']
        ).first()
        if not to_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"To surgery type with ID {update_data['to_surgery_type_id']} not found"
            )

    try:
        for field, value in update_data.items():
            setattr(db_sdst, field, value)

        db.commit()
        db.refresh(db_sdst)
        return db_sdst
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update SDST due to database constraint violation"
        )


@router.delete("/{sdst_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sdst(
    sdst_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an SDST record.

    Args:
        sdst_id: SDST ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If SDST not found
    """
    db_sdst = db.query(SDSTModel).filter(SDSTModel.id == sdst_id).first()

    if db_sdst is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SDST with ID {sdst_id} not found"
        )

    try:
        db.delete(db_sdst)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete SDST due to database constraint violation"
        )


@router.post("/bulk/import", response_model=Dict[str, Any])
async def bulk_import_sdst(
    bulk_data: BulkSDSTImport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Bulk import SDST data.

    Args:
        bulk_data: Bulk SDST import data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dict: Import results summary

    Raises:
        HTTPException: If validation fails
    """
    created_count = 0
    updated_count = 0
    errors = []

    for i, sdst_data in enumerate(bulk_data.sdst_data):
        try:
            # Validate surgery types exist
            from_type = db.query(SurgeryTypeModel).filter(
                SurgeryTypeModel.type_id == sdst_data.from_surgery_type_id
            ).first()
            if not from_type:
                errors.append(f"Row {i+1}: From surgery type {sdst_data.from_surgery_type_id} not found")
                continue

            to_type = db.query(SurgeryTypeModel).filter(
                SurgeryTypeModel.type_id == sdst_data.to_surgery_type_id
            ).first()
            if not to_type:
                errors.append(f"Row {i+1}: To surgery type {sdst_data.to_surgery_type_id} not found")
                continue

            # Check if SDST already exists
            existing_sdst = db.query(SDSTModel).filter(
                SDSTModel.from_surgery_type_id == sdst_data.from_surgery_type_id,
                SDSTModel.to_surgery_type_id == sdst_data.to_surgery_type_id
            ).first()

            if existing_sdst:
                if bulk_data.overwrite_existing:
                    existing_sdst.setup_time_minutes = sdst_data.setup_time_minutes
                    updated_count += 1
                else:
                    errors.append(f"Row {i+1}: SDST already exists for transition {sdst_data.from_surgery_type_id} -> {sdst_data.to_surgery_type_id}")
                    continue
            else:
                new_sdst = SDSTModel(
                    from_surgery_type_id=sdst_data.from_surgery_type_id,
                    to_surgery_type_id=sdst_data.to_surgery_type_id,
                    setup_time_minutes=sdst_data.setup_time_minutes
                )
                db.add(new_sdst)
                created_count += 1

        except Exception as e:
            errors.append(f"Row {i+1}: {str(e)}")

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bulk import failed: {str(e)}"
        )

    return {
        "created_count": created_count,
        "updated_count": updated_count,
        "error_count": len(errors),
        "errors": errors
    }


@router.post("/bulk/export", response_model=List[SDSTResponse])
async def bulk_export_sdst(
    export_params: BulkSDSTExport = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Bulk export SDST data.

    Args:
        export_params: Export parameters
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[SequenceDependentSetupTime]: Exported SDST data
    """
    query = db.query(SDSTModel)

    if export_params.surgery_type_ids:
        query = query.filter(
            (SDSTModel.from_surgery_type_id.in_(export_params.surgery_type_ids)) |
            (SDSTModel.to_surgery_type_id.in_(export_params.surgery_type_ids))
        )

    return query.all()
