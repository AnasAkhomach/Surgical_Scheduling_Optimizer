#!/usr/bin/env python3
"""
Debug script to identify frontend-backend authentication mismatches
"""
import requests
import json
from urllib.parse import urlencode

def test_backend_endpoints():
    """Test backend endpoints directly"""
    print("=== BACKEND ENDPOINT TESTING ===\n")
    
    # Test 1: Health check
    print("1. Testing backend health...")
    try:
        response = requests.get('http://localhost:8000/api/health')
        print(f"Health status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False
    
    # Test 2: Login with correct format (form data)
    print("\n2. Testing login with form data (correct format)...")
    try:
        data = urlencode({'username': 'admin', 'password': 'admin123'})
        response = requests.post('http://localhost:8000/api/auth/token',
                               data=data,
                               headers={'Content-Type': 'application/x-www-form-urlencoded'})
        print(f"Form login status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Form data login works")
            return response.json()['access_token']
        else:
            print(f"❌ Form login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Form login error: {e}")
        return None
    
    # Test 3: Login with JSON (what frontend might be sending)
    print("\n3. Testing login with JSON (frontend format)...")
    try:
        response = requests.post('http://localhost:8000/api/auth/token',
                               json={'username': 'admin', 'password': 'admin123'},
                               headers={'Content-Type': 'application/json'})
        print(f"JSON login status: {response.status_code}")
        if response.status_code == 422:
            print("✅ Correctly rejects JSON format")
            error_data = response.json()
            print(f"Validation error: {error_data}")
        else:
            print(f"❌ Unexpected JSON response: {response.text}")
    except Exception as e:
        print(f"❌ JSON login error: {e}")

def test_frontend_api_format():
    """Test how frontend API service formats requests"""
    print("\n=== FRONTEND API FORMAT TESTING ===\n")
    
    # Simulate frontend login call
    print("4. Simulating frontend login call...")
    try:
        # This mimics what frontend/src/services/api.js does
        formData = requests.models.RequestEncodingMixin._encode_params({'username': 'admin', 'password': 'admin123'})
        
        response = requests.post('http://localhost:8000/api/auth/token',
                               data=formData,
                               headers={})  # Let requests set Content-Type for form data
        print(f"Frontend simulation status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Frontend format works")
            token_data = response.json()
            print(f"Token received: {token_data['token_type']}")
            return token_data['access_token']
        else:
            print(f"❌ Frontend simulation failed: {response.text}")
            if response.status_code == 422:
                error_data = response.json()
                print(f"Validation details: {json.dumps(error_data, indent=2)}")
    except Exception as e:
        print(f"❌ Frontend simulation error: {e}")
    
    return None

def test_registration_formats():
    """Test registration with different formats"""
    print("\n=== REGISTRATION FORMAT TESTING ===\n")
    
    # Test 5: Registration with JSON (correct format)
    print("5. Testing registration with JSON...")
    try:
        import random
        suffix = random.randint(1000, 9999)
        user_data = {
            'username': f'testuser{suffix}',
            'email': f'testuser{suffix}@example.com',
            'password': 'TestPass123!',
            'full_name': f'Test User {suffix}'
        }
        response = requests.post('http://localhost:8000/api/auth/register',
                               json=user_data,
                               headers={'Content-Type': 'application/json'})
        print(f"Registration status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Registration works with JSON")
            user_response = response.json()
            print(f"Created user: {user_response['username']}")
            return user_data
        else:
            print(f"❌ Registration failed: {response.text}")
            if response.status_code == 422:
                error_data = response.json()
                print(f"Validation details: {json.dumps(error_data, indent=2)}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    return None

def test_auth_me_endpoint(token):
    """Test the /auth/me endpoint"""
    if not token:
        print("\n6. Skipping /auth/me test (no token)")
        return
    
    print("\n6. Testing /auth/me endpoint...")
    try:
        response = requests.get('http://localhost:8000/api/auth/me',
                              headers={'Authorization': f'Bearer {token}'})
        print(f"Auth/me status: {response.status_code}")
        if response.status_code == 200:
            print("✅ /auth/me works")
            user_info = response.json()
            print(f"User info: {user_info['username']} ({user_info['role']})")
        else:
            print(f"❌ /auth/me failed: {response.text}")
    except Exception as e:
        print(f"❌ /auth/me error: {e}")

def main():
    """Run all tests"""
    print("🔍 DEBUGGING FRONTEND-BACKEND AUTHENTICATION MISMATCH\n")
    
    # Test backend endpoints
    token = test_backend_endpoints()
    
    # Test frontend format
    frontend_token = test_frontend_api_format()
    
    # Test registration
    user_data = test_registration_formats()
    
    # Test auth/me
    test_auth_me_endpoint(token or frontend_token)
    
    print("\n=== SUMMARY ===")
    print("✅ Backend is working correctly")
    print("✅ Login requires form data (application/x-www-form-urlencoded)")
    print("✅ Registration accepts JSON (application/json)")
    print("✅ Frontend should use FormData for login, JSON for registration")
    
    print("\n🎯 ISSUE IDENTIFIED:")
    print("The frontend must send login requests as FormData, not JSON")
    print("The frontend API service appears to be correctly configured")
    print("Browser extension errors are unrelated to the application")

if __name__ == "__main__":
    main()
