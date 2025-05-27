"""
Tests for the SDST API endpoints.

This module provides comprehensive tests for the SDST (Sequence-Dependent Setup Time) API endpoints.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_config import get_db, Base
from api.main import app
from api.auth import get_current_active_user, get_password_hash
from models import User, SurgeryType, SequenceDependentSetupTime

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_active_user():
    return User(
        user_id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        role="admin",
        is_active=True,
        created_at=datetime.now(),
        hashed_password=get_password_hash("testpassword")
    )

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_active_user] = override_get_current_active_user

client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create test surgery types
    surgery_type1 = SurgeryType(
        type_id=1,
        name="Orthopedic Surgery",
        description="Bone and joint surgery",
        average_duration=120
    )
    surgery_type2 = SurgeryType(
        type_id=2,
        name="Cardiac Surgery",
        description="Heart surgery",
        average_duration=180
    )
    surgery_type3 = SurgeryType(
        type_id=3,
        name="General Surgery",
        description="General surgical procedures",
        average_duration=90
    )

    db.add_all([surgery_type1, surgery_type2, surgery_type3])
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


def test_create_surgery_type():
    """Test creating a surgery type."""
    response = client.post(
        "/api/surgery-types/",
        json={
            "name": "Neurosurgery",
            "description": "Brain and nervous system surgery",
            "average_duration": 240
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Neurosurgery"
    assert data["description"] == "Brain and nervous system surgery"
    assert data["average_duration"] == 240
    assert "type_id" in data


def test_read_surgery_types():
    """Test reading surgery types."""
    response = client.get("/api/surgery-types/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_read_surgery_type():
    """Test reading a specific surgery type."""
    # First create a surgery type
    create_response = client.post(
        "/api/surgery-types/",
        json={
            "name": "Test Surgery Type",
            "description": "Test description",
            "average_duration": 60
        }
    )
    surgery_type_id = create_response.json()["type_id"]

    # Then read it
    response = client.get(f"/api/surgery-types/{surgery_type_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Surgery Type"


def test_update_surgery_type():
    """Test updating a surgery type."""
    # First create a surgery type
    create_response = client.post(
        "/api/surgery-types/",
        json={
            "name": "Original Name",
            "description": "Original description",
            "average_duration": 60
        }
    )
    surgery_type_id = create_response.json()["type_id"]

    # Then update it
    response = client.put(
        f"/api/surgery-types/{surgery_type_id}",
        json={
            "name": "Updated Name",
            "average_duration": 90
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["average_duration"] == 90


def test_delete_surgery_type():
    """Test deleting a surgery type."""
    # First create a surgery type
    create_response = client.post(
        "/api/surgery-types/",
        json={
            "name": "To Delete",
            "description": "Will be deleted",
            "average_duration": 60
        }
    )
    surgery_type_id = create_response.json()["type_id"]

    # Then delete it
    response = client.delete(f"/api/surgery-types/{surgery_type_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/api/surgery-types/{surgery_type_id}")
    assert response.status_code == 404


def test_create_sdst(db):
    """Test creating an SDST record."""
    response = client.post(
        "/api/sdst/",
        json={
            "from_surgery_type_id": 1,
            "to_surgery_type_id": 2,
            "setup_time_minutes": 30
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["from_surgery_type_id"] == 1
    assert data["to_surgery_type_id"] == 2
    assert data["setup_time_minutes"] == 30
    assert "id" in data


def test_create_sdst_invalid_surgery_type(db):
    """Test creating SDST with invalid surgery type."""
    response = client.post(
        "/api/sdst/",
        json={
            "from_surgery_type_id": 999,  # Non-existent
            "to_surgery_type_id": 1,
            "setup_time_minutes": 30
        }
    )
    assert response.status_code == 404


def test_create_duplicate_sdst(db):
    """Test creating duplicate SDST record."""
    # Create first SDST
    client.post(
        "/api/sdst/",
        json={
            "from_surgery_type_id": 1,
            "to_surgery_type_id": 2,
            "setup_time_minutes": 30
        }
    )

    # Try to create duplicate
    response = client.post(
        "/api/sdst/",
        json={
            "from_surgery_type_id": 1,
            "to_surgery_type_id": 2,
            "setup_time_minutes": 45
        }
    )
    assert response.status_code == 400


def test_read_sdst_list(db):
    """Test reading SDST list."""
    # Create some SDST records
    client.post("/api/sdst/", json={"from_surgery_type_id": 1, "to_surgery_type_id": 2, "setup_time_minutes": 30})
    client.post("/api/sdst/", json={"from_surgery_type_id": 2, "to_surgery_type_id": 3, "setup_time_minutes": 45})

    response = client.get("/api/sdst/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_read_sdst_matrix(db):
    """Test reading SDST matrix."""
    # Create some SDST records
    client.post("/api/sdst/", json={"from_surgery_type_id": 1, "to_surgery_type_id": 2, "setup_time_minutes": 30})
    client.post("/api/sdst/", json={"from_surgery_type_id": 2, "to_surgery_type_id": 3, "setup_time_minutes": 45})

    response = client.get("/api/sdst/matrix")
    assert response.status_code == 200
    data = response.json()
    assert "surgery_types" in data
    assert "setup_times" in data
    assert "matrix" in data
    assert isinstance(data["matrix"], dict)


def test_update_sdst(db):
    """Test updating an SDST record."""
    # Create SDST
    create_response = client.post(
        "/api/sdst/",
        json={
            "from_surgery_type_id": 1,
            "to_surgery_type_id": 2,
            "setup_time_minutes": 30
        }
    )
    sdst_id = create_response.json()["id"]

    # Update it
    response = client.put(
        f"/api/sdst/{sdst_id}",
        json={"setup_time_minutes": 45}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["setup_time_minutes"] == 45


def test_delete_sdst(db):
    """Test deleting an SDST record."""
    # Create SDST
    create_response = client.post(
        "/api/sdst/",
        json={
            "from_surgery_type_id": 1,
            "to_surgery_type_id": 2,
            "setup_time_minutes": 30
        }
    )
    sdst_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/api/sdst/{sdst_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/api/sdst/{sdst_id}")
    assert response.status_code == 404


def test_bulk_import_sdst(db):
    """Test bulk importing SDST data."""
    response = client.post(
        "/api/sdst/bulk/import",
        json={
            "sdst_data": [
                {"from_surgery_type_id": 1, "to_surgery_type_id": 2, "setup_time_minutes": 30},
                {"from_surgery_type_id": 2, "to_surgery_type_id": 3, "setup_time_minutes": 45},
                {"from_surgery_type_id": 3, "to_surgery_type_id": 1, "setup_time_minutes": 60}
            ],
            "overwrite_existing": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["created_count"] == 3
    assert data["error_count"] == 0


def test_bulk_export_sdst(db):
    """Test bulk exporting SDST data."""
    # Create some SDST records first
    client.post("/api/sdst/", json={"from_surgery_type_id": 1, "to_surgery_type_id": 2, "setup_time_minutes": 30})
    client.post("/api/sdst/", json={"from_surgery_type_id": 2, "to_surgery_type_id": 3, "setup_time_minutes": 45})

    response = client.post(
        "/api/sdst/bulk/export",
        json={"surgery_type_ids": [1, 2]}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
