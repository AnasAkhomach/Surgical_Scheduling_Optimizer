#!/usr/bin/env python3
"""
Fix surgery data by adding proper start and end times
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from datetime import datetime, timedelta
from db_config import engine

def fix_surgery_data():
    """Fix surgery data with proper start and end times"""
    try:
        print("🔧 Fixing Surgery Data")
        print("=" * 50)
        
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            
            try:
                # Get all surgeries with NULL start_time or end_time
                result = conn.execute(text("""
                    SELECT surgery_id, scheduled_date, duration_minutes, status
                    FROM surgery 
                    WHERE start_time IS NULL OR end_time IS NULL
                """))
                
                surgeries = result.fetchall()
                print(f"📊 Found {len(surgeries)} surgeries needing time updates")
                
                # Update each surgery with proper times
                base_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
                current_time = base_date
                
                for i, (surgery_id, scheduled_date, duration_minutes, status) in enumerate(surgeries):
                    # Calculate start and end times
                    start_time = current_time + timedelta(hours=i * 2)  # Space surgeries 2 hours apart
                    end_time = start_time + timedelta(minutes=duration_minutes)
                    
                    # Update the surgery
                    conn.execute(text("""
                        UPDATE surgery 
                        SET start_time = :start_time, 
                            end_time = :end_time,
                            scheduled_date = :scheduled_date,
                            status = 'Scheduled'
                        WHERE surgery_id = :surgery_id
                    """), {
                        "surgery_id": surgery_id,
                        "start_time": start_time,
                        "end_time": end_time,
                        "scheduled_date": start_time.date()
                    })
                    
                    print(f"✅ Updated surgery {surgery_id}: {start_time} - {end_time}")
                
                # Also ensure we have some surgeries scheduled for today
                today = datetime.now().date()
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM surgery 
                    WHERE DATE(scheduled_date) = :today AND status = 'Scheduled'
                """), {"today": today})
                
                today_count = result.scalar()
                print(f"📅 Surgeries scheduled for today: {today_count}")
                
                if today_count == 0:
                    # Schedule some surgeries for today
                    print("📅 Adding surgeries for today...")
                    
                    # Get some existing surgeries and reschedule them for today
                    result = conn.execute(text("""
                        SELECT surgery_id, duration_minutes 
                        FROM surgery 
                        LIMIT 3
                    """))
                    
                    surgeries_to_reschedule = result.fetchall()
                    today_start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
                    
                    for i, (surgery_id, duration_minutes) in enumerate(surgeries_to_reschedule):
                        start_time = today_start + timedelta(hours=i * 2)
                        end_time = start_time + timedelta(minutes=duration_minutes)
                        
                        conn.execute(text("""
                            UPDATE surgery 
                            SET scheduled_date = :scheduled_date,
                                start_time = :start_time,
                                end_time = :end_time,
                                status = 'Scheduled'
                            WHERE surgery_id = :surgery_id
                        """), {
                            "surgery_id": surgery_id,
                            "scheduled_date": today,
                            "start_time": start_time,
                            "end_time": end_time
                        })
                        
                        print(f"📅 Rescheduled surgery {surgery_id} for today: {start_time}")
                
                # Commit the transaction
                trans.commit()
                
                # Verify the changes
                print("\n🔍 Verifying changes...")
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM surgery 
                    WHERE start_time IS NOT NULL AND end_time IS NOT NULL
                """))
                valid_count = result.scalar()
                
                result = conn.execute(text("SELECT COUNT(*) FROM surgery"))
                total_count = result.scalar()
                
                print(f"📊 Surgeries with valid times: {valid_count}/{total_count}")
                
                # Check today's schedule
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM surgery 
                    WHERE DATE(scheduled_date) = :today AND status = 'Scheduled'
                """), {"today": datetime.now().date()})
                
                today_scheduled = result.scalar()
                print(f"📅 Surgeries scheduled for today: {today_scheduled}")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Data fix failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_surgery_data()
    sys.exit(0 if success else 1)
