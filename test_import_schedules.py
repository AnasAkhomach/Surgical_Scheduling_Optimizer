#!/usr/bin/env python3
"""
Test script to check if schedules router can be imported without errors
"""

import sys
import traceback

def test_import():
    """Test importing the schedules router"""
    try:
        print("Testing import of schedules router...")

        # Test basic imports first
        print("1. Testing basic imports...")
        from api import models
        print("   ✅ api.models imported successfully")

        from api import schemas
        print("   ✅ api.schemas imported successfully")

        # Test the schedules router import
        print("2. Testing schedules router import...")
        from api.routers import schedules
        print("   ✅ api.routers.schedules imported successfully")

        # Test specific models used in the endpoint
        print("3. Testing specific models...")
        print(f"   - CurrentScheduleResponse: {hasattr(models, 'CurrentScheduleResponse')}")
        print(f"   - ScheduleAssignment: {hasattr(models, 'ScheduleAssignment')}")

        if hasattr(models, 'CurrentScheduleResponse'):
            print(f"   - CurrentScheduleResponse fields: {models.CurrentScheduleResponse.__annotations__ if hasattr(models.CurrentScheduleResponse, '__annotations__') else 'No annotations'}")

        if hasattr(models, 'ScheduleAssignment'):
            print(f"   - ScheduleAssignment fields: {models.ScheduleAssignment.__annotations__ if hasattr(models.ScheduleAssignment, '__annotations__') else 'No annotations'}")

        print("\n✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing schedules router imports")
    print("=" * 60)

    success = test_import()

    print("\n" + "=" * 60)
    if success:
        print("Import test completed successfully")
    else:
        print("Import test failed")
        sys.exit(1)