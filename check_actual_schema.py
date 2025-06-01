#!/usr/bin/env python3
"""
Check actual database schema vs model definition
"""

from sqlalchemy import create_engine, text
from db_config import get_database_url

def check_actual_schema():
    try:
        engine = create_engine(get_database_url())

        with engine.connect() as conn:
            print("=== ACTUAL STAFF TABLE COLUMNS ===")
            result = conn.execute(text('DESCRIBE staff'))
            actual_columns = []
            for row in result:
                column_name = row[0]
                column_type = row[1]
                actual_columns.append(column_name)
                print(f"  {column_name} - {column_type}")

            print("\n=== MODEL EXPECTED COLUMNS ===")
            from models import Staff
            model_columns = list(Staff.__table__.columns.keys())
            for col in model_columns:
                print(f"  {col}")

            print("\n=== COLUMN COMPARISON ===")
            missing_in_db = set(model_columns) - set(actual_columns)
            extra_in_db = set(actual_columns) - set(model_columns)

            if missing_in_db:
                print(f"❌ Columns missing in database: {missing_in_db}")
            if extra_in_db:
                print(f"⚠️  Extra columns in database: {extra_in_db}")
            if not missing_in_db and not extra_in_db:
                print("✅ All columns match")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_actual_schema()