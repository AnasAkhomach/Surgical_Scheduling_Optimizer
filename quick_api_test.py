#!/usr/bin/env python3
"""
Quick API test to diagnose authentication and basic connectivity
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health Check Error: {e}")
        return False

def test_register():
    """Test user registration"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
        print(f"Register Status: {response.status_code}")
        print(f"Register Response: {response.text}")
        return response.status_code in [200, 201, 400]  # 400 if user already exists
    except Exception as e:
        print(f"Register Error: {e}")
        return False

def test_auth():
    """Test authentication"""
    try:
        # Try to login using correct endpoint and format with admin credentials
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={
                "username": "admin",
                "password": "admin123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"Auth Status: {response.status_code}")
        print(f"Auth Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"Token received: {token[:20] if token else 'None'}...")
            return token
        else:
            print(f"Auth failed: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Auth Error: {e}")
        return None

def test_endpoints_without_auth():
    """Test endpoints that might not require auth"""
    endpoints = [
        "/operating-rooms",
        "/staff",
        "/schedules/current",
        "/sdst/matrix"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"{endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text[:100]}")
        except Exception as e:
            print(f"{endpoint}: Error - {e}")

def test_authenticated_endpoints(token):
    """Test endpoints with authentication"""
    headers = {"Authorization": f"Bearer {token}"}
    endpoints = [
        "/operating-rooms",
        "/staff",
        "/schedules/current",
        "/sdst/matrix"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"{endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text[:100]}")
        except Exception as e:
            print(f"{endpoint}: Error - {e}")

def main():
    print("🔍 Quick API Diagnostic Test")
    print("=" * 40)

    print("\n1. Testing Health Endpoint...")
    health_ok = test_health()

    print("\n2. Testing User Registration...")
    register_ok = test_register()

    print("\n3. Testing Authentication...")
    token = test_auth()
    auth_ok = token is not None

    if token:
        print("\n4. Testing Authenticated Endpoints...")
        test_authenticated_endpoints(token)
    else:
        print("\n4. Testing Unauthenticated Endpoints...")
        test_endpoints_without_auth()

    print("\n" + "=" * 40)
    print(f"Health: {'✅' if health_ok else '❌'}")
    print(f"Register: {'✅' if register_ok else '❌'}")
    print(f"Auth: {'✅' if auth_ok else '❌'}")

if __name__ == "__main__":
    main()
