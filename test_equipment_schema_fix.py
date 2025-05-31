#!/usr/bin/env python3
"""
Test script to verify the equipment usage schema fix.
This test ensures that SurgeryEquipmentUsage model has correct schema fields.
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import SurgeryEquipmentUsage

def test_surgery_equipment_usage_schema():
    """Test that SurgeryEquipmentUsage has the correct schema fields."""
    
    print("🔍 Testing SurgeryEquipmentUsage schema fields...")
    
    # Check that the model has the correct fields
    required_fields = [
        'usage_id',
        'surgery_id', 
        'equipment_id',
        'usage_start_time',
        'usage_end_time'
    ]
    
    # Check that deprecated fields don't exist
    deprecated_fields = ['quantity']
    
    # Get the model's columns
    model_columns = [column.name for column in SurgeryEquipmentUsage.__table__.columns]
    
    print(f"   Model columns found: {model_columns}")
    
    # Verify required fields exist
    missing_fields = []
    for field in required_fields:
        if field not in model_columns:
            missing_fields.append(field)
    
    # Verify deprecated fields don't exist
    found_deprecated = []
    for field in deprecated_fields:
        if field in model_columns:
            found_deprecated.append(field)
    
    # Report results
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        return False
    
    if found_deprecated:
        print(f"❌ Found deprecated fields that should be removed: {found_deprecated}")
        return False
    
    print("✅ All required schema fields present")
    print("✅ No deprecated fields found")
    print("✅ SurgeryEquipmentUsage schema is correct!")
    
    return True

def test_equipment_usage_creation():
    """Test that SurgeryEquipmentUsage can be created with correct fields."""
    
    print("\n🔍 Testing SurgeryEquipmentUsage creation...")
    
    try:
        # Create a SurgeryEquipmentUsage instance with correct fields
        start_time = datetime(2023, 10, 27, 8, 0, 0)
        end_time = datetime(2023, 10, 27, 9, 30, 0)
        
        usage_record = SurgeryEquipmentUsage(
            surgery_id=1,
            equipment_id=1,
            usage_start_time=start_time,
            usage_end_time=end_time
        )
        
        # Verify the fields are set correctly
        assert usage_record.surgery_id == 1
        assert usage_record.equipment_id == 1
        assert usage_record.usage_start_time == start_time
        assert usage_record.usage_end_time == end_time
        
        print("✅ SurgeryEquipmentUsage created successfully with correct fields")
        print(f"   - surgery_id: {usage_record.surgery_id}")
        print(f"   - equipment_id: {usage_record.equipment_id}")
        print(f"   - usage_start_time: {usage_record.usage_start_time}")
        print(f"   - usage_end_time: {usage_record.usage_end_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create SurgeryEquipmentUsage: {e}")
        return False

def test_deprecated_quantity_field():
    """Test that the deprecated 'quantity' field cannot be used."""
    
    print("\n🔍 Testing that deprecated 'quantity' field is not accessible...")
    
    try:
        # Try to create with the old quantity field - this should fail
        usage_record = SurgeryEquipmentUsage(
            surgery_id=1,
            equipment_id=1,
            quantity=1  # This should cause an error
        )
        
        print("❌ ERROR: SurgeryEquipmentUsage accepted deprecated 'quantity' field!")
        return False
        
    except TypeError as e:
        if "quantity" in str(e):
            print("✅ Deprecated 'quantity' field correctly rejected")
            print(f"   Error message: {e}")
            return True
        else:
            print(f"❌ Unexpected TypeError: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_scheduling_optimizer_code_fix():
    """Test that the scheduling_optimizer.py code has been fixed."""
    
    print("\n🔍 Testing scheduling_optimizer.py code fix...")
    
    try:
        # Read the scheduling_optimizer.py file
        with open('scheduling_optimizer.py', 'r') as f:
            content = f.read()
        
        # Check that the old quantity field usage is removed
        if 'quantity=quantity' in content:
            print("❌ Found old 'quantity=quantity' usage in scheduling_optimizer.py")
            return False
        
        # Check that the new usage_start_time and usage_end_time fields are used
        if 'usage_start_time=' not in content:
            print("❌ Missing 'usage_start_time=' in scheduling_optimizer.py")
            return False
            
        if 'usage_end_time=' not in content:
            print("❌ Missing 'usage_end_time=' in scheduling_optimizer.py")
            return False
        
        print("✅ scheduling_optimizer.py code has been fixed correctly")
        print("   - Old 'quantity' field usage removed")
        print("   - New 'usage_start_time' and 'usage_end_time' fields added")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to check scheduling_optimizer.py: {e}")
        return False

def run_equipment_schema_tests():
    """Run all equipment schema fix tests."""
    print("🧪 Running Equipment Schema Fix Tests")
    print("=" * 50)
    
    tests = [
        ("Schema Fields Check", test_surgery_equipment_usage_schema),
        ("Equipment Usage Creation", test_equipment_usage_creation),
        ("Deprecated Field Rejection", test_deprecated_quantity_field),
        ("Scheduling Optimizer Code Fix", test_scheduling_optimizer_code_fix),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Running: {test_name}")
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Equipment Schema Fix Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All equipment schema fix tests passed!")
        print("✅ The SurgeryEquipmentUsage schema fix is working correctly!")
        return True
    else:
        print("⚠️  Some tests failed. The schema fix needs attention.")
        return False

if __name__ == "__main__":
    success = run_equipment_schema_tests()
    sys.exit(0 if success else 1)
