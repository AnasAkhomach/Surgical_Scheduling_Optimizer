#!/usr/bin/env python3
import os
from dotenv import load_dotenv

def debug_secret_key():
    """Debug SECRET_KEY configuration"""
    print("SECRET_KEY Debug")
    print("=" * 30)

    # Check if .env file exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env file exists: {env_file}")
        load_dotenv()
    else:
        print(f"❌ .env file not found: {env_file}")
        print("Using default values from environment or hardcoded defaults")

    # Get SECRET_KEY from environment
    secret_key = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
    print(f"SECRET_KEY: {secret_key}")

    # Get other auth settings
    algorithm = os.getenv("ALGORITHM", "HS256")
    expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    print(f"ALGORITHM: {algorithm}")
    print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {expire_minutes}")

    # Test token creation and verification
    print("\nTesting token creation and verification...")

    try:
        from jose import jwt
        from datetime import datetime, timedelta

        # Create a test token
        test_data = {"sub": "testuser", "role": "user"}
        expire = datetime.utcnow() + timedelta(minutes=30)
        test_data.update({"exp": expire})

        token = jwt.encode(test_data, secret_key, algorithm=algorithm)
        print(f"✅ Token created: {token[:50]}...")

        # Verify the token
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        print(f"✅ Token verified: {payload}")

        return True

    except Exception as e:
        print(f"❌ Token test failed: {e}")
        return False

if __name__ == "__main__":
    debug_secret_key()