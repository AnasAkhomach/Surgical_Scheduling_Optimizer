# Surgery Scheduler API

This directory contains the FastAPI implementation for the Surgery Scheduler application.

## Overview

The API provides endpoints for managing surgeries, operating rooms, surgeons, patients, staff, appointments, and schedule optimization.

## Directory Structure

```
api/
├── main.py                # FastAPI application entry point
├── auth.py                # Authentication utilities
├── models.py              # Pydantic models for request/response validation
├── routers/               # API route handlers
│   ├── auth.py            # Authentication endpoints
│   ├── users.py           # User management endpoints
│   ├── surgeries.py       # Surgery management endpoints
│   ├── operating_rooms.py # Operating room management endpoints
│   ├── surgeons.py        # Surgeon management endpoints
│   ├── patients.py        # Patient management endpoints
│   ├── staff.py           # Staff management endpoints
│   ├── appointments.py    # Appointment management endpoints
│   └── schedules.py       # Schedule optimization endpoints
└── test_api.py            # API tests
```

## API Endpoints

### Authentication

- `POST /api/auth/token`: Authenticate user and get JWT token

### Users

- `POST /api/users/`: Create a new user (admin only)
- `GET /api/users/me`: Get current user
- `GET /api/users/`: Get all users (admin only)
- `GET /api/users/{user_id}`: Get user by ID (admin only)
- `PUT /api/users/{user_id}`: Update user (admin only)
- `DELETE /api/users/{user_id}`: Delete user (admin only)

### Surgeries

- `POST /api/surgeries/`: Create a new surgery
- `GET /api/surgeries/`: Get all surgeries
- `GET /api/surgeries/{surgery_id}`: Get surgery by ID
- `PUT /api/surgeries/{surgery_id}`: Update surgery
- `DELETE /api/surgeries/{surgery_id}`: Delete surgery

### Operating Rooms

- `POST /api/operating-rooms/`: Create a new operating room
- `GET /api/operating-rooms/`: Get all operating rooms
- `GET /api/operating-rooms/{room_id}`: Get operating room by ID
- `PUT /api/operating-rooms/{room_id}`: Update operating room
- `DELETE /api/operating-rooms/{room_id}`: Delete operating room

### Surgeons

- `POST /api/surgeons/`: Create a new surgeon
- `GET /api/surgeons/`: Get all surgeons
- `GET /api/surgeons/{surgeon_id}`: Get surgeon by ID
- `PUT /api/surgeons/{surgeon_id}`: Update surgeon
- `DELETE /api/surgeons/{surgeon_id}`: Delete surgeon

### Patients

- `POST /api/patients/`: Create a new patient
- `GET /api/patients/`: Get all patients
- `GET /api/patients/{patient_id}`: Get patient by ID
- `PUT /api/patients/{patient_id}`: Update patient
- `DELETE /api/patients/{patient_id}`: Delete patient

### Staff

- `POST /api/staff/`: Create a new staff member
- `GET /api/staff/`: Get all staff members
- `GET /api/staff/{staff_id}`: Get staff member by ID
- `PUT /api/staff/{staff_id}`: Update staff member
- `DELETE /api/staff/{staff_id}`: Delete staff member

### Appointments

- `POST /api/appointments/`: Create a new appointment
- `GET /api/appointments/`: Get all appointments
- `GET /api/appointments/{appointment_id}`: Get appointment by ID
- `PUT /api/appointments/{appointment_id}`: Update appointment
- `DELETE /api/appointments/{appointment_id}`: Delete appointment

### Schedules

- `POST /api/schedules/optimize`: Optimize surgery schedule
- `POST /api/schedules/apply`: Apply optimized schedule
- `GET /api/schedules/current`: Get current schedule

## Running the API

To run the API, use the `run_api.py` script in the root directory:

```bash
python run_api.py
```

Or use uvicorn directly:

```bash
uvicorn api.main:app --reload
```

## API Documentation

Once the API is running, you can access the auto-generated documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

To run the API tests:

```bash
pytest api/test_api.py
```
