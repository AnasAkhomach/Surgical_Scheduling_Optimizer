from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api import models, schemas
from services import operating_room_equipment_service
from db_config import get_db

router = APIRouter(
    prefix="/equipment",
    tags=["Equipment"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Equipment, status_code=status.HTTP_201_CREATED)
def create_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db)):
    """Create new equipment."""
    db_equipment = operating_room_equipment_service.create_equipment(db, equipment)
    return db_equipment

@router.get("/", response_model=List[schemas.Equipment])
def read_equipment(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a list of all equipment."""
    equipment = operating_room_equipment_service.get_equipment(db, skip=skip, limit=limit)
    return equipment

@router.get("/{equipment_id}", response_model=schemas.Equipment)
def read_equipment_by_id(equipment_id: int, db: Session = Depends(get_db)):
    """Retrieve equipment by its ID."""
    db_equipment = operating_room_equipment_service.get_equipment_by_id(db, equipment_id)
    if db_equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return db_equipment

@router.put("/{equipment_id}", response_model=schemas.Equipment)
def update_equipment(equipment_id: int, equipment: schemas.EquipmentUpdate, db: Session = Depends(get_db)):
    """Update existing equipment."""
    db_equipment = operating_room_equipment_service.update_equipment(db, equipment_id, equipment)
    if db_equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return db_equipment

@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """Delete equipment by its ID."""
    success = operating_room_equipment_service.delete_equipment(db, equipment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return {"message": "Equipment deleted successfully"}