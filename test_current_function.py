#!/usr/bin/env python3
"""
Direct test of the get_current_schedule function to isolate the issue.
"""

import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from db_config import get_db
from api.models import User
from api.routers.schedules import get_current_schedule
import asyncio
import json

def test_function_directly():
    """Test the get_current_schedule function directly."""
    print("🔧 DIRECT FUNCTION TEST")
    print("=" * 50)

    try:
        # Get database session
        db = next(get_db())

        # Create a mock user (since we need authentication)
        mock_user = User(
            user_id=1,
            username="test",
            email="test@example.com",
            role="admin",
            is_active=True
        )

        # Test the function
        print("📋 Testing get_current_schedule function...")

        # Since it's an async function, we need to run it properly
        async def run_test():
            result = await get_current_schedule(
                date=None,  # No date filter
                db=db,
                current_user=mock_user
            )
            return result

        # Run the async function
        result = asyncio.run(run_test())

        print(f"📦 Result Type: {type(result).__name__}")
        print(f"📄 Result: {result}")

        # Check if it's the expected type
        if hasattr(result, 'surgeries'):
            print(f"✅ Has 'surgeries' attribute")
            print(f"📋 Surgeries count: {len(result.surgeries)}")
            print(f"📄 Other attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
        else:
            print(f"🚨 Missing 'surgeries' attribute")
            print(f"📄 Available attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")

        # Try to serialize to JSON to see what the API would return
        try:
            if hasattr(result, 'dict'):
                json_data = result.dict()
                print(f"\n📄 JSON Serialization:")
                print(json.dumps(json_data, indent=2, default=str))
            else:
                print(f"\n📄 Direct JSON attempt:")
                print(json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"❌ JSON Serialization Error: {e}")

        db.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🏁 TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_function_directly()