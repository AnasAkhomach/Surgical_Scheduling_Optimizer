import requests
import json

try:
    print('Testing /api/schedules/current endpoint...')
    response = requests.get('http://localhost:5000/api/schedules/current')
    print(f'Status: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        print(f'Response: {json.dumps(data, indent=2)}')

        # Check if there are any surgeries
        if 'surgeries' in data:
            surgeries = data['surgeries']
            print(f'Number of surgeries: {len(surgeries)}')
            if len(surgeries) == 0:
                print('No surgeries found - this explains the optimization error!')
            else:
                print('Surgeries found - optimization should work')
        else:
            print('No surgeries field in response')
    else:
        print(f'Error response: {response.text}')

except requests.exceptions.ConnectionError as e:
    print(f'Connection error: {e}')
except Exception as e:
    print(f'Error: {e}')