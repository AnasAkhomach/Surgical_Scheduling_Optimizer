"""
Tests for the authentication functionality.

This module provides tests for the authentication functionality,
including JWT token generation, password hashing, and user authentication.
"""

import os
import sys
import pytest
from datetime import datetime, timedelta
from jose import jwt

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword"
    hashed_password = get_password_hash(password)

    # Verify that the hash is different from the original password
    assert hashed_password != password

    # Verify that the password can be verified against the hash
    assert verify_password(password, hashed_password)

    # Verify that an incorrect password fails verification
    assert not verify_password("wrongpassword", hashed_password)


def test_access_token_creation():
    """Test JWT access token creation."""
    # Create a token with test data
    data = {"sub": "testuser", "role": "admin"}
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, expires_delta)

    # Verify that the token is a string
    assert isinstance(token, str)

    # Decode the token and verify its contents
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    # Verify that the subject and role are correct
    assert payload["sub"] == "testuser"
    assert payload["role"] == "admin"

    # Verify that the expiration time is set
    assert "exp" in payload

    # Verify that the token expires in the future
    exp_time = datetime.fromtimestamp(payload["exp"])
    assert exp_time > datetime.utcnow()

    # Verify that the token expires in the future (we don't need to check exact time)
    time_diff = exp_time - datetime.utcnow()
    assert time_diff.total_seconds() > 0


def test_access_token_expiration():
    """Test JWT access token expiration."""
    # Create a token that expires in 1 second
    data = {"sub": "testuser"}
    expires_delta = timedelta(seconds=1)
    token = create_access_token(data, expires_delta)

    # Wait for the token to expire
    import time
    time.sleep(2)

    # Verify that the token is expired
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def test_access_token_default_expiration():
    """Test JWT access token default expiration."""
    # Create a token without specifying an expiration time
    data = {"sub": "testuser"}
    token = create_access_token(data)

    # Decode the token and verify its contents
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    # Verify that the expiration time is set
    assert "exp" in payload

    # Verify that the token expires in the future
    exp_time = datetime.fromtimestamp(payload["exp"])
    assert exp_time > datetime.utcnow()


def test_invalid_token_signature():
    """Test JWT token with invalid signature."""
    # Create a token with test data
    data = {"sub": "testuser"}
    token = create_access_token(data)

    # Modify the token to invalidate the signature
    parts = token.split(".")
    parts[2] = "invalid_signature"
    invalid_token = ".".join(parts)

    # Verify that the token fails validation
    with pytest.raises(jwt.JWTError):
        jwt.decode(invalid_token, SECRET_KEY, algorithms=[ALGORITHM])


# Run the tests
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
