"""
Database setup script for the surgery scheduling application.

This script initializes the database and creates the necessary tables.
It supports both MySQL and SQLite databases.
"""

import logging
import argparse
import os
import sys
from sqlalchemy import inspect, create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from dotenv import load_dotenv

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

def setup_mysql_database():
    """
    Set up a MySQL database by creating it if it doesn't exist.
    """
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        logger.error("MySQL connection parameters not set. Check your environment variables.")
        return False

    # Connect to MySQL server (without specifying a database initially)
    server_engine_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    server_engine = create_engine(server_engine_url)

    try:
        with server_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
            connection.commit()  # Ensure the CREATE DATABASE command is committed
            logger.info(f"Database '{DB_NAME}' ensured to exist.")
        return True
    except OperationalError as e:
        logger.error(f"Could not connect to MySQL server or create database: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during database creation: {e}")
        return False

def setup_database():
    """
    Set up the database by creating all tables.
    """
    try:
        from db_config import engine, Base, DATABASE_URL
        import models  # Import models to ensure they're registered with Base
        #from models import *  # Import all models to ensure they're registered with Base

        # If using MySQL with individual parameters, ensure the database exists
        if "mysql" in DATABASE_URL and not os.getenv("DATABASE_URL"):
            if not setup_mysql_database():
                return False

        # Create tables
        inspector = inspect(engine)

        # Create all tables defined in the models if they don't exist
        if not inspector.get_table_names():
            logger.info("Creating database tables based on SQLAlchemy models...")
            Base.metadata.create_all(engine)
            logger.info("Database tables created successfully.")
        else:
            logger.info("Database tables already exist.")

        # Log the tables that were created
        logger.info(f"Available tables: {inspector.get_table_names()}")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def run_migrations():
    """
    Run database migrations using Alembic.
    """
    try:
        import alembic.config

        logger.info("Running database migrations...")
        alembic_args = [
            '--raiseerr',
            'upgrade', 'head',
        ]
        alembic.config.main(argv=alembic_args)
        logger.info("Database migrations completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        return False

def main():
    """
    Main entry point for the database setup script.
    """
    parser = argparse.ArgumentParser(description='Set up the surgery scheduling database')
    parser.add_argument('--migrations', action='store_true', help='Run database migrations')
    parser.add_argument('--create-tables', action='store_true', help='Create database tables')

    args = parser.parse_args()

    if args.migrations:
        success = run_migrations()
    elif args.create_tables:
        success = setup_database()
    else:
        # Default: create tables
        success = setup_database()

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
