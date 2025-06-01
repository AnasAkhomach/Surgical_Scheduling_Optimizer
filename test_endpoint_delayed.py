import requests
import time
import json

# Wait a bit to ensure server is ready
time.sleep(2)

try:
    response = requests.get('http://localhost:5000/api/schedules/current')
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
except Exception as e:
    print(f"Unexpected error: {e}")