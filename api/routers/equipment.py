from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api import models, schemas
from services.operating_room_equipment_service import OperatingRoomEquipmentService
from db_config import get_db

router = APIRouter(
    prefix="/equipment",
    tags=["Equipment"],
    responses={404: {"description": "Not found"}},
)

from api.auth import get_current_active_user # Added import
from models import User # Added import

@router.post("", response_model=schemas.Equipment, status_code=status.HTTP_201_CREATED)
def create_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Create new equipment."""
    db_equipment = OperatingRoomEquipmentService.create_operating_room_equipment(db, equipment.dict())
    return db_equipment

@router.get("", response_model=List[schemas.Equipment])
def read_equipment(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Retrieve a list of all equipment."""
    equipment = OperatingRoomEquipmentService.get_equipment(db, skip=skip, limit=limit)
    return equipment

@router.get("/{equipment_id}", response_model=schemas.Equipment)
def read_equipment_by_id(equipment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Retrieve equipment by its ID."""
    db_equipment = OperatingRoomEquipmentService.get_operating_room_equipment(db, equipment_id)
    if db_equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return db_equipment

@router.put("/{equipment_id}", response_model=schemas.Equipment)
def update_equipment(equipment_id: int, equipment: schemas.EquipmentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Update existing equipment."""
    success = OperatingRoomEquipmentService.update_operating_room_equipment(db, equipment_id, equipment.dict(exclude_unset=True))
    if not success:
        raise HTTPException(status_code=404, detail="Equipment not found")
    # Return the updated equipment
    db_equipment = OperatingRoomEquipmentService.get_operating_room_equipment(db, equipment_id)
    return db_equipment

@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment(equipment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete equipment by its ID."""
    success = OperatingRoomEquipmentService.delete_operating_room_equipment(db, equipment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return {"message": "Equipment deleted successfully"}