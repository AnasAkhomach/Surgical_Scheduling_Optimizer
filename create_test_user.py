import os
import sys
import logging
import traceback
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db_config import get_db, init_db

# Import models directly
try:
    import models
    print("Successfully imported models")
except ImportError as e:
    print(f"Error importing models: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, username: str, password: str, email: str, full_name: str = None, role: str = "user"):
    """Create a new user in the database."""
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        logger.info(f"User {username} already exists")
        return existing_user

    # Hash the password
    hashed_password = pwd_context.hash(password)

    # Create new user
    new_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role,
        is_active=True
    )

    # Add to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Created new user: {username}")
    return new_user

def main():
    """Create test users."""
    try:
        # Initialize the database
        print("Initializing database...")
        init_db()
        print("Database initialized")

        # Get database session
        print("Getting database session...")
        db = next(get_db())
        print("Database session obtained")

        # Create admin user
        print("Creating admin user...")
        admin = create_user(
            db=db,
            username="admin",
            password="admin123",
            email="admin@example.com",
            full_name="Admin User",
            role="admin"
        )
        print(f"Admin user created: {admin.username}")

        # Create regular user
        print("Creating regular user...")
        user = create_user(
            db=db,
            username="user",
            password="user123",
            email="user@example.com",
            full_name="Regular User",
            role="user"
        )
        print(f"Regular user created: {user.username}")

        # Create surgeon user
        print("Creating surgeon user...")
        surgeon = create_user(
            db=db,
            username="surgeon",
            password="surgeon123",
            email="surgeon@example.com",
            full_name="Dr. Smith",
            role="surgeon"
        )
        print(f"Surgeon user created: {surgeon.username}")

        logger.info("Test users created successfully")
        print("\nTest users created successfully!")
        print("\nLogin credentials:")
        print("------------------")
        print("Admin:    username=admin, password=admin123")
        print("User:     username=user, password=user123")
        print("Surgeon:  username=surgeon, password=surgeon123")

    except Exception as e:
        logger.error(f"Error creating test users: {e}")
        print(f"Error creating test users: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
