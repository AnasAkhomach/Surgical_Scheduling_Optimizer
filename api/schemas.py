from pydantic import BaseModel
from typing import Optional, List

# Equipment Schemas
class EquipmentBase(BaseModel):
    name: str
    type: str
    status: str
    location: str

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(EquipmentBase):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None

class Equipment(EquipmentBase):
    equipment_id: int

    class Config:
        from_attributes = True