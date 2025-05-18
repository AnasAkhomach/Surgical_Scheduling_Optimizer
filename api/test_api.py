"""
Tests for the FastAPI application.

This module provides tests for the FastAPI application.
"""

import os
import sys
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_config import get_db, Base
from api.main import app
from api.auth import get_current_active_user
from models import User, OperatingRoom

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test tables
Base.metadata.create_all(bind=engine)

# Create tables explicitly
from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime, ForeignKey
metadata = MetaData()

# Create OperatingRoom table
operating_room_table = Table(
    'operatingroom', metadata,
    Column('room_id', Integer, primary_key=True),
    Column('location', String(255), nullable=False)
)

# Create Surgery table
surgery_table = Table(
    'surgery', metadata,
    Column('surgery_id', Integer, primary_key=True),
    Column('scheduled_date', DateTime),
    Column('surgery_type_id', Integer),
    Column('urgency_level', String(50)),
    Column('duration_minutes', Integer),
    Column('status', String(50)),
    Column('start_time', DateTime),
    Column('end_time', DateTime),
    Column('patient_id', Integer),
    Column('surgeon_id', Integer),
    Column('room_id', Integer, ForeignKey('operatingroom.room_id'))
)

# Create OperatingRoomEquipment table
operating_room_equipment_table = Table(
    'operatingroomequipment', metadata,
    Column('id', Integer, primary_key=True),
    Column('room_id', Integer, ForeignKey('operatingroom.room_id')),
    Column('equipment_name', String(255))
)

metadata.create_all(bind=engine)


# Mock current user for testing
async def override_get_current_active_user():
    """Mock current user for testing."""
    return User(
        user_id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        role="admin",
        is_active=True,
        created_at=datetime.now()
    )


# Override dependencies
app.dependency_overrides[get_current_active_user] = override_get_current_active_user


# Override database session
def override_get_db():
    """Override database session for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_read_users_me():
    """Test read current user endpoint."""
    response = client.get("/api/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["role"] == "admin"


def test_create_operating_room():
    """Test create operating room endpoint."""
    response = client.post(
        "/api/operating-rooms/",
        json={"location": "Test Room"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["location"] == "Test Room"
    assert "room_id" in data


def test_read_operating_rooms():
    """Test read operating rooms endpoint."""
    # Create a test operating room
    client.post(
        "/api/operating-rooms/",
        json={"location": "Test Room 2"}
    )

    response = client.get("/api/operating-rooms/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(room["location"] == "Test Room 2" for room in data)


def test_read_operating_room():
    """Test read operating room endpoint."""
    # Create a test operating room
    create_response = client.post(
        "/api/operating-rooms/",
        json={"location": "Test Room 3"}
    )
    room_id = create_response.json()["room_id"]

    response = client.get(f"/api/operating-rooms/{room_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "Test Room 3"
    assert data["room_id"] == room_id


def test_update_operating_room():
    """Test update operating room endpoint."""
    # Create a test operating room
    create_response = client.post(
        "/api/operating-rooms/",
        json={"location": "Test Room 4"}
    )
    room_id = create_response.json()["room_id"]

    response = client.put(
        f"/api/operating-rooms/{room_id}",
        json={"location": "Updated Test Room"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "Updated Test Room"
    assert data["room_id"] == room_id


def test_delete_operating_room():
    """Test delete operating room endpoint."""
    # Create a test operating room
    create_response = client.post(
        "/api/operating-rooms/",
        json={"location": "Test Room 5"}
    )
    room_id = create_response.json()["room_id"]

    response = client.delete(f"/api/operating-rooms/{room_id}")
    assert response.status_code == 204

    # Verify it's deleted
    response = client.get(f"/api/operating-rooms/{room_id}")
    assert response.status_code == 404
