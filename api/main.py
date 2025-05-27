"""
FastAPI application for surgery scheduling.

This module provides a RESTful API for the surgery scheduling application.
"""

import os
import logging
import sys
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import database configuration
from db_config import get_db, init_db

# Import API routers
from api.routers import (
    surgeries,
    operating_rooms,
    surgeons,
    patients,
    staff,
    appointments,
    schedules,
    auth,
    users,
    surgery_types,
    sdst,
    websockets
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Surgery Scheduler API",
    description="API for surgery scheduling with Tabu Search optimization",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed field information."""
    field_errors = {}
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])  # Skip 'body' prefix
        if field not in field_errors:
            field_errors[field] = []
        field_errors[field].append(error["msg"])

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "field_errors": field_errors
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors."""
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "error_code": "VALUE_ERROR"
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors."""
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Database constraint violation",
            "error_code": "INTEGRITY_ERROR"
        }
    )

# Initialize database
@app.on_event("startup")
async def startup_db_client():
    """Initialize database on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(surgeries.router, prefix="/api/surgeries", tags=["Surgeries"])
app.include_router(operating_rooms.router, prefix="/api/operating-rooms", tags=["Operating Rooms"])
app.include_router(surgeons.router, prefix="/api/surgeons", tags=["Surgeons"])
app.include_router(patients.router, prefix="/api/patients", tags=["Patients"])
app.include_router(staff.router, prefix="/api/staff", tags=["Staff"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["Schedules"])
app.include_router(surgery_types.router, prefix="/api/surgery-types", tags=["Surgery Types"])
app.include_router(sdst.router, prefix="/api/sdst", tags=["SDST"])
app.include_router(websockets.router, prefix="/api/ws", tags=["WebSockets"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
