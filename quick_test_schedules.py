import requests
import json
import time

def quick_test():
    try:
        print("Making quick request to schedules endpoint...")
        response = requests.get('http://127.0.0.1:5000/api/schedules/current', timeout=5)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            # Save response to file immediately
            with open('schedules_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Response saved to schedules_response.json")
            print(f"Response preview: {json.dumps(data, indent=2)[:500]}...")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_test()