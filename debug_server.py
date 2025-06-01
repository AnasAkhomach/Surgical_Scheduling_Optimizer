#!/usr/bin/env python3
"""
Debug script to identify why the FastAPI server is crashing.
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Starting debug server...")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

try:
    print("\n1. Testing basic imports...")
    import uvicorn
    print("✓ uvicorn imported successfully")

    from fastapi import FastAPI
    print("✓ FastAPI imported successfully")

    print("\n2. Testing database configuration...")
    from db_config import get_database_url, DATABASE_URL
    print(f"✓ Database URL: {DATABASE_URL}")

    print("\n3. Testing models import...")
    import models
    print("✓ Models imported successfully")

    print("\n4. Testing database initialization...")
    from db_config import init_db
    init_db()
    print("✓ Database initialized successfully")

    print("\n5. Testing FastAPI app import...")
    from api.main import app
    print("✓ FastAPI app imported successfully")

    print("\n6. Starting server manually...")
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=5000,
        reload=False,
        log_level="debug"
    )

except Exception as e:
    print(f"\n❌ Error occurred: {e}")
    print(f"Exception type: {type(e).__name__}")
    print(f"\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)