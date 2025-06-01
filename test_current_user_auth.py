#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timedelta
import jwt

def test_current_user_authentication():
    """Test the current user authentication flow and token validation"""
    base_url = "http://localhost:5000"

    print("Testing Current User Authentication")
    print("=" * 40)

    try:
        # Step 1: Test authentication with admin credentials
        print("\n1. Testing authentication...")
        auth_data = {
            "username": "admin",
            "password": "admin123"
        }

        auth_response = requests.post(f"{base_url}/api/auth/token", data=auth_data)
        print(f"Auth Status: {auth_response.status_code}")

        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.text}")
            return False

        token_data = auth_response.json()
        access_token = token_data.get("access_token")
        print(f"✅ Token obtained: {access_token[:30]}...")

        # Step 2: Decode and inspect the token
        print("\n2. Inspecting token...")
        try:
            # Decode without verification to inspect payload
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            print(f"Token payload: {json.dumps(decoded, indent=2)}")

            # Check expiration
            exp_timestamp = decoded.get('exp')
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                now = datetime.now()
                print(f"Token expires: {exp_datetime}")
                print(f"Current time: {now}")
                print(f"Token valid: {exp_datetime > now}")

                if exp_datetime <= now:
                    print("❌ Token has expired!")
                    return False

        except Exception as e:
            print(f"⚠️ Could not decode token: {e}")

        # Step 3: Test /api/current endpoint
        print("\n3. Testing /api/current endpoint...")
        headers = {"Authorization": f"Bearer {access_token}"}

        current_response = requests.get(f"{base_url}/api/current", headers=headers)
        print(f"Current endpoint status: {current_response.status_code}")

        if current_response.status_code == 200:
            print("✅ SUCCESS: /api/current working correctly")
            data = current_response.json()
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        else:
            print(f"❌ FAILED: {current_response.status_code}")
            print(f"Response: {current_response.text}")
            return False

        # Step 4: Test with date parameter
        print("\n4. Testing /api/current with date parameter...")
        date_response = requests.get(f"{base_url}/api/current?date=2023-10-27", headers=headers)
        print(f"Date endpoint status: {date_response.status_code}")

        if date_response.status_code == 200:
            print("✅ SUCCESS: /api/current with date working correctly")
            return True
        else:
            print(f"❌ FAILED: {date_response.status_code}")
            print(f"Response: {date_response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_current_user_authentication()
    print("\n" + "=" * 40)
    if success:
        print("🎉 AUTHENTICATION TEST PASSED!")
    else:
        print("❌ AUTHENTICATION TEST FAILED")