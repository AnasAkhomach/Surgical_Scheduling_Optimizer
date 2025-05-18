"""
Database configuration for the surgery scheduling application.

This module provides functions to create database sessions and engines.
"""

import os
import logging
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Force SQLite for development/testing
DATABASE_URL = "sqlite:///./surgery_scheduler.db"
logger.info("Using SQLite database")

if not DATABASE_URL:
    raise ValueError("Database connection parameters not set. Please check your environment variables.")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "False").lower() in ("true", "1", "t"),
    pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create scoped session for thread safety
db_session = scoped_session(SessionLocal)

# Base class for all models
Base = declarative_base()
Base.query = db_session.query_property()

def get_db():
    """
    Get a database session.

    This function creates a new database session and ensures it is closed
    after use, even if an exception occurs.

    Yields:
        Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database.

    This function creates all tables defined in the models.
    """
    # Import all models here to ensure they are registered with Base
    import models

    Base.metadata.create_all(bind=engine)

def close_db_connection():
    """
    Close the database connection.

    This function should be called when the application shuts down.
    """
    db_session.remove()