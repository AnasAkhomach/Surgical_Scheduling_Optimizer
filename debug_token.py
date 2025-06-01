#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '.')

from db_config import get_db
from models import User
from api.auth import create_access_token
from datetime import timedelta

def main():
    # Check if user exists
    db = next(get_db())
    user = db.query(User).filter(User.username == 'user123').first()

    print(f"User 'user123' exists: {user is not None}")

    if user:
        print(f"User details: {user.username}, {user.email}, Active: {user.is_active}")

        # Generate a fresh token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username, "role": "user"},
            expires_delta=access_token_expires
        )
        print(f"\nFresh token: {access_token}")
    else:
        print("User does not exist. Available users:")
        users = db.query(User).all()
        for u in users:
            print(f"  - {u.username} ({u.email})")

    db.close()

if __name__ == "__main__":
    main()