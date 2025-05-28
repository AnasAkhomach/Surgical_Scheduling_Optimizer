import requests
import json

def test_auth_debug_final():
    """Final debug test to isolate the authentication issue"""
    print("=== FINAL AUTHENTICATION DEBUG TEST ===\n")
    
    base_url = "http://localhost:8000/api"
    
    # Test 1: Login and immediately test /auth/me
    print("1. Testing login -> immediate /auth/me sequence...")
    try:
        # Login
        login_data = {
            'username': 'admin2',
            'password': 'admin2admin2',
            'grant_type': 'password'
        }
        
        print("   Sending login request...")
        response = requests.post(f"{base_url}/auth/token", data=login_data)
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            print(f"   ✅ Login successful! Token: {access_token[:30]}...")
            
            # Immediately test /auth/me with the token
            print("   Testing /auth/me immediately...")
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            print(f"   Authorization header: Bearer {access_token[:30]}...")
            
            me_response = requests.get(f"{base_url}/auth/me", headers=headers)
            print(f"   /auth/me status: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"   ✅ /auth/me successful! User: {user_data['username']} (ID: {user_data['user_id']})")
                return True
            else:
                print(f"   ❌ /auth/me failed")
                try:
                    error_data = me_response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Raw response: {me_response.text}")
                return False
                
        else:
            print(f"   ❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        return False

def test_token_validation():
    """Test if the token itself is valid"""
    print("\n2. Testing token validation...")
    
    # First, let's decode the JWT token to see what's inside
    try:
        # Login to get a fresh token
        login_data = {
            'username': 'admin2',
            'password': 'admin2admin2',
            'grant_type': 'password'
        }
        
        response = requests.post("http://localhost:8000/api/auth/token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            
            # Try to decode the JWT (just the payload, not verifying signature)
            import base64
            import json
            
            # Split the JWT
            parts = access_token.split('.')
            if len(parts) == 3:
                # Decode the payload (second part)
                payload = parts[1]
                # Add padding if needed
                payload += '=' * (4 - len(payload) % 4)
                
                try:
                    decoded_payload = base64.b64decode(payload)
                    payload_data = json.loads(decoded_payload)
                    print(f"   Token payload: {json.dumps(payload_data, indent=2)}")
                    
                    # Check if token has expired
                    import time
                    current_time = time.time()
                    exp_time = payload_data.get('exp', 0)
                    
                    if exp_time > current_time:
                        print(f"   ✅ Token is valid (expires in {int(exp_time - current_time)} seconds)")
                    else:
                        print(f"   ❌ Token has expired!")
                        
                except Exception as e:
                    print(f"   ❌ Could not decode token payload: {e}")
            else:
                print(f"   ❌ Invalid JWT format")
                
        else:
            print(f"   ❌ Could not get token for validation")
            
    except Exception as e:
        print(f"   ❌ Token validation error: {e}")

def test_backend_auth_endpoint():
    """Test the backend auth endpoint directly"""
    print("\n3. Testing backend auth endpoint behavior...")
    
    try:
        # Test with no Authorization header
        print("   Testing /auth/me with no Authorization header...")
        response = requests.get("http://localhost:8000/api/auth/me")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejects request without Authorization header")
        
        # Test with invalid token
        print("   Testing /auth/me with invalid token...")
        headers = {'Authorization': 'Bearer invalid-token'}
        response = requests.get("http://localhost:8000/api/auth/me", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejects invalid token")
            
        # Test with malformed Authorization header
        print("   Testing /auth/me with malformed Authorization header...")
        headers = {'Authorization': 'InvalidFormat token'}
        response = requests.get("http://localhost:8000/api/auth/me", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejects malformed Authorization header")
            
    except Exception as e:
        print(f"   ❌ Backend test error: {e}")

if __name__ == "__main__":
    success = test_auth_debug_final()
    test_token_validation()
    test_backend_auth_endpoint()
    
    if success:
        print("\n=== AUTHENTICATION IS WORKING CORRECTLY ===")
        print("✅ The issue is likely in the frontend token storage/retrieval")
    else:
        print("\n=== AUTHENTICATION ISSUE CONFIRMED ===")
        print("❌ There is a problem with the backend authentication")
