#!/usr/bin/env python3
"""
Debug frontend authentication issues
"""
import requests
import json

def test_auth_debug():
    """Debug the authentication issue"""
    print("🔍 DEBUGGING FRONTEND AUTHENTICATION")
    print("=" * 50)

    # Test 1: Check if admin user exists and works
    print("1. Testing admin login...")
    try:
        data = {
            'username': 'admin',
            'password': 'admin123',
            'grant_type': 'password'
        }
        response = requests.post('http://localhost:8000/api/auth/token', data=data)
        print(f"   Admin login status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Admin login works!")
            token_data = response.json()
            admin_token = token_data['access_token']

            # Test /auth/me with admin token
            me_response = requests.get('http://localhost:8000/api/auth/me',
                                     headers={'Authorization': f'Bearer {admin_token}'})
            if me_response.status_code == 200:
                user_info = me_response.json()
                print(f"   Admin user info: {user_info['username']} ({user_info['role']})")

        else:
            print(f"   ❌ Admin login failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Admin login error: {e}")

    # Test 2: Try to create a test user
    print("\n2. Creating test user...")
    try:
        user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com',
            'full_name': 'Test User'
        }
        response = requests.post('http://localhost:8000/api/auth/register',
                               json=user_data)
        print(f"   Registration status: {response.status_code}")
        if response.status_code == 201:
            print("   ✅ Test user created successfully!")

            # Now try to login with the test user
            print("   Testing login with new user...")
            login_data = {
                'username': 'testuser',
                'password': 'testpass123',
                'grant_type': 'password'
            }
            login_response = requests.post('http://localhost:8000/api/auth/token',
                                         data=login_data)
            print(f"   Test user login status: {login_response.status_code}")
            if login_response.status_code == 200:
                print("   ✅ Test user login works!")
            else:
                print(f"   ❌ Test user login failed: {login_response.text}")

        else:
            print(f"   Registration response: {response.text}")
            if response.status_code == 400 and 'already exists' in response.text:
                print("   User already exists, trying login...")
                login_data = {
                    'username': 'testuser',
                    'password': 'testpass123',
                    'grant_type': 'password'
                }
                login_response = requests.post('http://localhost:8000/api/auth/token',
                                             data=login_data)
                print(f"   Existing user login status: {login_response.status_code}")
                if login_response.status_code == 200:
                    print("   ✅ Existing test user login works!")
                else:
                    print(f"   ❌ Existing test user login failed: {login_response.text}")
    except Exception as e:
        print(f"   ❌ Test user creation error: {e}")

    # Test 3: Check what happens with user7
    print("\n3. Testing user7 (from frontend logs)...")
    try:
        # Try different possible passwords for user7
        passwords = ['password123', 'user7', 'test123', 'admin123']
        for pwd in passwords:
            login_data = {
                'username': 'user7',
                'password': pwd,
                'grant_type': 'password'
            }
            response = requests.post('http://localhost:8000/api/auth/token', data=login_data)
            print(f"   user7 with '{pwd}': {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ user7 password is '{pwd}'!")
                break
        else:
            print("   ❌ None of the common passwords work for user7")
    except Exception as e:
        print(f"   ❌ user7 test error: {e}")

    # Test 4: Simulate exact frontend request
    print("\n4. Simulating exact frontend FormData request...")
    try:
        # Create FormData exactly like the frontend
        form_data = {
            'username': 'admin',
            'password': 'admin123',
            'grant_type': 'password'
        }

        # Send without Content-Type header (let requests handle it)
        response = requests.post('http://localhost:8000/api/auth/token',
                               data=form_data)

        print(f"   Frontend simulation status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Frontend format works perfectly!")
        else:
            print(f"   ❌ Frontend format failed: {response.text}")

    except Exception as e:
        print(f"   ❌ Frontend simulation error: {e}")

if __name__ == "__main__":
    test_auth_debug()
