"""
Patients router for the FastAPI application.

This module provides API endpoints for patient management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_config import get_db
from models import Patient, User
from api.models import PatientCreate, Patient as PatientResponse, PatientUpdate
from api.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new patient.

    Args:
        patient: Patient data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Patient: Created patient
    """
    db_patient = Patient(
        name=patient.name,
        dob=patient.dob,
        contact_info=patient.contact_info,
        privacy_consent=patient.privacy_consent
    )

    try:
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating patient"
        )


@router.get("/", response_model=List[PatientResponse])
async def read_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all patients.

    Args:
        skip: Number of patients to skip
        limit: Maximum number of patients to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[Patient]: List of patients
    """
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
async def read_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get patient by ID.

    Args:
        patient_id: Patient ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Patient: Patient with specified ID

    Raises:
        HTTPException: If patient not found
    """
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update patient.

    Args:
        patient_id: Patient ID
        patient: Patient data to update
        db: Database session
        current_user: Current authenticated user

    Returns:
        Patient: Updated patient

    Raises:
        HTTPException: If patient not found
    """
    db_patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # Update patient fields
    update_data = patient.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)

    try:
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating patient"
        )


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete patient.

    Args:
        patient_id: Patient ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If patient not found
    """
    db_patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    db.delete(db_patient)
    db.commit()
    return None
