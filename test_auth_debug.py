import requests
import json

def test_auth_debug():
    """Test authentication endpoints to debug frontend issues"""
    print("=== AUTHENTICATION DEBUG TEST ===\n")
    
    # Test 1: Check if backend is running
    print("1. Testing backend connectivity...")
    try:
        response = requests.get('http://localhost:8000/docs')
        print(f"   Backend status: {response.status_code} ✅")
    except Exception as e:
        print(f"   ❌ Backend not accessible: {e}")
        return
    
    # Test 2: Test user creation (to ensure we have a test user)
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
                
        elif response.status_code == 400:
            print("   ℹ️ User already exists, proceeding with login tests...")
        else:
            print(f"   ❌ Registration failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Registration error: {e}")

    # Test 3: Test login with form data (correct format)
    print("\n3. Testing login with form data (correct format)...")
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'grant_type': 'password'
        }
        
        response = requests.post('http://localhost:8000/api/auth/token',
                               data=login_data)
        print(f"   Form data login status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Form data login works!")
            token_data = response.json()
            print(f"   Token type: {token_data.get('token_type')}")
        else:
            print(f"   ❌ Form data login failed: {response.text}")
            if response.status_code == 422:
                error_data = response.json()
                print(f"   Validation details: {json.dumps(error_data, indent=2)}")
    except Exception as e:
        print(f"   ❌ Form data login error: {e}")

    # Test 4: Simulate exact frontend FormData request
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

    # Test 5: Test with JSON (what frontend might be incorrectly sending)
    print("\n5. Testing login with JSON (incorrect format)...")
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'grant_type': 'password'
        }
        
        response = requests.post('http://localhost:8000/api/auth/token',
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        print(f"   JSON login status: {response.status_code}")
        if response.status_code == 422:
            print("   ✅ Correctly rejects JSON format")
            error_data = response.json()
            print(f"   Validation error details: {json.dumps(error_data, indent=2)}")
        else:
            print(f"   ❌ Unexpected JSON response: {response.text}")
    except Exception as e:
        print(f"   ❌ JSON login error: {e}")

    # Test 6: Test registration with existing user
    print("\n6. Testing registration with existing user...")
    try:
        user_data = {
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@example.com',
            'full_name': 'Admin User'
        }
        
        response = requests.post('http://localhost:8000/api/auth/register',
                               json=user_data)
        print(f"   Duplicate registration status: {response.status_code}")
        if response.status_code == 400:
            print("   ✅ Correctly rejects duplicate user")
            error_data = response.json()
            print(f"   Error message: {error_data.get('detail')}")
        else:
            print(f"   ❌ Unexpected registration response: {response.text}")
    except Exception as e:
        print(f"   ❌ Duplicate registration error: {e}")

if __name__ == "__main__":
    test_auth_debug()
