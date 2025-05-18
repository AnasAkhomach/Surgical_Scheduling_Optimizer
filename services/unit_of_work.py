"""
Unit of Work pattern implementation for transaction management.

This module provides a UnitOfWork class that manages transactions across multiple services.
It ensures that all operations within a transaction either succeed or fail together.
"""

import logging
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import os
from db_config import SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class UnitOfWork:
    """
    Unit of Work pattern implementation for transaction management.

    This class manages database transactions and ensures that all operations
    within a transaction either succeed or fail together.
    """

    def __init__(self, testing=False):
        """
        Initialize the unit of work.

        Args:
            testing: Whether the unit of work is being used in a test environment.
        """
        self.db = None
        self._in_transaction = False
        self.testing = testing or os.getenv('TESTING', 'False').lower() in ('true', '1', 't')

    def __enter__(self):
        """
        Enter the context manager and start a new transaction.

        Returns:
            UnitOfWork: The UnitOfWork instance.
        """
        if self.testing:
            # Use SQLite in-memory database for testing
            engine = create_engine('sqlite:///:memory:')
            TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

            # Create tables
            from models import Base
            Base.metadata.create_all(engine)

            self.db = TestingSessionLocal()
        else:
            # Use the configured database session
            self.db = SessionLocal()

        self._in_transaction = True
        logger.debug("Transaction started")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager and commit or rollback the transaction.

        Args:
            exc_type: Exception type if an exception was raised, None otherwise.
            exc_val: Exception value if an exception was raised, None otherwise.
            exc_tb: Exception traceback if an exception was raised, None otherwise.
        """
        try:
            if exc_type is not None:
                self.rollback()
                logger.error(f"Transaction rolled back due to exception: {exc_val}")
            else:
                self.commit()
                logger.debug("Transaction committed")
        finally:
            self.db.close()
            self._in_transaction = False
            logger.debug("Database session closed")

    def commit(self):
        """
        Commit the current transaction.

        Raises:
            RuntimeError: If not in a transaction.
        """
        if not self._in_transaction:
            raise RuntimeError("Cannot commit - not in a transaction")

        self.db.commit()

    def rollback(self):
        """
        Rollback the current transaction.

        Raises:
            RuntimeError: If not in a transaction.
        """
        if not self._in_transaction:
            raise RuntimeError("Cannot rollback - not in a transaction")

        self.db.rollback()

    @contextmanager
    def savepoint(self, name=None):
        """
        Create a savepoint within the current transaction.

        This allows for nested transactions. If an exception occurs within the
        savepoint, only the operations since the savepoint are rolled back.

        Args:
            name: Optional name for the savepoint.

        Yields:
            The current session.

        Raises:
            RuntimeError: If not in a transaction.
        """
        if not self._in_transaction:
            raise RuntimeError("Cannot create savepoint - not in a transaction")

        try:
            with self.db.begin_nested():
                logger.debug(f"Savepoint created{f' ({name})' if name else ''}")
                yield self.db
                logger.debug(f"Savepoint committed{f' ({name})' if name else ''}")
        except Exception as e:
            logger.error(f"Savepoint rolled back{f' ({name})' if name else ''} due to exception: {e}")
            raise


# Singleton instance for global access
unit_of_work = UnitOfWork()
