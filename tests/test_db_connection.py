import sys
import os
import logging
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from db_config import engine, DATABASE_URL

def test_connection():
    """Test the database connection and report on the database status."""
    try:
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Successfully connected to the database!")

            # Determine database type
            is_mysql = DATABASE_URL.startswith('mysql')
            is_sqlite = DATABASE_URL.startswith('sqlite')

            if is_mysql:
                print(f"Database type: MySQL")
                test_mysql_connection(connection)
            elif is_sqlite:
                print(f"Database type: SQLite")
                test_sqlite_connection(connection)
            else:
                print(f"Database type: Unknown ({DATABASE_URL.split(':')[0]})")

    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {e}")

def test_mysql_connection(connection):
    """Test MySQL-specific connection details."""
    try:
        # Check if our database exists
        db_name = DATABASE_URL.split('/')[-1]
        db_result = connection.execute(text(f"SHOW DATABASES LIKE '{db_name}'"))
        if db_result.rowcount > 0:
            print(f"✅ The '{db_name}' database exists!")
        else:
            print(f"❌ The '{db_name}' database does not exist yet.")

        # Check if any tables exist in our database
        try:
            connection.execute(text(f"USE {db_name}"))
            table_result = connection.execute(text("SHOW TABLES"))
            tables = table_result.fetchall()

            if tables:
                print(f"✅ Found {len(tables)} tables in the database:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("⚠️ No tables found in the database yet.")
        except SQLAlchemyError as e:
            print(f"❌ Error checking tables: {e}")

        # Check database version
        version_result = connection.execute(text("SELECT VERSION()"))
        version = version_result.scalar()
        print(f"MySQL version: {version}")

    except SQLAlchemyError as e:
        print(f"❌ Error during MySQL tests: {e}")

def test_sqlite_connection(connection):
    """Test SQLite-specific connection details."""
    try:
        # Get the inspector
        inspector = inspect(engine)

        # Get all table names
        tables = inspector.get_table_names()

        if tables:
            print(f"✅ Found {len(tables)} tables in the SQLite database:")
            for table in tables:
                print(f"  - {table}")
        else:
            print("⚠️ No tables found in the SQLite database yet.")

        # Check SQLite version
        version_result = connection.execute(text("SELECT sqlite_version()"))
        version = version_result.scalar()
        print(f"SQLite version: {version}")

        # Check database file
        db_path = DATABASE_URL.replace('sqlite:///', '')
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"SQLite database file: {db_path} (Size: {size/1024:.2f} KB)")
        else:
            print(f"SQLite database file not found: {db_path}")

    except SQLAlchemyError as e:
        print(f"❌ Error during SQLite tests: {e}")

if __name__ == "__main__":
    print("Testing database connection...")
    print(f"Database URL: {DATABASE_URL}")
    test_connection()