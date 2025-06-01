import requests
import time
import json
import sys

def test_server_health():
    """Test if the server is responding"""
    try:
        response = requests.get('http://localhost:5000/docs', timeout=5)
        return response.status_code == 200
    except:
        return False

def test_schedules_endpoint():
    """Test the schedules endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/schedules/current', timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")

            if 'surgeries' in data:
                print(f"Found {len(data['surgeries'])} surgeries in the response")
                for i, surgery in enumerate(data['surgeries']):
                    print(f"  Surgery {i+1}: {surgery.get('surgery_type', 'Unknown')} - {surgery.get('start_time', 'No time')}")
            else:
                print("No 'surgeries' field found in response")
                print(f"Available fields: {list(data.keys())}")
        else:
            print(f"Error response: {response.text}")

    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    return True

if __name__ == "__main__":
    print("Testing server health...")

    # Wait for server to be ready
    max_retries = 10
    for i in range(max_retries):
        if test_server_health():
            print(f"Server is responding after {i+1} attempts")
            break
        print(f"Attempt {i+1}: Server not ready, waiting...")
        time.sleep(2)
    else:
        print("Server is not responding after maximum retries")
        sys.exit(1)

    print("\nTesting schedules endpoint...")
    success = test_schedules_endpoint()

    if success:
        print("\nEndpoint test completed successfully")
    else:
        print("\nEndpoint test failed")
        sys.exit(1)