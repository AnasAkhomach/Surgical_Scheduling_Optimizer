"""
Tests for the database configuration module.
"""

import os
import pytest
from unittest.mock import patch
import tempfile
import sqlite3

# Set environment variables for testing
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SQL_ECHO"] = "False"

from db_config import engine, Base, get_db, init_db, close_db_connection


def test_engine_creation():
    """Test that the engine is created correctly."""
    assert engine is not None
    assert str(engine.url) == "sqlite:///:memory:"


def test_get_db():
    """Test the get_db function."""
    db_generator = get_db()
    db = next(db_generator)
    
    # Check that we can execute a query
    result = db.execute("SELECT 1").scalar()
    assert result == 1
    
    # Clean up
    try:
        next(db_generator)
    except StopIteration:
        pass


def test_init_db():
    """Test the init_db function."""
    # Create a simple model for testing
    class TestModel(Base):
        __tablename__ = "test_model"
        from sqlalchemy import Column, Integer, String
        id = Column(Integer, primary_key=True)
        name = Column(String(50))
    
    # Initialize the database
    init_db()
    
    # Check that the table was created
    inspector = engine.dialect.inspector
    tables = inspector.get_table_names()
    assert "test_model" in tables


def test_close_db_connection():
    """Test the close_db_connection function."""
    # This is mostly a smoke test
    close_db_connection()


@patch("db_config.create_engine")
def test_sqlite_fallback(mock_create_engine):
    """Test that SQLite is used as a fallback if MySQL parameters are not set."""
    # Clear environment variables
    with patch.dict(os.environ, {
        "DATABASE_URL": "",
        "DB_USER": "",
        "DB_PASSWORD": "",
        "DB_HOST": "",
        "DB_PORT": "",
        "DB_NAME": "",
        "SQLITE_URL": "sqlite:///test.db"
    }):
        # Reload the module
        import importlib
        import db_config
        importlib.reload(db_config)
        
        # Check that create_engine was called with the SQLite URL
        mock_create_engine.assert_called_once()
        args, kwargs = mock_create_engine.call_args
        assert "sqlite:///test.db" in args[0]


if __name__ == "__main__":
    pytest.main(["-v", __file__])
