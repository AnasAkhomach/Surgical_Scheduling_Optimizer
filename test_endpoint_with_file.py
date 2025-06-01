import requests
import json

output_file = 'endpoint_test_output.txt'

with open(output_file, 'w') as f:
    try:
        f.write('Testing /api/schedules/current endpoint...\n')
        response = requests.get('http://localhost:5000/api/schedules/current')
        f.write(f'Status: {response.status_code}\n')

        if response.status_code == 200:
            data = response.json()
            f.write(f'Response: {json.dumps(data, indent=2)}\n')

            # Check if there are any surgeries
            if 'surgeries' in data:
                surgeries = data['surgeries']
                f.write(f'Number of surgeries: {len(surgeries)}\n')
                if len(surgeries) == 0:
                    f.write('No surgeries found - this explains the optimization error!\n')
                else:
                    f.write('Surgeries found - optimization should work\n')
            else:
                f.write('No surgeries field in response\n')
        else:
            f.write(f'Error response: {response.text}\n')

    except requests.exceptions.ConnectionError as e:
        f.write(f'Connection error: {e}\n')
    except Exception as e:
        f.write(f'Error: {e}\n')

print(f'Output written to {output_file}')