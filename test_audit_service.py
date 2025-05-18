"""
Tests for the audit service.
"""

import os
import sys
import unittest
import tempfile
import time
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from services.audit_service import AuditService, audit_service
from models import Base, AuditLog


# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """
    Create a database session for testing.

    This fixture creates an in-memory SQLite database, creates all tables,
    and yields a session for testing. After the test, it closes the session
    and drops all tables.

    Yields:
        Session: A SQLAlchemy database session.
    """
    # Create an in-memory SQLite database
    engine = create_engine(DATABASE_URL)

    # Create the AuditLog table explicitly
    from sqlalchemy import (
        Table, Column, Integer, String, DateTime, Text, MetaData
    )

    metadata = MetaData()

    # Define the AuditLog table
    audit_log_table = Table(
        'auditlog',
        metadata,
        Column('log_id', Integer, primary_key=True, autoincrement=True),
        Column('timestamp', DateTime, nullable=False),
        Column('user_id', String(100), nullable=False),
        Column('action', String(50), nullable=False),
        Column('entity_type', String(100), nullable=False),
        Column('entity_id', String(100), nullable=False),
        Column('details', Text, nullable=True)
    )

    # Create the table
    metadata.create_all(engine)

    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Verify that the AuditLog table exists
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if 'auditlog' not in tables:
        raise Exception(f"AuditLog table not created. Available tables: {tables}")
    else:
        print(f"AuditLog table created successfully. Tables: {tables}")

    try:
        yield db
    finally:
        db.close()
        metadata.drop_all(engine)


def test_audit_service_singleton():
    """Test that the audit service is a singleton."""
    service1 = AuditService()
    service2 = AuditService()
    assert service1 is service2


def test_log_event(db_session):
    """Test logging an event to the database."""
    # Create a new audit service for testing
    service = AuditService()

    # Create audit data directly
    audit_data = {
        'timestamp': datetime.now(),
        'user_id': 'test_user',
        'action': 'create',
        'entity_type': 'Surgery',
        'entity_id': '1',
        'details': {"field1": "value1", "field2": "value2"}
    }

    # Log directly to the database
    service._log_to_database(db_session, audit_data)

    # Check that the event was logged to the database
    audit_logs = db_session.query(AuditLog).all()
    assert len(audit_logs) == 1

    log = audit_logs[0]
    assert log.action == "create"
    assert log.entity_type == "Surgery"
    assert log.entity_id == "1"
    assert log.user_id == "test_user"
    assert "field1" in log.details
    assert "field2" in log.details


def test_log_create(db_session):
    """Test logging a create event."""
    # Create a new audit service for testing
    service = AuditService()

    # Create audit data directly
    audit_data = {
        'timestamp': datetime.now(),
        'user_id': 'test_user',
        'action': 'create',
        'entity_type': 'Patient',
        'entity_id': '2',
        'details': {"name": "John Doe"}
    }

    # Log directly to the database
    service._log_to_database(db_session, audit_data)

    # Check that the event was logged to the database
    audit_logs = db_session.query(AuditLog).filter_by(action="create").all()
    assert len(audit_logs) == 1

    log = audit_logs[0]
    assert log.entity_type == "Patient"
    assert log.entity_id == "2"
    assert log.user_id == "test_user"
    assert "name" in log.details


def test_log_update(db_session):
    """Test logging an update event."""
    # Create a new audit service for testing
    service = AuditService()

    # Create audit data directly
    audit_data = {
        'timestamp': datetime.now(),
        'user_id': 'test_user',
        'action': 'update',
        'entity_type': 'Surgeon',
        'entity_id': '3',
        'details': {"name": "Dr. Smith", "old_name": "Dr. Jones"}
    }

    # Log directly to the database
    service._log_to_database(db_session, audit_data)

    # Check that the event was logged to the database
    audit_logs = db_session.query(AuditLog).filter_by(action="update").all()
    assert len(audit_logs) == 1

    log = audit_logs[0]
    assert log.entity_type == "Surgeon"
    assert log.entity_id == "3"
    assert log.user_id == "test_user"
    assert "name" in log.details
    assert "old_name" in log.details


def test_log_delete(db_session):
    """Test logging a delete event."""
    # Create a new audit service for testing
    service = AuditService()

    # Create audit data directly
    audit_data = {
        'timestamp': datetime.now(),
        'user_id': 'test_user',
        'action': 'delete',
        'entity_type': 'OperatingRoom',
        'entity_id': '4',
        'details': {"reason": "No longer needed"}
    }

    # Log directly to the database
    service._log_to_database(db_session, audit_data)

    # Check that the event was logged to the database
    audit_logs = db_session.query(AuditLog).filter_by(action="delete").all()
    assert len(audit_logs) == 1

    log = audit_logs[0]
    assert log.entity_type == "OperatingRoom"
    assert log.entity_id == "4"
    assert log.user_id == "test_user"
    assert "reason" in log.details


def test_log_to_file():
    """Test logging an event to a file."""
    # Create a temporary directory and file for testing
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, "audit.log")

    try:
        # Create a new audit service for testing with direct file logging
        with patch.dict(os.environ, {
            'AUDIT_LOG_TO_FILE': 'True',
            'AUDIT_LOG_FILE': temp_file_path
        }):
            # Create a new service instance to pick up the environment variables
            service = AuditService()

            # Force the log_to_file flag to True
            service.log_to_file = True
            service.log_file = temp_file_path

            # Log an event
            service.log_event(
                db=None,
                action="view",
                entity_type="Report",
                entity_id=5,
                user_id="test_user",
                details={"report_type": "Monthly"}
            )

            # Wait for the event to be processed
            time.sleep(0.5)  # Increase wait time

            # Check that the event was logged to the file
            if os.path.exists(temp_file_path):
                with open(temp_file_path, 'r') as f:
                    content = f.read()
                    print(f"File content: {content}")
                    assert "view" in content
                    assert "Report" in content
                    assert "5" in content
                    assert "test_user" in content
                    assert "Monthly" in content
            else:
                # If the file doesn't exist, log the directory contents
                print(f"File {temp_file_path} does not exist")
                print(f"Directory contents: {os.listdir(temp_dir)}")
                assert False, f"Log file {temp_file_path} was not created"

    finally:
        # Clean up the temporary file and directory
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        os.rmdir(temp_dir)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
