"""
Appointments router for the FastAPI application.

This module provides API endpoints for appointment management.
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_config import get_db
from models import SurgeryAppointment, Patient, Surgeon, OperatingRoom, User
from api.models import AppointmentCreate, Appointment as AppointmentResponse
from api.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new appointment.

    Args:
        appointment: Appointment data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Appointment: Created appointment

    Raises:
        HTTPException: If patient, surgeon, or room not found
    """
    # Validate patient
    patient = db.query(Patient).filter(Patient.patient_id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {appointment.patient_id} not found"
        )
    
    # Validate surgeon
    surgeon = db.query(Surgeon).filter(Surgeon.surgeon_id == appointment.surgeon_id).first()
    if not surgeon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Surgeon with ID {appointment.surgeon_id} not found"
        )
    
    # Validate room if provided
    if appointment.room_id:
        room = db.query(OperatingRoom).filter(OperatingRoom.room_id == appointment.room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Operating room with ID {appointment.room_id} not found"
            )
    
    # Create new appointment
    db_appointment = SurgeryAppointment(
        patient_id=appointment.patient_id,
        surgeon_id=appointment.surgeon_id,
        room_id=appointment.room_id,
        appointment_date=appointment.appointment_date,
        status=appointment.status,
        notes=appointment.notes
    )
    
    try:
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating appointment: {str(e)}"
        )


@router.get("/", response_model=List[AppointmentResponse])
async def read_appointments(
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    surgeon_id: Optional[int] = Query(None, description="Filter by surgeon ID"),
    status: Optional[str] = Query(None, description="Filter by appointment status"),
    date_from: Optional[date] = Query(None, description="Filter by date (from)"),
    date_to: Optional[date] = Query(None, description="Filter by date (to)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all appointments with optional filtering.

    Args:
        skip: Number of appointments to skip
        limit: Maximum number of appointments to return
        patient_id: Filter by patient ID
        surgeon_id: Filter by surgeon ID
        status: Filter by appointment status
        date_from: Filter by date (from)
        date_to: Filter by date (to)
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[Appointment]: List of appointments
    """
    query = db.query(SurgeryAppointment)
    
    # Apply filters if provided
    if patient_id:
        query = query.filter(SurgeryAppointment.patient_id == patient_id)
    if surgeon_id:
        query = query.filter(SurgeryAppointment.surgeon_id == surgeon_id)
    if status:
        query = query.filter(SurgeryAppointment.status == status)
    if date_from:
        query = query.filter(SurgeryAppointment.appointment_date >= date_from)
    if date_to:
        query = query.filter(SurgeryAppointment.appointment_date <= date_to)
    
    appointments = query.offset(skip).limit(limit).all()
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def read_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get appointment by ID.

    Args:
        appointment_id: Appointment ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Appointment: Appointment with specified ID

    Raises:
        HTTPException: If appointment not found
    """
    appointment = db.query(SurgeryAppointment).filter(SurgeryAppointment.appointment_id == appointment_id).first()
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update appointment.

    Args:
        appointment_id: Appointment ID
        appointment: Appointment data to update
        db: Database session
        current_user: Current authenticated user

    Returns:
        Appointment: Updated appointment

    Raises:
        HTTPException: If appointment not found
    """
    db_appointment = db.query(SurgeryAppointment).filter(SurgeryAppointment.appointment_id == appointment_id).first()
    if db_appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Validate patient
    patient = db.query(Patient).filter(Patient.patient_id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {appointment.patient_id} not found"
        )
    
    # Validate surgeon
    surgeon = db.query(Surgeon).filter(Surgeon.surgeon_id == appointment.surgeon_id).first()
    if not surgeon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Surgeon with ID {appointment.surgeon_id} not found"
        )
    
    # Validate room if provided
    if appointment.room_id:
        room = db.query(OperatingRoom).filter(OperatingRoom.room_id == appointment.room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Operating room with ID {appointment.room_id} not found"
            )
    
    # Update appointment fields
    db_appointment.patient_id = appointment.patient_id
    db_appointment.surgeon_id = appointment.surgeon_id
    db_appointment.room_id = appointment.room_id
    db_appointment.appointment_date = appointment.appointment_date
    db_appointment.status = appointment.status
    db_appointment.notes = appointment.notes
    
    try:
        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating appointment: {str(e)}"
        )


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete appointment.

    Args:
        appointment_id: Appointment ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If appointment not found
    """
    db_appointment = db.query(SurgeryAppointment).filter(SurgeryAppointment.appointment_id == appointment_id).first()
    if db_appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    db.delete(db_appointment)
    db.commit()
    return None
