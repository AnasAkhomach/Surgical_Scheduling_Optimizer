import requests
import time

def test_server_health():
    try:
        # Wait a moment for server to be ready
        time.sleep(2)

        # Test basic server response
        response = requests.get('http://localhost:5000/', timeout=5)
        print(f"Root endpoint status: {response.status_code}")
        print(f"Root response: {response.text[:200]}")

        # Test docs endpoint
        response = requests.get('http://localhost:5000/docs', timeout=5)
        print(f"Docs endpoint status: {response.status_code}")

        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    test_server_health()