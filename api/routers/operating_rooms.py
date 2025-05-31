"""
Operating rooms router for the FastAPI application.

This module provides API endpoints for operating room management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_config import get_db
from models import OperatingRoom, User
from api.models import OperatingRoomCreate, OperatingRoom as OperatingRoomResponse, OperatingRoomUpdate
from api.auth import get_current_active_user
from services.operating_room_service import OperatingRoomService

router = APIRouter()


@router.post("/", response_model=OperatingRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_operating_room(
    operating_room: OperatingRoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new operating room.

    Args:
        operating_room: Operating room data
        db: Database session
        current_user: Current authenticated user

    Returns:
        OperatingRoom: Created operating room
    """
    db_operating_room = OperatingRoom(location=operating_room.location)

    try:
        db.add(db_operating_room)
        db.commit()
        db.refresh(db_operating_room)
        return db_operating_room
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating operating room"
        )


@router.get("/", response_model=List[OperatingRoomResponse])
async def read_operating_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all operating rooms.

    Args:
        skip: Number of operating rooms to skip
        limit: Maximum number of operating rooms to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[OperatingRoom]: List of operating rooms
    """
    operating_rooms = OperatingRoomService.get_all_operating_rooms(db, skip=skip, limit=limit)
    return operating_rooms


@router.get("/{room_id}", response_model=OperatingRoomResponse)
async def read_operating_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get operating room by ID.

    Args:
        room_id: Operating room ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        OperatingRoom: Operating room with specified ID

    Raises:
        HTTPException: If operating room not found
    """
    operating_room = db.query(OperatingRoom).filter(OperatingRoom.room_id == room_id).first()
    if operating_room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operating room not found"
        )
    return operating_room


@router.put("/{room_id}", response_model=OperatingRoomResponse)
async def update_operating_room(
    room_id: int,
    operating_room: OperatingRoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update operating room.

    Args:
        room_id: Operating room ID
        operating_room: Operating room data to update
        db: Database session
        current_user: Current authenticated user

    Returns:
        OperatingRoom: Updated operating room

    Raises:
        HTTPException: If operating room not found
    """
    db_operating_room = db.query(OperatingRoom).filter(OperatingRoom.room_id == room_id).first()
    if db_operating_room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operating room not found"
        )

    # Update operating room fields
    update_data = operating_room.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_operating_room, key, value)

    try:
        db.commit()
        db.refresh(db_operating_room)
        return db_operating_room
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating operating room"
        )


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_operating_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete operating room.

    Args:
        room_id: Operating room ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If operating room not found
    """
    db_operating_room = db.query(OperatingRoom).filter(OperatingRoom.room_id == room_id).first()
    if db_operating_room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operating room not found"
        )

    db.delete(db_operating_room)
    db.commit()
    return None
