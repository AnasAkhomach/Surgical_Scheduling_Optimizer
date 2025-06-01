#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv

def debug_authentication_issue():
    """Comprehensive authentication debugging"""
    print("Authentication Issue Debug")
    print("=" * 40)

    # Load environment variables
    if os.path.exists(".env"):
        print("✅ Loading .env file")
        load_dotenv()
    else:
        print("❌ No .env file found")

    # Get configuration
    secret_key = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
    algorithm = os.getenv("ALGORITHM", "HS256")
    print(f"SECRET_KEY: {secret_key}")
    print(f"ALGORITHM: {algorithm}")

    base_url = "http://localhost:5000"

    try:
        # Step 1: Authenticate and get token
        print("\n1. Authenticating...")
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

        # Step 2: Decode token with the same SECRET_KEY
        print("\n2. Decoding token with backend SECRET_KEY...")
        try:
            decoded = jwt.decode(access_token, secret_key, algorithms=[algorithm])
            print(f"✅ Token decoded successfully: {json.dumps(decoded, indent=2)}")

            # Check expiration
            exp_timestamp = decoded.get('exp')
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                now = datetime.now()
                print(f"Token expires: {exp_datetime}")
                print(f"Current time: {now}")
                print(f"Token valid: {exp_datetime > now}")

                if exp_datetime <= now:
                    print("❌ TOKEN HAS EXPIRED!")
                    return False

        except jwt.ExpiredSignatureError:
            print("❌ Token has expired")
            return False
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid token: {e}")
            return False
        except Exception as e:
            print(f"❌ Token decode error: {e}")
            return False

        # Step 3: Test /api/current endpoint
        print("\n3. Testing /api/current endpoint...")
        headers = {"Authorization": f"Bearer {access_token}"}

        current_response = requests.get(f"{base_url}/api/current", headers=headers)
        print(f"Current endpoint status: {current_response.status_code}")

        if current_response.status_code == 200:
            print("✅ SUCCESS: /api/current working correctly")
            return True
        elif current_response.status_code == 401:
            print("❌ 401 Unauthorized - Token validation failed on backend")
            print(f"Response: {current_response.text}")

            # Additional debugging
            print("\n4. Additional debugging...")
            print("Checking if backend is using different SECRET_KEY...")

            # Try to decode with default key
            try:
                default_key = "your-secret-key-for-development-only"
                decoded_default = jwt.decode(access_token, default_key, algorithms=[algorithm])
                print(f"✅ Token decodes with default key: {decoded_default}")
            except Exception as e:
                print(f"❌ Token doesn't decode with default key: {e}")

            return False
        else:
            print(f"❌ Unexpected status: {current_response.status_code}")
            print(f"Response: {current_response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = debug_authentication_issue()
    print("\n" + "=" * 40)
    if success:
        print("🎉 AUTHENTICATION DEBUG COMPLETED SUCCESSFULLY!")
    else:
        print("❌ AUTHENTICATION ISSUE IDENTIFIED")