#!/usr/bin/env python3
"""
Debug staff model to find the duplicate FROM clause issue
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db_config import get_database_url, get_db
from models import Staff
import traceback

def debug_staff_model():
    try:
        print("=== DEBUGGING STAFF MODEL ===")

        # Get database session
        db = next(get_db())

        print("\n1. Testing simple Staff query...")
        try:
            # Try the exact query that's failing
            staff_query = db.query(Staff)
            print(f"Query object created: {staff_query}")

            # Get the SQL statement
            sql_statement = str(staff_query.statement.compile(compile_kwargs={"literal_binds": True}))
            print(f"Generated SQL: {sql_statement}")

            # Try to execute with limit
            staff_with_limit = staff_query.offset(0).limit(100)
            sql_with_limit = str(staff_with_limit.statement.compile(compile_kwargs={"literal_binds": True}))
            print(f"SQL with limit: {sql_with_limit}")

            # Try to execute
            result = staff_with_limit.all()
            print(f"✅ Query executed successfully, found {len(result)} staff members")

        except Exception as e:
            print(f"❌ Query failed: {e}")
            print(f"Error type: {type(e)}")
            traceback.print_exc()

        print("\n2. Checking Staff model definition...")
        print(f"Table name: {Staff.__tablename__}")
        print(f"Primary key: {Staff.__table__.primary_key}")
        print(f"Columns: {list(Staff.__table__.columns.keys())}")

        print("\n3. Testing raw SQL query...")
        try:
            raw_result = db.execute(text("SELECT COUNT(*) FROM staff"))
            count = raw_result.scalar()
            print(f"✅ Raw SQL query successful, staff count: {count}")
        except Exception as e:
            print(f"❌ Raw SQL query failed: {e}")

        db.close()

    except Exception as e:
        print(f"❌ General error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_staff_model()