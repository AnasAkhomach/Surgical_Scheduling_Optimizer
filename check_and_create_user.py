#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from sqlalchemy.orm import Session
from db_config import get_db
from models import User
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def main():
    # Get database session
    db = next(get_db())

    try:
        # Check existing users
        users = db.query(User).all()
        print(f"Found {len(users)} users in database:")
        for user in users:
            print(f"  - Username: {user.username}, Email: {user.email}, Role: {user.role}")

        # Check if user123 exists
        existing_user = db.query(User).filter(User.username == "user123").first()

        if not existing_user:
            print("\nCreating test user 'user123'...")
            # Create test user
            test_user = User(
                username="user123",
                email="user123@example.com",
                hashed_password=hash_password("password123"),
                role="user",
                is_active=True
            )
            db.add(test_user)
            db.commit()
            print("Test user created successfully!")
        else:
            print(f"\nUser 'user123' already exists with email: {existing_user.email}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()