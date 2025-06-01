from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime # Moved import to the top

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

# Surgery Schemas
class SurgeryBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    urgency: Optional[str] = None # Consider Enum for specific values
    special_requirements: Optional[List[str]] = None
    status: Optional[str] = None # Consider Enum for specific values
    surgeon_id: int
    patient_id: int
    surgery_type_id: Optional[int] = None

class SurgeryCreate(SurgeryBase):
    pass

class Surgery(SurgeryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SurgeryDetail(Surgery):
    surgeon_name: Optional[str] = None
    patient_name: Optional[str] = None
    assigned_room_id: Optional[int] = None
    assigned_room_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

# Schedule Schemas
class ScheduleBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = None # Consider Enum for specific values

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ScheduleResponse(Schedule):
    surgeries: List[SurgeryDetail] = []