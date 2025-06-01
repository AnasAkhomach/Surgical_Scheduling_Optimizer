"""
Database configuration for the surgery scheduling application.

This module provides functions to create database sessions and engines.
It supports both MySQL and SQLite databases.
"""

import os
import logging
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Configure logging
# logging.basicConfig(level=logging.INFO) # Commented out to prevent double logging
logger = logging.getLogger(__name__)

# Determine database URL
def get_database_url():
    """
    Get the database URL from environment variables.

    Returns:
        str: The database URL.
    """
    # Check for direct DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        logger.info(f"Using database URL from DATABASE_URL environment variable")
        return database_url

    # Check for MySQL components
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if all([db_user, db_password, db_host, db_port, db_name]):
        # Construct MySQL URL
        encoded_password = quote_plus(db_password)
        mysql_url = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
        logger.info(f"Using MySQL database at {db_host}:{db_port}/{db_name}")
        return mysql_url

    # Fallback to SQLite
    sqlite_url = os.getenv("SQLITE_URL", "sqlite:///./surgery_scheduler.db")
    logger.info("Using SQLite database (fallback)")
    return sqlite_url

# Get the database URL
DATABASE_URL = get_database_url()

if not DATABASE_URL:
    raise ValueError("Database connection parameters not set. Please check your environment variables.")

# Create SQLAlchemy engine with appropriate parameters
def create_db_engine(url):
    """
    Create a SQLAlchemy engine.

    Args:
        url (str): The database URL.

    Returns:
        Engine: A SQLAlchemy engine.
    """
    echo = os.getenv("SQL_ECHO", "False").lower() in ("true", "1", "t")

    # MySQL-specific parameters
    if url.startswith("mysql"):
        return create_engine(
            url,
            echo=echo,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections after 1 hour
            pool_size=10,       # Connection pool size
            max_overflow=20,    # Max extra connections when pool is full
            connect_args={"connect_timeout": 30}  # Connection timeout in seconds
        )
    # SQLite-specific parameters
    else:
        return create_engine(
            url,
            echo=echo,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False}  # Allow multi-threaded access
        )

# Create the engine
try:
    engine = create_db_engine(DATABASE_URL)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Error creating database engine: {e}")
    raise

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

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def close_db_connection():
    """
    Close the database connection.

    This function should be called when the application shuts down.
    """
    db_session.remove()
    logger.info("Database connection closed")