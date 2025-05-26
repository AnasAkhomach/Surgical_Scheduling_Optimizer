"""
SQLite to MySQL migration script.

This script migrates data from a SQLite database to a MySQL database.
It should be run after setting up the MySQL database schema.
"""

import os
import sys
import logging
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

def get_sqlite_engine():
    """Create a SQLAlchemy engine for SQLite."""
    sqlite_url = os.getenv("SQLITE_URL", "sqlite:///./surgery_scheduler.db")
    return create_engine(sqlite_url)

def get_mysql_engine():
    """Create a SQLAlchemy engine for MySQL."""
    # Check for direct DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith('mysql'):
        return create_engine(database_url)
    
    # Check for MySQL components
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    if all([db_user, db_password, db_host, db_port, db_name]):
        from urllib.parse import quote_plus
        encoded_password = quote_plus(db_password)
        mysql_url = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
        return create_engine(mysql_url)
    
    raise ValueError("MySQL connection parameters not set. Please check your environment variables.")

def get_table_names(engine):
    """Get all table names from the database."""
    with engine.connect() as connection:
        if str(engine.url).startswith('sqlite'):
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            return [row[0] for row in result if not row[0].startswith('sqlite_')]
        else:
            db_name = str(engine.url).split('/')[-1]
            result = connection.execute(text(f"SHOW TABLES FROM `{db_name}`"))
            return [row[0] for row in result]

def migrate_table(sqlite_engine, mysql_engine, table_name):
    """Migrate data from SQLite table to MySQL table."""
    logger.info(f"Migrating table: {table_name}")
    
    # Create sessions
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    MySQLSession = sessionmaker(bind=mysql_engine)
    
    sqlite_session = SQLiteSession()
    mysql_session = MySQLSession()
    
    try:
        # Get all data from SQLite table
        result = sqlite_session.execute(text(f"SELECT * FROM {table_name}"))
        rows = result.fetchall()
        
        if not rows:
            logger.info(f"No data to migrate for table: {table_name}")
            return 0
        
        # Get column names
        columns = result.keys()
        
        # Prepare data for MySQL
        for row in rows:
            # Convert row to dict
            row_dict = dict(zip(columns, row))
            
            # Handle SQLite-specific data types
            for key, value in row_dict.items():
                # Convert datetime.date to string
                if isinstance(value, datetime):
                    row_dict[key] = value.isoformat()
            
            # Insert into MySQL
            columns_str = ", ".join([f"`{col}`" for col in row_dict.keys()])
            placeholders = ", ".join([f":{col}" for col in row_dict.keys()])
            
            query = text(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})")
            mysql_session.execute(query, row_dict)
        
        # Commit changes
        mysql_session.commit()
        logger.info(f"Migrated {len(rows)} rows for table: {table_name}")
        return len(rows)
    
    except Exception as e:
        mysql_session.rollback()
        logger.error(f"Error migrating table {table_name}: {e}")
        return 0
    
    finally:
        sqlite_session.close()
        mysql_session.close()

def migrate_all_tables():
    """Migrate all tables from SQLite to MySQL."""
    logger.info("Starting migration from SQLite to MySQL...")
    
    # Create engines
    sqlite_engine = get_sqlite_engine()
    mysql_engine = get_mysql_engine()
    
    # Get table names
    sqlite_tables = get_table_names(sqlite_engine)
    mysql_tables = get_table_names(mysql_engine)
    
    logger.info(f"Found {len(sqlite_tables)} tables in SQLite: {', '.join(sqlite_tables)}")
    logger.info(f"Found {len(mysql_tables)} tables in MySQL: {', '.join(mysql_tables)}")
    
    # Check if tables exist in both databases
    common_tables = set(sqlite_tables) & set(mysql_tables)
    missing_tables = set(sqlite_tables) - set(mysql_tables)
    
    if missing_tables:
        logger.warning(f"Tables in SQLite but not in MySQL: {', '.join(missing_tables)}")
        logger.warning("Please initialize the MySQL database schema first.")
    
    # Migrate each table
    total_rows = 0
    for table in common_tables:
        rows = migrate_table(sqlite_engine, mysql_engine, table)
        total_rows += rows
    
    logger.info(f"Migration complete. Migrated {total_rows} rows across {len(common_tables)} tables.")

if __name__ == "__main__":
    try:
        migrate_all_tables()
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
