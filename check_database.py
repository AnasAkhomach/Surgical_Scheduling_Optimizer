#!/usr/bin/env python3
"""
Quick database check to see what tables and columns exist
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import inspect, text
from db_config import engine

def check_database():
    """Check database structure"""
    try:
        inspector = inspect(engine)
        
        print("🔍 Database Structure Check")
        print("=" * 50)
        
        # Get all tables
        tables = inspector.get_table_names()
        print(f"📋 Available tables: {tables}")
        
        # Check surgery table specifically
        if 'surgery' in tables:
            print("\n🏥 Surgery table columns:")
            columns = inspector.get_columns('surgery')
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("\n❌ Surgery table not found!")
        
        # Check if we have any data
        with engine.connect() as conn:
            if 'surgery' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM surgery"))
                count = result.scalar()
                print(f"\n📊 Surgery records: {count}")
            
            if 'operatingroom' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM operatingroom"))
                count = result.scalar()
                print(f"📊 Operating room records: {count}")
            
            if 'staff' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM staff"))
                count = result.scalar()
                print(f"📊 Staff records: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

if __name__ == "__main__":
    check_database()
