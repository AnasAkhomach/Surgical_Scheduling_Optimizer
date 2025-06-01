#!/usr/bin/env python3
import jwt
from datetime import datetime, timedelta

def test_secret_key_mismatch():
    """Test if there's a SECRET_KEY mismatch causing 401 errors"""
    print("SECRET_KEY Mismatch Test")
    print("=" * 30)

    # Keys from different sources
    env_key = "dev_secret_key_change_in_production"  # From .env file
    default_key = "your-secret-key-for-development-only"  # From auth.py default

    print(f"ENV file key: {env_key}")
    print(f"Default key: {default_key}")
    print(f"Keys match: {env_key == default_key}")

    # Test token from user's error message
    user_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwicm9sZSI6InVzZXIiLCJleHAiOjE3NDg3NzgyMTF9.ZyBkJYDUtf-N5KEOPbjs9s4U4ed_3rVEsuneYUWndIg"

    print(f"\nTesting user's token: {user_token[:50]}...")

    # Try to decode with both keys
    algorithm = "HS256"

    print("\n1. Trying to decode with ENV key...")
    try:
        decoded_env = jwt.decode(user_token, env_key, algorithms=[algorithm])
        print(f"✅ SUCCESS with ENV key: {decoded_env}")
    except jwt.ExpiredSignatureError:
        print("❌ Token expired (but key worked)")
    except jwt.InvalidTokenError as e:
        print(f"❌ FAILED with ENV key: {e}")

    print("\n2. Trying to decode with DEFAULT key...")
    try:
        decoded_default = jwt.decode(user_token, default_key, algorithms=[algorithm])
        print(f"✅ SUCCESS with DEFAULT key: {decoded_default}")
    except jwt.ExpiredSignatureError:
        print("❌ Token expired (but key worked)")
    except jwt.InvalidTokenError as e:
        print(f"❌ FAILED with DEFAULT key: {e}")

    # Create test tokens with both keys
    print("\n3. Creating test tokens...")
    test_data = {"sub": "testuser", "role": "user", "exp": datetime.utcnow() + timedelta(hours=1)}

    token_env = jwt.encode(test_data, env_key, algorithm=algorithm)
    token_default = jwt.encode(test_data, default_key, algorithm=algorithm)

    print(f"Token with ENV key: {token_env[:50]}...")
    print(f"Token with DEFAULT key: {token_default[:50]}...")
    print(f"Tokens are same: {token_env == token_default}")

    # Cross-validation test
    print("\n4. Cross-validation test...")
    try:
        # Try to decode ENV token with DEFAULT key
        jwt.decode(token_env, default_key, algorithms=[algorithm])
        print("❌ ENV token validated with DEFAULT key (shouldn't work)")
    except jwt.InvalidTokenError:
        print("✅ ENV token correctly rejected by DEFAULT key")

    try:
        # Try to decode DEFAULT token with ENV key
        jwt.decode(token_default, env_key, algorithms=[algorithm])
        print("❌ DEFAULT token validated with ENV key (shouldn't work)")
    except jwt.InvalidTokenError:
        print("✅ DEFAULT token correctly rejected by ENV key")

if __name__ == "__main__":
    test_secret_key_mismatch()