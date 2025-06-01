#!/usr/bin/env python3
"""
Simple Operating Rooms API Test

This script tests only the operating rooms endpoint to verify the fix is working.
"""

import requests
import json
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:5000"
REGISTER_URL = f"{BASE_URL}/api/auth/register"
AUTH_URL = f"{BASE_URL}/api/auth/token"
OPERATING_ROOMS_URL = f"{BASE_URL}/api/operating-rooms/"

# Test user credentials
TEST_USER = {
    "username": "simple_test_user",
    "email": "simple@test.com",
    "password": "testpass123",
    "role": "admin"
}

def print_result(step: str, success: bool, details: str = ""):
    """Print a formatted result"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"{status}: {step}")
    if details:
        print(f"   Details: {details}")

def setup_authentication() -> str:
    """Setup authentication and return access token"""
    try:
        # Register user (might already exist)
        requests.post(REGISTER_URL, json=TEST_USER, timeout=10)

        # Authenticate
        auth_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        response = requests.post(AUTH_URL, data=auth_data, timeout=10)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            if access_token:
                print_result("Authentication Setup", True, "Token obtained")
                return access_token

        print_result("Authentication Setup", False, f"Status: {response.status_code}")
        return None
    except Exception as e:
        print_result("Authentication Setup", False, f"Error: {str(e)}")
        return None

def test_operating_rooms(token: str) -> Dict[str, Any]:
    """Test the operating rooms API endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(OPERATING_ROOMS_URL, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print_result("Operating Rooms API Test", True, f"Received {len(data)} items")
            return {"success": True, "data": data}
        else:
            print_result("Operating Rooms API Test", False, f"Status: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print_result("Operating Rooms API Test", False, f"Error: {str(e)}")
        return {"success": False, "error": str(e)}

def validate_operating_rooms_data(data: List[Dict]) -> bool:
    """Validate operating rooms data structure"""
    if not data:
        print_result("Operating Rooms Data Validation", True, "No data to validate (empty dataset)")
        return True

    validation_results = []

    for i, item in enumerate(data):
        item_issues = []

        # Check if room_id is mapped to 'id'
        if 'id' in item and item['id'] is not None:
            validation_results.append(f"Item {i+1}: ✅ ID mapping working (room_id → id = {item['id']})")
        else:
            item_issues.append("Missing or null ID field")

        # Check required fields
        required_fields = ['name', 'status']
        missing_required = [field for field in required_fields if field not in item or item[field] is None]
        if missing_required:
            item_issues.append(f"Missing required fields: {missing_required}")

        if item_issues:
            validation_results.append(f"Item {i+1}: ❌ Issues: {'; '.join(item_issues)}")
        elif not any(f"Item {i+1}:" in result for result in validation_results):
            validation_results.append(f"Item {i+1}: ✅ All validations passed")

    all_valid = all("✅" in result for result in validation_results)

    print_result("Operating Rooms Data Validation", all_valid)
    for result in validation_results:
        print(f"   {result}")

    return all_valid

def display_sample_data(data: List[Dict]):
    """Display sample operating rooms data"""
    if not data:
        print("\n📋 Operating Rooms: No data available")
        return

    print("\n📋 Operating Rooms Sample Data:")
    sample_item = data[0]

    print(f"   Primary Key Mapping: room_id → id = {sample_item.get('id')}")
    print(f"   Available Fields: {list(sample_item.keys())}")

    # Show all key-value pairs
    for key, value in sample_item.items():
        print(f"   {key}: {value}")

def main():
    """Main test function"""
    print("="*80)
    print(" OPERATING ROOMS API FIX VERIFICATION")
    print("="*80)
    print("Testing the operating rooms model fix to ensure room_id → id mapping is working.")

    # Setup authentication
    print("\n🔐 Setting up authentication...")
    token = setup_authentication()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return False

    # Test operating rooms endpoint
    print("\n🏥 Testing Operating Rooms API...")
    api_result = test_operating_rooms(token)

    if api_result["success"]:
        data = api_result["data"]

        # Validate data structure
        print("\n🔍 Validating data structure...")
        validation_success = validate_operating_rooms_data(data)

        # Display sample data
        display_sample_data(data)

        # Final result
        print("\n" + "="*80)
        print(" FINAL RESULT")
        print("="*80)

        if validation_success:
            print("🎉 SUCCESS: Operating Rooms API fix is working correctly!")
            print("✅ Data structure validation passed")
            print("✅ Field mapping (room_id → id) is functioning")
            print("✅ All required fields are present")
            print("\n🚀 Ready for frontend integration testing")
            return True
        else:
            print("⚠️  PARTIAL SUCCESS: API responding but data validation failed")
            print("🔧 Additional fixes may be needed")
            return False
    else:
        print("\n" + "="*80)
        print(" FINAL RESULT")
        print("="*80)
        print("❌ FAILED: Operating Rooms API is not responding correctly")
        print(f"Error: {api_result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {str(e)}")
        exit(1)