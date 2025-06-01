#!/usr/bin/env python3
"""
Comprehensive Model Fix Verification Script

This script tests all the data structure fixes applied to resolve frontend-backend integration issues:
1. Operating Room model fix (already completed)
2. Surgery model fix (newly applied)
3. Staff model fix (newly applied)
4. Appointment model fix (newly applied)

Each model now properly maps their primary key to 'id' field for frontend compatibility.
"""

import requests
import json
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:5000"
REGISTER_URL = f"{BASE_URL}/api/auth/register"
AUTH_URL = f"{BASE_URL}/api/auth/token"

# API endpoints to test
ENDPOINTS = {
    "operating_rooms": "/api/operating-rooms/",
    "surgeries": "/api/surgeries/",
    "staff": "/api/staff/",
    "appointments": "/api/appointments/"
}

# Expected field mappings for each model
FIELD_MAPPINGS = {
    "operating_rooms": {
        "primary_key": "room_id",
        "required_fields": ["id", "name", "status"],
        "optional_fields": ["location", "primary_service"]
    },
    "surgeries": {
        "primary_key": "surgery_id",
        "required_fields": ["id", "surgery_type_id", "duration_minutes"],
        "optional_fields": ["patient_id", "surgeon_id", "room_id", "start_time", "end_time", "status"]
    },
    "staff": {
        "primary_key": "staff_id",
        "required_fields": ["id", "name", "role"],
        "optional_fields": ["email", "phone", "status", "specialization"]
    },
    "appointments": {
        "primary_key": "appointment_id",
        "required_fields": ["id", "patient_id", "surgeon_id", "appointment_date"],
        "optional_fields": ["room_id", "status", "notes"]
    }
}

# Test user credentials
TEST_USER = {
    "username": "model_test_user",
    "email": "models@test.com",
    "password": "testpass123",
    "role": "admin"
}

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}")

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

def test_endpoint(endpoint_name: str, endpoint_path: str, token: str) -> Dict[str, Any]:
    """Test a specific API endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BASE_URL}{endpoint_path}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print_result(f"{endpoint_name.title()} API Test", True, f"Received {len(data)} items")
            return {"success": True, "data": data}
        else:
            print_result(f"{endpoint_name.title()} API Test", False, f"Status: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print_result(f"{endpoint_name.title()} API Test", False, f"Error: {str(e)}")
        return {"success": False, "error": str(e)}

def validate_field_mapping(endpoint_name: str, data: List[Dict]) -> bool:
    """Validate field mapping for a specific endpoint"""
    if not data:
        print_result(f"{endpoint_name.title()} Field Mapping", True, "No data to validate (empty dataset)")
        return True

    mapping_config = FIELD_MAPPINGS.get(endpoint_name, {})
    primary_key = mapping_config.get("primary_key")
    required_fields = mapping_config.get("required_fields", [])

    validation_results = []

    for i, item in enumerate(data):
        item_issues = []

        # Check if primary key is mapped to 'id'
        if primary_key and 'id' in item:
            if item['id'] is not None:
                validation_results.append(f"Item {i+1}: ✅ ID mapping working ({primary_key} → id)")
            else:
                item_issues.append("ID field is null")
        elif primary_key:
            item_issues.append(f"Missing ID field (should map from {primary_key})")

        # Check required fields
        missing_required = [field for field in required_fields if field not in item or item[field] is None]
        if missing_required:
            item_issues.append(f"Missing required fields: {missing_required}")

        if item_issues:
            validation_results.append(f"Item {i+1}: ❌ Issues: {'; '.join(item_issues)}")
        elif not any(f"Item {i+1}:" in result for result in validation_results):
            validation_results.append(f"Item {i+1}: ✅ All validations passed")

    all_valid = all("✅" in result for result in validation_results)

    print_result(f"{endpoint_name.title()} Field Mapping Validation", all_valid)
    for result in validation_results[:5]:  # Show first 5 items
        print(f"   {result}")

    if len(validation_results) > 5:
        print(f"   ... and {len(validation_results) - 5} more items")

    return all_valid

def display_sample_data(endpoint_name: str, data: List[Dict]):
    """Display sample data for an endpoint"""
    if not data:
        print(f"\n📋 {endpoint_name.title()}: No data available")
        return

    print(f"\n📋 {endpoint_name.title()} Sample Data:")
    sample_item = data[0]

    # Show key fields
    mapping_config = FIELD_MAPPINGS.get(endpoint_name, {})
    primary_key = mapping_config.get("primary_key")

    print(f"   Primary Key Mapping: {primary_key} → id = {sample_item.get('id')}")
    print(f"   Available Fields: {list(sample_item.keys())}")

    # Show first few key-value pairs
    for key, value in list(sample_item.items())[:6]:
        print(f"   {key}: {value}")

    if len(sample_item) > 6:
        print(f"   ... and {len(sample_item) - 6} more fields")

def generate_integration_report(results: Dict[str, Dict]):
    """Generate a comprehensive integration report"""
    print_section("INTEGRATION REPORT SUMMARY")

    total_endpoints = len(results)
    successful_endpoints = sum(1 for result in results.values() if result.get("api_success") and result.get("validation_success"))

    print(f"📊 Overall Integration Status: {successful_endpoints}/{total_endpoints} endpoints working")

    print(f"\n🔍 Detailed Results:")
    for endpoint_name, result in results.items():
        api_status = "✅" if result.get("api_success") else "❌"
        validation_status = "✅" if result.get("validation_success") else "❌"
        data_count = len(result.get("data", []))

        print(f"   {endpoint_name.title()}:")
        print(f"     API Response: {api_status} ({data_count} items)")
        print(f"     Field Mapping: {validation_status}")

        if not result.get("api_success"):
            print(f"     Error: {result.get('error', 'Unknown error')}")

    print(f"\n🎯 Integration Status:")
    if successful_endpoints == total_endpoints:
        print("   🎉 ALL MODELS FIXED: Complete integration success!")
        print("   ✅ All data structure mismatches have been resolved")
        print("   ✅ Frontend-backend field mapping is working correctly")
        print("   ✅ All models now provide consistent 'id' field mapping")
        print("\n🚀 Ready for:")
        print("   - Complete frontend integration testing")
        print("   - End-to-end application testing")
        print("   - Production deployment preparation")
    else:
        print(f"   ⚠️  PARTIAL SUCCESS: {successful_endpoints}/{total_endpoints} models working")
        print("   🔧 Additional fixes may be needed for failed endpoints")
        print("   📋 Review error details above for specific issues")

def main():
    """Main test function"""
    print_section("COMPREHENSIVE MODEL FIX VERIFICATION")
    print("Testing all data structure fixes applied to resolve frontend-backend integration issues.")
    print("\nModels being tested:")
    for endpoint_name, endpoint_path in ENDPOINTS.items():
        mapping = FIELD_MAPPINGS[endpoint_name]
        print(f"- {endpoint_name.title()}: {mapping['primary_key']} → id mapping")

    # Setup authentication
    print_section("AUTHENTICATION SETUP")
    token = setup_authentication()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return False

    # Test all endpoints
    results = {}

    for endpoint_name, endpoint_path in ENDPOINTS.items():
        print_section(f"TESTING {endpoint_name.upper()} MODEL")

        # Test API endpoint
        api_result = test_endpoint(endpoint_name, endpoint_path, token)

        if api_result["success"]:
            data = api_result["data"]

            # Validate field mapping
            validation_success = validate_field_mapping(endpoint_name, data)

            # Display sample data
            display_sample_data(endpoint_name, data)

            results[endpoint_name] = {
                "api_success": True,
                "validation_success": validation_success,
                "data": data
            }
        else:
            results[endpoint_name] = {
                "api_success": False,
                "validation_success": False,
                "error": api_result.get("error", "Unknown error"),
                "data": []
            }

    # Generate comprehensive report
    generate_integration_report(results)

    # Return overall success
    all_successful = all(result.get("api_success") and result.get("validation_success")
                        for result in results.values())

    return all_successful

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