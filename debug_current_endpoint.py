#!/usr/bin/env python3
"""
Diagnostic script to test the /api/current endpoint and analyze response structure.
This script will help identify why the endpoint returns an empty array instead of a CurrentScheduleResponse object.
"""

import requests
import json
import sys
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_DATE = "2023-10-27"

def get_auth_token():
    """Get authentication token for API requests."""
    try:
        # Try to login with test credentials
        login_data = {
            "username": "admin",
            "password": "admin123"
        }

        response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_current_endpoint(token=None):
    """Test the /api/current endpoint with various scenarios."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    print("\n" + "="*60)
    print("🔍 TESTING /api/current ENDPOINT")
    print("="*60)

    # Test scenarios
    test_cases = [
        {"name": "No date parameter", "url": f"{BASE_URL}/current"},
        {"name": "With test date", "url": f"{BASE_URL}/current?date={TEST_DATE}"},
        {"name": "With current date", "url": f"{BASE_URL}/current?date={date.today().isoformat()}"}
    ]

    for test_case in test_cases:
        print(f"\n📋 Test Case: {test_case['name']}")
        print(f"🌐 URL: {test_case['url']}")

        try:
            response = requests.get(test_case['url'], headers=headers)

            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Content-Type: {response.headers.get('content-type', 'Not specified')}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"📦 Response Type: {type(data).__name__}")

                    if isinstance(data, list):
                        print(f"📋 Array Length: {len(data)}")
                        print(f"🚨 ISSUE DETECTED: Response is an array, not an object!")
                        if data:
                            print(f"📄 First Item Structure: {list(data[0].keys()) if data[0] else 'Empty item'}")
                    elif isinstance(data, dict):
                        print(f"📋 Object Keys: {list(data.keys())}")
                        if 'surgeries' in data:
                            print(f"✅ 'surgeries' key found")
                            print(f"📋 Surgeries Count: {len(data['surgeries'])}")
                            print(f"📄 Other Fields: {[k for k in data.keys() if k != 'surgeries']}")
                        else:
                            print(f"🚨 ISSUE: 'surgeries' key missing from response object")

                    # Pretty print the response for analysis
                    print(f"\n📄 Full Response:")
                    print(json.dumps(data, indent=2, default=str))

                except json.JSONDecodeError as e:
                    print(f"❌ JSON Decode Error: {e}")
                    print(f"📄 Raw Response: {response.text[:500]}...")
            else:
                print(f"❌ Error Response: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")

        print("-" * 40)

def analyze_database_state():
    """Analyze the database state to understand why no data is returned."""
    print("\n" + "="*60)
    print("🗄️ DATABASE STATE ANALYSIS")
    print("="*60)

    try:
        # Import database components
        from db_config import get_db
        from models import Surgery, OperatingRoom, Surgeon, Patient, SurgeryType

        # Get database session
        db = next(get_db())

        # Check surgery count
        surgery_count = db.query(Surgery).count()
        print(f"📊 Total Surgeries in Database: {surgery_count}")

        # Check surgeries with room assignments
        assigned_surgeries = db.query(Surgery).filter(Surgery.room_id.isnot(None)).count()
        print(f"📊 Surgeries with Room Assignments: {assigned_surgeries}")

        # Check surgeries for test date
        test_date_surgeries = db.query(Surgery).filter(Surgery.scheduled_date == TEST_DATE).count()
        print(f"📊 Surgeries for {TEST_DATE}: {test_date_surgeries}")

        # Check related tables
        room_count = db.query(OperatingRoom).count()
        surgeon_count = db.query(Surgeon).count()
        patient_count = db.query(Patient).count()
        surgery_type_count = db.query(SurgeryType).count()

        print(f"📊 Operating Rooms: {room_count}")
        print(f"📊 Surgeons: {surgeon_count}")
        print(f"📊 Patients: {patient_count}")
        print(f"📊 Surgery Types: {surgery_type_count}")

        # Sample some data
        if surgery_count > 0:
            sample_surgery = db.query(Surgery).first()
            print(f"\n📄 Sample Surgery:")
            print(f"   ID: {sample_surgery.surgery_id}")
            print(f"   Room ID: {sample_surgery.room_id}")
            print(f"   Scheduled Date: {sample_surgery.scheduled_date}")
            print(f"   Start Time: {sample_surgery.start_time}")
            print(f"   Status: {sample_surgery.status}")

        db.close()

    except Exception as e:
        print(f"❌ Database Analysis Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main diagnostic function."""
    print("🔧 DIAGNOSTIC SCRIPT: /api/current Endpoint Analysis")
    print(f"🕒 Timestamp: {datetime.now()}")
    print(f"🌐 API Base URL: {BASE_URL}")

    # Get authentication token
    print("\n🔐 Getting authentication token...")
    token = get_auth_token()

    if token:
        print(f"✅ Authentication successful")
    else:
        print(f"⚠️ Authentication failed, proceeding without token")

    # Test the endpoint
    test_current_endpoint(token)

    # Analyze database state
    analyze_database_state()

    print("\n" + "="*60)
    print("🏁 DIAGNOSTIC COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()