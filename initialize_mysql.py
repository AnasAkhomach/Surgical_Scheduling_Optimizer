"""
MySQL database initialization script.

This script initializes the MySQL database schema and creates necessary tables.
It should be run once when setting up a new MySQL database.
"""

import os
import sys
import logging
import pymysql
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from db_config import engine, Base, DATABASE_URL
from models import *  # Ensure all models are imported to be registered with Base

def create_database_if_not_exists():
    """Create the MySQL database if it doesn't exist."""
    if not DATABASE_URL.startswith('mysql'):
        logger.info("Not using MySQL, skipping database creation.")
        return

    try:
        # Extract database name from URL
        db_name = DATABASE_URL.split('/')[-1]

        # Extract connection parameters from URL
        connection_string = DATABASE_URL.split('@')[1].split('/')[0]
        host = connection_string.split(':')[0]
        port = int(connection_string.split(':')[1]) if ':' in connection_string else 3306

        # Extract username and password
        credentials = DATABASE_URL.split('@')[0].split('://')[-1]
        username = credentials.split(':')[0]
        password = credentials.split(':')[1] if ':' in credentials else ''

        # Connect to MySQL server (without specifying a database)
        connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password
        )

        try:
            with connection.cursor() as cursor:
                # Create database if it doesn't exist
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                logger.info(f"Database '{db_name}' created or already exists.")

                # Grant privileges (if running as root)
                try:
                    cursor.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{username}'@'%'")
                    cursor.execute("FLUSH PRIVILEGES")
                    logger.info(f"Privileges granted to user '{username}'.")
                except Exception as e:
                    logger.warning(f"Could not grant privileges: {e}")
                    logger.warning("This is normal if you're not running as root or the user already has privileges.")
        finally:
            connection.close()

    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise

def initialize_database_schema():
    """Initialize the database schema by creating all tables."""
    logger.info("Initializing database schema...")
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("Database schema initialized successfully based on models.")

        # Verify tables were created
        with engine.connect() as connection:
            if DATABASE_URL.startswith('mysql'):
                # For MySQL
                db_name = DATABASE_URL.split('/')[-1]
                result = connection.execute(text(f"SHOW TABLES FROM `{db_name}`"))
                tables = [row[0] for row in result]
            else:
                # For SQLite
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]

            logger.info(f"Created tables: {', '.join(tables)}")

    except SQLAlchemyError as e:
        logger.error(f"Error initializing database schema: {e}")
        raise

if __name__ == "__main__":
    if DATABASE_URL.startswith('mysql'):
        logger.info("Initializing MySQL database...")
        create_database_if_not_exists()
    else:
        logger.info(f"Using database: {DATABASE_URL}")

    initialize_database_schema()
    logger.info("Database initialization complete.")