#!/usr/bin/env python3
"""
Fix surgeryequipmentusage table schema by adding missing time columns
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text, inspect
from db_config import engine

def fix_equipment_usage_schema():
    """Fix the surgeryequipmentusage table schema"""
    try:
        print("🔧 Fixing SurgeryEquipmentUsage Table Schema")
        print("=" * 50)
        
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            
            try:
                # Check current schema
                inspector = inspect(engine)
                
                # Check if table exists
                if 'surgeryequipmentusage' not in inspector.get_table_names():
                    print("❌ surgeryequipmentusage table does not exist")
                    return False
                
                columns = inspector.get_columns('surgeryequipmentusage')
                column_names = [col['name'] for col in columns]
                
                print(f"📋 Current columns: {column_names}")
                
                # Check if we need to add the missing columns
                has_usage_start_time = 'usage_start_time' in column_names
                has_usage_end_time = 'usage_end_time' in column_names
                
                if has_usage_start_time and has_usage_end_time:
                    print("✅ Schema is already correct!")
                    return True
                
                # Add missing columns
                if not has_usage_start_time:
                    print("🔧 Adding usage_start_time column...")
                    conn.execute(text(
                        "ALTER TABLE surgeryequipmentusage ADD COLUMN usage_start_time DATETIME"
                    ))
                
                if not has_usage_end_time:
                    print("🔧 Adding usage_end_time column...")
                    conn.execute(text(
                        "ALTER TABLE surgeryequipmentusage ADD COLUMN usage_end_time DATETIME"
                    ))
                
                # Update existing records with default values if any exist
                result = conn.execute(text("SELECT COUNT(*) FROM surgeryequipmentusage"))
                record_count = result.scalar()
                
                if record_count > 0:
                    print(f"📊 Updating {record_count} existing records...")
                    
                    # Set default times based on surgery times if available
                    conn.execute(text("""
                        UPDATE surgeryequipmentusage seu
                        JOIN surgery s ON seu.surgery_id = s.surgery_id
                        SET seu.usage_start_time = s.start_time,
                            seu.usage_end_time = s.end_time
                        WHERE seu.usage_start_time IS NULL OR seu.usage_end_time IS NULL
                    """))
                    
                    # For any remaining NULL values, set to current time
                    conn.execute(text("""
                        UPDATE surgeryequipmentusage 
                        SET usage_start_time = NOW(),
                            usage_end_time = DATE_ADD(NOW(), INTERVAL 1 HOUR)
                        WHERE usage_start_time IS NULL OR usage_end_time IS NULL
                    """))
                
                # Commit the transaction
                trans.commit()
                
                # Verify the changes
                print("\n🔍 Verifying changes...")
                inspector = inspect(engine)
                columns = inspector.get_columns('surgeryequipmentusage')
                column_names = [col['name'] for col in columns]
                print(f"📋 Updated columns: {column_names}")
                
                # Check if the required columns are now present
                if 'usage_start_time' in column_names and 'usage_end_time' in column_names:
                    print("✅ Schema fix completed successfully!")
                    return True
                else:
                    print("❌ Schema fix failed - columns still missing")
                    return False
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Schema fix failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_equipment_usage_schema()
    sys.exit(0 if success else 1)
