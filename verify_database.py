"""
Database verification script.

This script verifies the database configuration, connection, and schema.
It can be used to check if the database is properly set up.
"""

import os
import sys
import logging
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from tabulate import tabulate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from db_config import engine, DATABASE_URL, Base
import models

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def verify_connection():
    """Verify database connection."""
    print_header("Database Connection")
    
    try:
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            print(f"✅ Successfully connected to the database: {DATABASE_URL}")
            
            # Determine database type
            is_mysql = DATABASE_URL.startswith('mysql')
            is_sqlite = DATABASE_URL.startswith('sqlite')
            
            if is_mysql:
                print("Database type: MySQL")
                # Check MySQL version
                version = connection.execute(text("SELECT VERSION()")).scalar()
                print(f"MySQL version: {version}")
            elif is_sqlite:
                print("Database type: SQLite")
                # Check SQLite version
                version = connection.execute(text("SELECT sqlite_version()")).scalar()
                print(f"SQLite version: {version}")
                
                # Check database file
                db_path = DATABASE_URL.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    size = os.path.getsize(db_path)
                    print(f"SQLite database file: {db_path} (Size: {size/1024:.2f} KB)")
                else:
                    print(f"⚠️ SQLite database file not found: {db_path}")
            else:
                print(f"Database type: Unknown ({DATABASE_URL.split(':')[0]})")
                
            return True
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {e}")
        return False

def verify_tables():
    """Verify database tables."""
    print_header("Database Tables")
    
    try:
        # Get the inspector
        inspector = inspect(engine)
        
        # Get all table names
        tables = inspector.get_table_names()
        
        if not tables:
            print("⚠️ No tables found in the database.")
            return False
        
        print(f"✅ Found {len(tables)} tables in the database:")
        
        # Get expected tables from models
        expected_tables = set()
        for name, obj in vars(models).items():
            if isinstance(obj, type) and issubclass(obj, Base) and obj != Base:
                if hasattr(obj, '__tablename__'):
                    expected_tables.add(obj.__tablename__)
        
        # Check for missing tables
        missing_tables = expected_tables - set(tables)
        if missing_tables:
            print(f"⚠️ Missing tables: {', '.join(missing_tables)}")
        
        # Check for extra tables
        extra_tables = set(tables) - expected_tables
        if extra_tables:
            print(f"ℹ️ Extra tables (not defined in models): {', '.join(extra_tables)}")
        
        # Print table details
        table_data = []
        for table in sorted(tables):
            columns = inspector.get_columns(table)
            primary_keys = [pk for pk in inspector.get_pk_constraint(table)['constrained_columns']]
            foreign_keys = inspector.get_foreign_keys(table)
            
            table_data.append([
                table,
                len(columns),
                ", ".join(primary_keys),
                len(foreign_keys)
            ])
        
        print(tabulate(
            table_data,
            headers=["Table Name", "Columns", "Primary Keys", "Foreign Keys"],
            tablefmt="grid"
        ))
        
        return True
    except SQLAlchemyError as e:
        print(f"❌ Error verifying tables: {e}")
        return False

def verify_data():
    """Verify database data."""
    print_header("Database Data")
    
    try:
        # Get the inspector
        inspector = inspect(engine)
        
        # Get all table names
        tables = inspector.get_table_names()
        
        # Check row counts for each table
        table_data = []
        with engine.connect() as connection:
            for table in sorted(tables):
                try:
                    result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    table_data.append([table, count])
                except SQLAlchemyError as e:
                    table_data.append([table, f"Error: {e}"])
        
        print(tabulate(
            table_data,
            headers=["Table Name", "Row Count"],
            tablefmt="grid"
        ))
        
        # Check for empty tables
        empty_tables = [table for table, count in table_data if count == 0]
        if empty_tables:
            print(f"⚠️ Empty tables: {', '.join(empty_tables)}")
        
        return True
    except SQLAlchemyError as e:
        print(f"❌ Error verifying data: {e}")
        return False

def verify_constraints():
    """Verify database constraints."""
    print_header("Database Constraints")
    
    try:
        # Get the inspector
        inspector = inspect(engine)
        
        # Get all table names
        tables = inspector.get_table_names()
        
        # Check constraints for each table
        for table in sorted(tables):
            print(f"\nTable: {table}")
            
            # Primary keys
            pk_constraint = inspector.get_pk_constraint(table)
            if pk_constraint['constrained_columns']:
                print(f"  Primary Key: {', '.join(pk_constraint['constrained_columns'])}")
            else:
                print("  ⚠️ No Primary Key defined")
            
            # Foreign keys
            foreign_keys = inspector.get_foreign_keys(table)
            if foreign_keys:
                print(f"  Foreign Keys ({len(foreign_keys)}):")
                for fk in foreign_keys:
                    print(f"    {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}")
            else:
                print("  ℹ️ No Foreign Keys defined")
            
            # Indexes
            indexes = inspector.get_indexes(table)
            if indexes:
                print(f"  Indexes ({len(indexes)}):")
                for idx in indexes:
                    unique = "UNIQUE " if idx['unique'] else ""
                    print(f"    {unique}Index {idx['name']} on {', '.join(idx['column_names'])}")
            else:
                print("  ℹ️ No Indexes defined")
        
        return True
    except SQLAlchemyError as e:
        print(f"❌ Error verifying constraints: {e}")
        return False

def run_verification():
    """Run all verification checks."""
    print_header("Database Verification")
    print(f"Database URL: {DATABASE_URL}")
    
    connection_ok = verify_connection()
    if not connection_ok:
        print("❌ Database connection failed. Cannot proceed with further checks.")
        return False
    
    tables_ok = verify_tables()
    data_ok = verify_data()
    constraints_ok = verify_constraints()
    
    print_header("Verification Summary")
    print(f"Connection: {'✅ OK' if connection_ok else '❌ Failed'}")
    print(f"Tables: {'✅ OK' if tables_ok else '⚠️ Issues found'}")
    print(f"Data: {'✅ OK' if data_ok else '⚠️ Issues found'}")
    print(f"Constraints: {'✅ OK' if constraints_ok else '⚠️ Issues found'}")
    
    return all([connection_ok, tables_ok, data_ok, constraints_ok])

if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
