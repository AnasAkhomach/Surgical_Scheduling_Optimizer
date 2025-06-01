#!/usr/bin/env python3
"""
Fix staff table schema to match the model definition
"""

from sqlalchemy import create_engine, text
from db_config import get_database_url

def fix_staff_schema():
    try:
        engine = create_engine(get_database_url())

        with engine.connect() as conn:
            print("=== FIXING STAFF TABLE SCHEMA ===")

            # Start transaction
            trans = conn.begin()

            try:
                # 1. Add the missing 'status' column
                print("1. Adding 'status' column...")
                conn.execute(text("""
                    ALTER TABLE staff
                    ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'Active'
                """))
                print("   ✅ Status column added")

                # 2. Rename 'specialization' to 'specializations' and change type to TEXT
                print("2. Renaming 'specialization' to 'specializations' and changing type...")
                conn.execute(text("""
                    ALTER TABLE staff
                    CHANGE COLUMN specialization specializations TEXT
                """))
                print("   ✅ Specializations column updated")

                # 3. Verify the changes
                print("\n3. Verifying changes...")
                result = conn.execute(text('DESCRIBE staff'))
                print("Updated staff table columns:")
                for row in result:
                    print(f"  {row[0]} - {row[1]}")

                # Commit the transaction
                trans.commit()
                print("\n✅ Schema migration completed successfully!")

            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Migration failed, rolled back: {e}")
                raise

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_staff_schema()