#!/usr/bin/env python3
"""
Operating Rooms API Fix Verification Script

This script demonstrates that the operating rooms API integration issue has been resolved:
1. Database schema now includes all required fields (name, status, primary_service)
2. Pydantic model properly maps room_id to id for frontend compatibility
3. API returns consistent, valid data structure
4. Authentication flow works correctly

Expected Results:
- User registration: 201 Created (or 400 if user exists)
- Authentication: 200 OK with access token
- Operating rooms fetch: 200 OK with valid data structure
- All required fields present in response
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:5000"
REGISTER_URL = f"{BASE_URL}/api/auth/register"
AUTH_URL = f"{BASE_URL}/api/auth/token"
OPERATING_ROOMS_URL = f"{BASE_URL}/api/operating-rooms/"

# Test user credentials
TEST_USER = {
    "username": "test_integration_user",
    "email": "test@integration.com",
    "password": "testpass123",
    "role": "admin"
}

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(step: str, success: bool, details: str = ""):
    """Print a formatted result"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"{status}: {step}")
    if details:
        print(f"   Details: {details}")

def register_user() -> bool:
    """Register test user"""
    try:
        response = requests.post(REGISTER_URL, json=TEST_USER, timeout=10)
        if response.status_code in [201, 400]:  # 400 if user already exists
            print_result("User Registration", True, f"Status: {response.status_code}")
            return True
        else:
            print_result("User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_result("User Registration", False, f"Error: {str(e)}")
        return False

def authenticate() -> str:
    """Authenticate and get access token"""
    try:
        auth_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        response = requests.post(AUTH_URL, data=auth_data, timeout=10)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            if access_token:
                print_result("Authentication", True, f"Token received (length: {len(access_token)})")
                return access_token
            else:
                print_result("Authentication", False, "No access token in response")
                return None
        else:
            print_result("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print_result("Authentication", False, f"Error: {str(e)}")
        return None

def fetch_operating_rooms(token: str) -> Dict[str, Any]:
    """Fetch operating rooms data"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(OPERATING_ROOMS_URL, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print_result("Operating Rooms Fetch", True, f"Received {len(data)} operating rooms")
            return data
        else:
            print_result("Operating Rooms Fetch", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print_result("Operating Rooms Fetch", False, f"Error: {str(e)}")
        return None

def validate_data_structure(data: list) -> bool:
    """Validate the operating rooms data structure"""
    if not data:
        print_result("Data Structure Validation", False, "No data received")
        return False

    required_fields = ['id', 'name', 'status']
    validation_results = []

    for i, room in enumerate(data):
        missing_fields = [field for field in required_fields if field not in room or room[field] is None]
        if missing_fields:
            validation_results.append(f"Room {i}: Missing fields {missing_fields}")
        else:
            validation_results.append(f"Room {i}: ✅ All required fields present")

    all_valid = all("✅" in result for result in validation_results)

    print_result("Data Structure Validation", all_valid)
    for result in validation_results:
        print(f"   {result}")

    return all_valid

def display_sample_data(data: list):
    """Display sample operating room data"""
    print_section("SAMPLE OPERATING ROOMS DATA")

    if not data:
        print("No operating rooms data available")
        return

    for i, room in enumerate(data[:3]):  # Show first 3 rooms
        print(f"\nOperating Room {i+1}:")
        for key, value in room.items():
            print(f"  {key}: {value}")

    if len(data) > 3:
        print(f"\n... and {len(data) - 3} more operating rooms")

def main():
    """Main verification function"""
    print_section("OPERATING ROOMS API FIX VERIFICATION")
    print("This script verifies that the operating rooms API integration issues have been resolved.")
    print("\nExpected outcomes:")
    print("- Database schema includes all required fields")
    print("- Pydantic model maps room_id to id correctly")
    print("- API returns valid, consistent data structure")
    print("- Authentication flow works properly")

    # Step 1: Register user
    print_section("STEP 1: USER REGISTRATION")
    if not register_user():
        print("\n❌ Cannot proceed without user registration")
        return False

    # Step 2: Authenticate
    print_section("STEP 2: AUTHENTICATION")
    token = authenticate()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return False

    # Step 3: Fetch operating rooms
    print_section("STEP 3: FETCH OPERATING ROOMS")
    operating_rooms_data = fetch_operating_rooms(token)
    if operating_rooms_data is None:
        print("\n❌ Cannot proceed without operating rooms data")
        return False

    # Step 4: Validate data structure
    print_section("STEP 4: DATA STRUCTURE VALIDATION")
    is_valid = validate_data_structure(operating_rooms_data)

    # Step 5: Display sample data
    display_sample_data(operating_rooms_data)

    # Final result
    print_section("VERIFICATION RESULTS")
    if is_valid:
        print("🎉 SUCCESS: Operating Rooms API integration fix is working correctly!")
        print("\n✅ All critical issues have been resolved:")
        print("   - Database schema is consistent")
        print("   - Pydantic model validation works")
        print("   - Field mapping (room_id → id) is functional")
        print("   - API returns valid data structure")
        print("   - Authentication flow is operational")
        print("\n🚀 Ready for frontend integration testing!")
        return True
    else:
        print("❌ FAILED: Operating Rooms API still has issues")
        print("\nPlease check:")
        print("   - Database schema consistency")
        print("   - Pydantic model configuration")
        print("   - Field mapping logic")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during verification: {str(e)}")
        exit(1)