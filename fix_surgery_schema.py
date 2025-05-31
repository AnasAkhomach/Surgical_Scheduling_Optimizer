#!/usr/bin/env python3
"""
Fix surgery table schema by migrating from surgery_type to surgery_type_id
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text, inspect
from db_config import engine
from models import SurgeryType

def fix_surgery_schema():
    """Fix the surgery table schema"""
    try:
        print("🔧 Fixing Surgery Table Schema")
        print("=" * 50)
        
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            
            try:
                # Check current schema
                inspector = inspect(engine)
                columns = inspector.get_columns('surgery')
                column_names = [col['name'] for col in columns]
                
                print(f"📋 Current columns: {column_names}")
                
                # Check if we need to migrate
                has_surgery_type = 'surgery_type' in column_names
                has_surgery_type_id = 'surgery_type_id' in column_names
                
                if has_surgery_type_id and not has_surgery_type:
                    print("✅ Schema is already correct!")
                    return True
                
                if has_surgery_type and not has_surgery_type_id:
                    print("🔄 Migrating from surgery_type to surgery_type_id...")
                    
                    # Step 1: Create surgery types if they don't exist
                    print("📝 Creating surgery types...")
                    surgery_types = [
                        ("Appendectomy", "Removal of the appendix"),
                        ("Knee Replacement", "Total knee arthroplasty"),
                        ("Craniotomy", "Surgical opening of the skull"),
                        ("Coronary Bypass", "Coronary artery bypass grafting"),
                        ("Hip Arthroscopy", "Minimally invasive hip surgery"),
                        ("Gallbladder Surgery", "Laparoscopic cholecystectomy"),
                        ("Hernia Repair", "Inguinal hernia repair"),
                        ("Cataract Surgery", "Phacoemulsification"),
                        ("Tonsillectomy", "Removal of tonsils"),
                        ("Arthroscopy", "Joint examination and repair")
                    ]
                    
                    # Insert surgery types if they don't exist
                    for name, description in surgery_types:
                        result = conn.execute(text(
                            "SELECT COUNT(*) FROM surgerytype WHERE name = :name"
                        ), {"name": name})
                        
                        if result.scalar() == 0:
                            conn.execute(text(
                                "INSERT INTO surgerytype (name, description, average_duration) VALUES (:name, :description, 60)"
                            ), {"name": name, "description": description})
                    
                    # Step 2: Add surgery_type_id column
                    print("🔧 Adding surgery_type_id column...")
                    conn.execute(text(
                        "ALTER TABLE surgery ADD COLUMN surgery_type_id INTEGER"
                    ))
                    
                    # Step 3: Populate surgery_type_id based on surgery_type
                    print("📊 Populating surgery_type_id...")
                    
                    # Get all unique surgery types from the surgery table
                    result = conn.execute(text("SELECT DISTINCT surgery_type FROM surgery WHERE surgery_type IS NOT NULL"))
                    existing_types = [row[0] for row in result]
                    
                    for surgery_type_name in existing_types:
                        # Get the type_id for this surgery type
                        result = conn.execute(text(
                            "SELECT type_id FROM surgerytype WHERE name = :name"
                        ), {"name": surgery_type_name})
                        
                        type_id_row = result.fetchone()
                        if type_id_row:
                            type_id = type_id_row[0]
                            
                            # Update all surgeries with this type
                            conn.execute(text(
                                "UPDATE surgery SET surgery_type_id = :type_id WHERE surgery_type = :name"
                            ), {"type_id": type_id, "name": surgery_type_name})
                        else:
                            # Create a new surgery type for unknown types
                            conn.execute(text(
                                "INSERT INTO surgerytype (name, description, average_duration) VALUES (:name, :description, 60)"
                            ), {"name": surgery_type_name, "description": f"Auto-created for {surgery_type_name}"})
                            
                            # Get the new type_id
                            result = conn.execute(text(
                                "SELECT type_id FROM surgerytype WHERE name = :name"
                            ), {"name": surgery_type_name})
                            type_id = result.scalar()
                            
                            # Update surgeries
                            conn.execute(text(
                                "UPDATE surgery SET surgery_type_id = :type_id WHERE surgery_type = :name"
                            ), {"type_id": type_id, "name": surgery_type_name})
                    
                    # Step 4: Set default surgery_type_id for any NULL values
                    print("🔧 Setting default values...")
                    result = conn.execute(text("SELECT type_id FROM surgerytype LIMIT 1"))
                    default_type_id = result.scalar()
                    
                    if default_type_id:
                        conn.execute(text(
                            "UPDATE surgery SET surgery_type_id = :type_id WHERE surgery_type_id IS NULL"
                        ), {"type_id": default_type_id})
                    
                    # Step 5: Add foreign key constraint
                    print("🔗 Adding foreign key constraint...")
                    conn.execute(text(
                        "ALTER TABLE surgery ADD CONSTRAINT fk_surgery_type_id FOREIGN KEY (surgery_type_id) REFERENCES surgerytype(type_id)"
                    ))
                    
                    # Step 6: Drop the old surgery_type column
                    print("🗑️ Removing old surgery_type column...")
                    conn.execute(text("ALTER TABLE surgery DROP COLUMN surgery_type"))
                    
                    print("✅ Schema migration completed successfully!")
                
                # Commit the transaction
                trans.commit()
                
                # Verify the changes
                print("\n🔍 Verifying changes...")
                inspector = inspect(engine)
                columns = inspector.get_columns('surgery')
                column_names = [col['name'] for col in columns]
                print(f"📋 Updated columns: {column_names}")
                
                # Check data
                result = conn.execute(text("SELECT COUNT(*) FROM surgery WHERE surgery_type_id IS NOT NULL"))
                count = result.scalar()
                print(f"📊 Surgeries with surgery_type_id: {count}")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_surgery_schema()
    sys.exit(0 if success else 1)
