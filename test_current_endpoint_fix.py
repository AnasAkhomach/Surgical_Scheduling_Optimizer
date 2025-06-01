#!/usr/bin/env python3
"""
Test script for the /api/current endpoint fix
"""
import requests
import json
import sys

def test_current_endpoint():
    """Test the /api/current endpoint"""
    url = "http://localhost:5001/api/current"

    try:
        print(f"Testing endpoint: {url}")
        # TODO: Replace with a valid token
        token = "YOUR_ACCESS_TOKEN"
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        if response.status_code == 200:
            try:
                data = response.json()
                print("\n=== Response Data ===")
                print(json.dumps(data, indent=2, default=str))

                # Check if response has expected structure
                if isinstance(data, dict) and 'surgeries' in data:
                    print("\n✅ SUCCESS: Response has expected object structure with 'surgeries' field")
                    print(f"   - surgeries type: {type(data['surgeries'])}")
                    print(f"   - surgeries length: {len(data['surgeries']) if isinstance(data['surgeries'], list) else 'N/A'}")

                    # Check other expected fields
                    expected_fields = ['date', 'total_count', 'status']
                    for field in expected_fields:
                        if field in data:
                            print(f"   - {field}: {data[field]}")
                        else:
                            print(f"   - {field}: MISSING")
                else:
                    print("\n❌ FAIL: Response does not have expected structure")
                    print(f"   - Response type: {type(data)}")
                    if isinstance(data, list):
                        print(f"   - Response length: {len(data)}")

            except json.JSONDecodeError as e:
                print(f"\n❌ JSON Decode Error: {e}")
                print(f"Raw response: {response.text[:500]}")

        elif response.status_code == 404:
            print("\n⚠️  No current schedule found (404) - this is expected if no data exists")
            try:
                error_data = response.json()
                print(f"Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
        else:
            print(f"\n❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the API server")
        print("   Make sure the API server is running on http://localhost:5001")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Testing /api/current endpoint fix")
    print("=" * 60)

    success = test_current_endpoint()

    print("\n" + "=" * 60)
    if success:
        print("Test completed successfully")
    else:
        print("Test failed")
        sys.exit(1)