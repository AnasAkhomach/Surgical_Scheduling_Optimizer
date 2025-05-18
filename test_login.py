import requests
import json

def test_login(username, password):
    """Test login functionality."""
    url = "http://127.0.0.1:8000/api/auth/token"
    
    # Prepare the form data
    data = {
        "username": username,
        "password": password
    }
    
    # Make the request
    print(f"Attempting to login with username: {username}")
    response = requests.post(url, data=data)
    
    # Check the response
    if response.status_code == 200:
        print("Login successful!")
        token_data = response.json()
        print(f"Access token: {token_data['access_token'][:20]}...")
        print(f"Token type: {token_data['token_type']}")
        return token_data
    else:
        print(f"Login failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint."""
    url = "http://127.0.0.1:8000/api/users/me"
    
    # Prepare the headers with the token
    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }
    
    # Make the request
    print("\nAttempting to access protected endpoint...")
    response = requests.get(url, headers=headers)
    
    # Check the response
    if response.status_code == 200:
        print("Access to protected endpoint successful!")
        user_data = response.json()
        print(f"User data: {json.dumps(user_data, indent=2)}")
        return user_data
    else:
        print(f"Access failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def main():
    """Main function to test login and protected endpoints."""
    print("=== Testing Admin Login ===")
    admin_token = test_login("admin", "admin123")
    if admin_token:
        test_protected_endpoint(admin_token)
    
    print("\n=== Testing User Login ===")
    user_token = test_login("user", "user123")
    if user_token:
        test_protected_endpoint(user_token)
    
    print("\n=== Testing Surgeon Login ===")
    surgeon_token = test_login("surgeon", "surgeon123")
    if surgeon_token:
        test_protected_endpoint(surgeon_token)
    
    print("\n=== Testing Invalid Login ===")
    test_login("invalid", "invalid123")

if __name__ == "__main__":
    main()
