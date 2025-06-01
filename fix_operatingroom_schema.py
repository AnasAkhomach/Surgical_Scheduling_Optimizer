#!/usr/bin/env python3
"""
Script to fix the operating room table schema by adding missing columns.
"""

import logging
from sqlalchemy import text
from db_config import get_db, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = '{table_name}'
                AND COLUMN_NAME = '{column_name}'
            """))
            return result.fetchone()[0] > 0
    except Exception as e:
        logger.error(f"Error checking column {column_name}: {e}")
        return False

def add_column_if_missing(table_name, column_name, column_definition):
    """Add a column to a table if it doesn't exist."""
    if not check_column_exists(table_name, column_name):
        try:
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"))
                conn.commit()
                logger.info(f"✅ Added column {column_name} to {table_name}")
                return True
        except Exception as e:
            logger.error(f"❌ Error adding column {column_name}: {e}")
            return False
    else:
        logger.info(f"ℹ️  Column {column_name} already exists in {table_name}")
        return True

def fix_operatingroom_schema():
    """Fix the operating room table schema."""
    logger.info("🔧 Fixing operating room table schema...")

    # Check current table structure
    try:
        with engine.connect() as conn:
            result = conn.execute(text("DESCRIBE operatingroom"))
            current_columns = [row[0] for row in result.fetchall()]
            logger.info(f"Current columns in operatingroom: {current_columns}")
    except Exception as e:
        logger.error(f"Error describing table: {e}")
        return False

    # Define required columns
    required_columns = {
        'name': 'VARCHAR(255) NOT NULL DEFAULT "Operating Room"',
        'status': 'VARCHAR(50) NOT NULL DEFAULT "Active"',
        'primary_service': 'VARCHAR(255) NULL'
    }

    success = True
    for column_name, column_def in required_columns.items():
        if not add_column_if_missing('operatingroom', column_name, column_def):
            success = False

    if success:
        logger.info("✅ Operating room schema fix completed successfully!")

        # Update existing records with default values
        try:
            with engine.connect() as conn:
                # Update name column for existing records
                conn.execute(text("""
                    UPDATE operatingroom
                    SET name = CONCAT('Operating Room ', room_id)
                    WHERE name IS NULL OR name = ''
                """))

                # Update status for existing records
                conn.execute(text("""
                    UPDATE operatingroom
                    SET status = 'Active'
                    WHERE status IS NULL OR status = ''
                """))

                conn.commit()
                logger.info("✅ Updated existing records with default values")
        except Exception as e:
            logger.error(f"❌ Error updating existing records: {e}")

    return success

def verify_schema():
    """Verify the schema is correct."""
    logger.info("🔍 Verifying schema...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("DESCRIBE operatingroom"))
            columns = result.fetchall()

            logger.info("Final operatingroom table structure:")
            for column in columns:
                logger.info(f"  {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")

            # Test a simple query
            result = conn.execute(text("SELECT room_id, name, location, status, primary_service FROM operatingroom LIMIT 1"))
            test_row = result.fetchone()
            if test_row:
                logger.info(f"✅ Test query successful: {test_row}")
            else:
                logger.info("ℹ️  No data in operatingroom table")

    except Exception as e:
        logger.error(f"❌ Schema verification failed: {e}")
        return False

    return True

def main():
    """Main function."""
    logger.info("🚀 Starting operating room schema fix...")

    if fix_operatingroom_schema():
        if verify_schema():
            logger.info("🎉 Schema fix completed successfully!")
            return True

    logger.error("❌ Schema fix failed")
    return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)