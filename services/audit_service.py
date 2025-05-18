"""
Audit logging service for the surgery scheduling application.

This module provides a service for logging audit events to track changes
to entities and user actions.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import threading
import queue
import time
import os

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models import AuditLog
from services.exceptions import DatabaseError
from services.logger_config import logger


class SingletonMeta(type):
    """Metaclass for implementing the Singleton pattern."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Ensure only one instance of the class is created.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The singleton instance of the class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AuditService(metaclass=SingletonMeta):
    """
    Service for logging audit events.

    This service provides methods for logging audit events to track changes
    to entities and user actions.
    """

    def __init__(self):
        """Initialize the audit service."""
        self.queue = queue.Queue()
        self.queue_thread = None
        self.queue_running = False
        self.log_to_file = os.getenv('AUDIT_LOG_TO_FILE', 'False').lower() in ('true', '1', 't')
        self.log_file = os.getenv('AUDIT_LOG_FILE', 'logs/audit.log')

        # Create logs directory if it doesn't exist and we're logging to file
        if self.log_to_file:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        # Start the queue processing thread
        self.start_queue_processing()

    def start_queue_processing(self):
        """Start the background thread for processing audit logs."""
        if self.queue_thread is None or not self.queue_thread.is_alive():
            self.queue_running = True
            self.queue_thread = threading.Thread(
                target=self._process_queue,
                daemon=True
            )
            self.queue_thread.start()
            logger.info("Audit log queue processing started")

    def stop_queue_processing(self):
        """Stop the background thread for processing audit logs."""
        self.queue_running = False
        if self.queue_thread and self.queue_thread.is_alive():
            self.queue_thread.join(timeout=5.0)
            logger.info("Audit log queue processing stopped")

    def _process_queue(self):
        """Process audit logs in the queue."""
        while self.queue_running:
            try:
                # Get the next audit log from the queue
                audit_data, db = self.queue.get(block=True, timeout=1.0)

                # Process the audit log
                try:
                    # Log to database if we have a session
                    if db:
                        self._log_to_database(db, audit_data)

                    # Log to file if enabled
                    if self.log_to_file:
                        self._log_to_file(audit_data)

                    # Log to console
                    logger.info(f"Audit: {audit_data['action']} - {audit_data['entity_type']} {audit_data['entity_id']}")

                except Exception as e:
                    logger.error(f"Error processing audit log: {e}")

                # Mark the task as done
                self.queue.task_done()

            except queue.Empty:
                # No audit logs in the queue, sleep for a bit
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in audit log queue processing: {e}")
                time.sleep(1.0)  # Sleep to avoid tight loop on error

    def _log_to_database(self, db: Session, audit_data: Dict[str, Any]):
        """
        Log an audit event to the database.

        Args:
            db: SQLAlchemy database session.
            audit_data: The audit data to log.

        Raises:
            DatabaseError: If the audit log cannot be saved to the database.
        """
        try:
            # Check if the AuditLog table exists
            from sqlalchemy import inspect
            inspector = inspect(db.get_bind())
            if 'auditlog' not in inspector.get_table_names():
                logger.warning("AuditLog table does not exist, creating it")

                # Create the AuditLog table
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
                metadata.create_all(db.get_bind())

            # Create audit log record
            audit_log = AuditLog(
                timestamp=audit_data['timestamp'],
                user_id=audit_data['user_id'],
                action=audit_data['action'],
                entity_type=audit_data['entity_type'],
                entity_id=audit_data['entity_id'],
                details=json.dumps(audit_data['details']) if audit_data['details'] else None
            )

            # Add to database
            db.add(audit_log)
            db.commit()

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error saving audit log to database: {e}")
            raise DatabaseError("Failed to save audit log to database", e)

    def _log_to_file(self, audit_data: Dict[str, Any]):
        """
        Log an audit event to a file.

        Args:
            audit_data: The audit data to log.
        """
        try:
            # Create a copy of the audit data for serialization
            log_data = audit_data.copy()

            # Convert datetime to string for JSON serialization
            if isinstance(log_data['timestamp'], datetime):
                log_data['timestamp'] = log_data['timestamp'].isoformat()

            # Format the log entry
            log_entry = json.dumps(log_data)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

            # Write to file
            with open(self.log_file, 'a') as f:
                f.write(f"{log_entry}\n")

        except Exception as e:
            logger.error(f"Error writing audit log to file: {e}")

    def log_event(
        self,
        db: Optional[Session],
        action: str,
        entity_type: str,
        entity_id: Union[int, str],
        user_id: Optional[Union[int, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log an audit event.

        Args:
            db: SQLAlchemy database session (optional).
            action: The action performed (e.g., "create", "update", "delete").
            entity_type: The type of entity (e.g., "Surgery", "Patient").
            entity_id: The ID of the entity.
            user_id: The ID of the user who performed the action.
            details: Additional details about the action.
        """
        # Create audit data
        audit_data = {
            'timestamp': datetime.now(),  # Use datetime object instead of string
            'user_id': user_id or 'system',
            'action': action,
            'entity_type': entity_type,
            'entity_id': str(entity_id),  # Convert to string to ensure compatibility
            'details': details or {}
        }

        # Add to queue for processing
        self.queue.put((audit_data, db))

    def log_create(
        self,
        db: Optional[Session],
        entity_type: str,
        entity_id: Union[int, str],
        user_id: Optional[Union[int, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a create event.

        Args:
            db: SQLAlchemy database session (optional).
            entity_type: The type of entity (e.g., "Surgery", "Patient").
            entity_id: The ID of the entity.
            user_id: The ID of the user who performed the action.
            details: Additional details about the action.
        """
        self.log_event(db, 'create', entity_type, entity_id, user_id, details)

    def log_update(
        self,
        db: Optional[Session],
        entity_type: str,
        entity_id: Union[int, str],
        user_id: Optional[Union[int, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log an update event.

        Args:
            db: SQLAlchemy database session (optional).
            entity_type: The type of entity (e.g., "Surgery", "Patient").
            entity_id: The ID of the entity.
            user_id: The ID of the user who performed the action.
            details: Additional details about the action.
        """
        self.log_event(db, 'update', entity_type, entity_id, user_id, details)

    def log_delete(
        self,
        db: Optional[Session],
        entity_type: str,
        entity_id: Union[int, str],
        user_id: Optional[Union[int, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a delete event.

        Args:
            db: SQLAlchemy database session (optional).
            entity_type: The type of entity (e.g., "Surgery", "Patient").
            entity_id: The ID of the entity.
            user_id: The ID of the user who performed the action.
            details: Additional details about the action.
        """
        self.log_event(db, 'delete', entity_type, entity_id, user_id, details)


# Singleton instance for global access
audit_service = AuditService()
