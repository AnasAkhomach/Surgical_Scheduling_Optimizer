from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(1, 5)  # Wait time between tasks
    host = "http://127.0.0.1:8000"  # Replace with your API host

    def on_start(self):
        """ On start, log in a user or prepare test data """
        # Example: self.client.post("/login", {"username":"test_user", "password":"password"})
        # For /auth/token, we might need to get a token first if other endpoints require auth
        # For now, we'll assume endpoints can be hit directly or auth is handled per task
        pass

    @task(1)
    def get_auth_token(self):
        """ Test the /auth/token endpoint. """
        # This endpoint is typically a POST request with username and password
        # Adjust the payload as per your application's requirements
        # For a GET request or a different type, modify self.client.post accordingly
        # Example for a POST request:
        # response = self.client.post("/api/v1/auth/token", data={"username": "testuser", "password": "testpassword"})
        # print(f"Token response: {response.status_code}")
        # For now, let's simulate a GET to a placeholder if the actual call is complex
        # or requires specific credentials not set up here.
        # Replace with actual POST request to /auth/token
        self.client.post("/api/v1/auth/token", data={"username": "testuser", "password": "testpassword"})

    @task(2)
    def get_surgery_types(self):
        """ Test the /surgery-types endpoint. """
        self.client.get("/api/v1/surgery-types")

    @task(2)
    def get_operating_rooms(self):
        """ Test the /operating-rooms endpoint. """
        # Test with default pagination
        self.client.get("/api/v1/operating-rooms")
        # Test with specific pagination
        self.client.get("/api/v1/operating-rooms?skip=0&limit=5")

    # Add more tasks for other endpoints or scenarios