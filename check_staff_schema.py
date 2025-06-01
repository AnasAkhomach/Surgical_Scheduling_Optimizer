#!/usr/bin/env python3
"""
Check staff table schema to debug the duplicate FROM clause issue
"""

import mysql.connector
from db_config import get_db_url
import re

def check_staff_schema():
    try:
        # Parse database URL
        url = get_db_url()
        match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', url)

        if not match:
            print("❌ Could not parse database URL")
            return

        host = match.group(3)
        user = match.group(1)
        password = match.group(2)
        database = match.group(5)

        print(f"Connecting to database: {database} at {host}")

        # Connect to database
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = conn.cursor()

        # Check table structure
        print("\n=== STAFF TABLE SCHEMA ===")
        cursor.execute('DESCRIBE staff')
        for row in cursor.fetchall():
            print(row)

        # Check create table statement
        print("\n=== CREATE TABLE STATEMENT ===")
        cursor.execute('SHOW CREATE TABLE staff')
        for row in cursor.fetchall():
            print(row[1])

        # Check if there are any views or triggers
        print("\n=== CHECKING FOR VIEWS ===")
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
        views = cursor.fetchall()
        if views:
            print("Found views:")
            for view in views:
                print(view)
        else:
            print("No views found")

        conn.close()
        print("\n✅ Database schema check completed")

    except Exception as e:
        print(f"❌ Error checking database schema: {e}")

if __name__ == "__main__":
    check_staff_schema()