import requests
import time
import json

def test_schedules_endpoint():
    try:
        # Wait for server to be ready
        time.sleep(2)

        print("Testing schedules endpoint...")

        # Test the schedules endpoint
        response = requests.get('http://127.0.0.1:5000/api/schedules/current', timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response JSON: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response Text: {response.text}")
        else:
            print(f"Error Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_schedules_endpoint()