"""
Pydantic models for the FastAPI application.

This module provides Pydantic models for request and response validation.
"""

from datetime import datetime, date
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr


class SurgeryStatus(str, Enum):
    """Enum for surgery status."""
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class AppointmentStatus(str, Enum):
    """Enum for appointment status."""
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class UrgencyLevel(str, Enum):
    """Enum for surgery urgency level."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EMERGENCY = "Emergency"


# Base models (for shared attributes)
class PatientBase(BaseModel):
    """Base model for patient data."""
    name: str
    dob: date
    contact_info: Optional[str] = None
    privacy_consent: bool = False


class SurgeonBase(BaseModel):
    """Base model for surgeon data."""
    name: str
    contact_info: Optional[str] = None
    specialization: str
    credentials: str
    availability: bool = True


class StaffBase(BaseModel):
    """Base model for staff data."""
    name: str
    role: str
    contact_info: Optional[str] = None
    specialization: Optional[str] = None
    availability: bool = True


class OperatingRoomBase(BaseModel):
    """Base model for operating room data."""
    location: str


class SurgeryBase(BaseModel):
    """Base model for surgery data."""
    surgery_type_id: int
    duration_minutes: int
    urgency_level: UrgencyLevel = UrgencyLevel.MEDIUM
    patient_id: Optional[int] = None
    surgeon_id: Optional[int] = None
    room_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: SurgeryStatus = SurgeryStatus.SCHEDULED


class SurgeryTypeBase(BaseModel):
    """Base model for surgery type data."""
    name: str
    description: Optional[str] = None
    average_duration: int


class AppointmentBase(BaseModel):
    """Base model for appointment data."""
    patient_id: int
    surgeon_id: int
    room_id: Optional[int] = None
    appointment_date: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None


class UserBase(BaseModel):
    """Base model for user data."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    staff_id: Optional[int] = None


# Create models (for request payloads)
class PatientCreate(PatientBase):
    """Model for creating a patient."""
    pass


class SurgeonCreate(SurgeonBase):
    """Model for creating a surgeon."""
    pass


class StaffCreate(StaffBase):
    """Model for creating a staff member."""
    pass


class OperatingRoomCreate(OperatingRoomBase):
    """Model for creating an operating room."""
    pass


class SurgeryCreate(SurgeryBase):
    """Model for creating a surgery."""
    pass


class SurgeryTypeCreate(SurgeryTypeBase):
    """Model for creating a surgery type."""
    pass


class AppointmentCreate(AppointmentBase):
    """Model for creating an appointment."""
    pass


class UserCreate(UserBase):
    """Model for creating a user."""
    password: str


# Response models (for API responses)
class Patient(PatientBase):
    """Model for patient response."""
    patient_id: int

    class Config:
        orm_mode = True


class Surgeon(SurgeonBase):
    """Model for surgeon response."""
    surgeon_id: int

    class Config:
        orm_mode = True


class Staff(StaffBase):
    """Model for staff response."""
    staff_id: int

    class Config:
        orm_mode = True


class OperatingRoom(OperatingRoomBase):
    """Model for operating room response."""
    room_id: int

    class Config:
        orm_mode = True


class SurgeryType(SurgeryTypeBase):
    """Model for surgery type response."""
    surgery_type_id: int

    class Config:
        orm_mode = True


class Surgery(SurgeryBase):
    """Model for surgery response."""
    surgery_id: int

    class Config:
        orm_mode = True


class Appointment(AppointmentBase):
    """Model for appointment response."""
    appointment_id: int

    class Config:
        orm_mode = True


class User(UserBase):
    """Model for user response."""
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


# Authentication models
class Token(BaseModel):
    """Model for authentication token."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Model for token data."""
    username: Optional[str] = None
    role: Optional[str] = None


# Update models (for partial updates)
class PatientUpdate(BaseModel):
    """Model for updating a patient."""
    name: Optional[str] = None
    contact_info: Optional[str] = None
    privacy_consent: Optional[bool] = None


class SurgeonUpdate(BaseModel):
    """Model for updating a surgeon."""
    name: Optional[str] = None
    contact_info: Optional[str] = None
    specialization: Optional[str] = None
    credentials: Optional[str] = None
    availability: Optional[bool] = None


class StaffUpdate(BaseModel):
    """Model for updating a staff member."""
    name: Optional[str] = None
    role: Optional[str] = None
    contact_info: Optional[str] = None
    specialization: Optional[str] = None
    availability: Optional[bool] = None


class OperatingRoomUpdate(BaseModel):
    """Model for updating an operating room."""
    location: Optional[str] = None


class SurgeryUpdate(BaseModel):
    """Model for updating a surgery."""
    surgery_type_id: Optional[int] = None
    duration_minutes: Optional[int] = None
    urgency_level: Optional[UrgencyLevel] = None
    patient_id: Optional[int] = None
    surgeon_id: Optional[int] = None
    room_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[SurgeryStatus] = None


class UserUpdate(BaseModel):
    """Model for updating a user."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    staff_id: Optional[int] = None
    is_active: Optional[bool] = None
