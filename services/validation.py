"""
Validation module for the surgery scheduling application.

This module provides validators for input data and business rules.
"""

import re
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Union, Callable, Type

from sqlalchemy.orm import Session

from models import (
    Surgery,
    OperatingRoom,
    Surgeon,
    Staff,
    Patient,
    SurgeryEquipment,
    SurgeryType,
    SurgeonPreference
)
from services.exceptions import ValidationError

logger = logging.getLogger(__name__)


class Validator:
    """Base class for validators."""
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize the validator.
        
        Args:
            db: SQLAlchemy database session.
        """
        self.db = db
        self.errors = {}
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate the data.
        
        Args:
            data: The data to validate.
            
        Returns:
            True if the data is valid, False otherwise.
            
        Raises:
            ValidationError: If validation fails.
        """
        self.errors = {}
        self._validate(data)
        
        if self.errors:
            logger.warning(f"Validation failed: {self.errors}")
            return False
        
        return True
    
    def validate_and_raise(self, data: Dict[str, Any]) -> None:
        """
        Validate the data and raise an exception if validation fails.
        
        Args:
            data: The data to validate.
            
        Raises:
            ValidationError: If validation fails.
        """
        if not self.validate(data):
            raise ValidationError("Validation failed", errors=self.errors)
    
    def _validate(self, data: Dict[str, Any]) -> None:
        """
        Validate the data.
        
        This method should be overridden by subclasses.
        
        Args:
            data: The data to validate.
        """
        raise NotImplementedError("Subclasses must implement _validate")
    
    def add_error(self, field: str, message: str) -> None:
        """
        Add an error for a field.
        
        Args:
            field: The field name.
            message: The error message.
        """
        if field not in self.errors:
            self.errors[field] = []
        
        self.errors[field].append(message)
    
    def validate_required(self, data: Dict[str, Any], fields: List[str]) -> bool:
        """
        Validate that required fields are present and not None.
        
        Args:
            data: The data to validate.
            fields: The required fields.
            
        Returns:
            True if all required fields are present, False otherwise.
        """
        valid = True
        
        for field in fields:
            if field not in data or data[field] is None:
                self.add_error(field, f"{field} is required")
                valid = False
        
        return valid
    
    def validate_string(
        self,
        data: Dict[str, Any],
        field: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        required: bool = True
    ) -> bool:
        """
        Validate a string field.
        
        Args:
            data: The data to validate.
            field: The field name.
            min_length: The minimum length of the string.
            max_length: The maximum length of the string.
            pattern: A regular expression pattern to match.
            required: Whether the field is required.
            
        Returns:
            True if the field is valid, False otherwise.
        """
        if field not in data or data[field] is None:
            if required:
                self.add_error(field, f"{field} is required")
                return False
            return True
        
        value = data[field]
        
        if not isinstance(value, str):
            self.add_error(field, f"{field} must be a string")
            return False
        
        if min_length is not None and len(value) < min_length:
            self.add_error(field, f"{field} must be at least {min_length} characters")
            return False
        
        if max_length is not None and len(value) > max_length:
            self.add_error(field, f"{field} must be at most {max_length} characters")
            return False
        
        if pattern is not None and not re.match(pattern, value):
            self.add_error(field, f"{field} must match pattern {pattern}")
            return False
        
        return True
    
    def validate_integer(
        self,
        data: Dict[str, Any],
        field: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        required: bool = True
    ) -> bool:
        """
        Validate an integer field.
        
        Args:
            data: The data to validate.
            field: The field name.
            min_value: The minimum value.
            max_value: The maximum value.
            required: Whether the field is required.
            
        Returns:
            True if the field is valid, False otherwise.
        """
        if field not in data or data[field] is None:
            if required:
                self.add_error(field, f"{field} is required")
                return False
            return True
        
        value = data[field]
        
        if not isinstance(value, int):
            try:
                value = int(value)
                data[field] = value  # Convert to int if possible
            except (ValueError, TypeError):
                self.add_error(field, f"{field} must be an integer")
                return False
        
        if min_value is not None and value < min_value:
            self.add_error(field, f"{field} must be at least {min_value}")
            return False
        
        if max_value is not None and value > max_value:
            self.add_error(field, f"{field} must be at most {max_value}")
            return False
        
        return True
    
    def validate_date(
        self,
        data: Dict[str, Any],
        field: str,
        min_date: Optional[Union[date, datetime]] = None,
        max_date: Optional[Union[date, datetime]] = None,
        required: bool = True
    ) -> bool:
        """
        Validate a date field.
        
        Args:
            data: The data to validate.
            field: The field name.
            min_date: The minimum date.
            max_date: The maximum date.
            required: Whether the field is required.
            
        Returns:
            True if the field is valid, False otherwise.
        """
        if field not in data or data[field] is None:
            if required:
                self.add_error(field, f"{field} is required")
                return False
            return True
        
        value = data[field]
        
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
                data[field] = value  # Convert to datetime if possible
            except ValueError:
                self.add_error(field, f"{field} must be a valid date")
                return False
        
        if not isinstance(value, (date, datetime)):
            self.add_error(field, f"{field} must be a date")
            return False
        
        if min_date is not None and value < min_date:
            self.add_error(field, f"{field} must be on or after {min_date}")
            return False
        
        if max_date is not None and value > max_date:
            self.add_error(field, f"{field} must be on or before {max_date}")
            return False
        
        return True
    
    def validate_boolean(
        self,
        data: Dict[str, Any],
        field: str,
        required: bool = True
    ) -> bool:
        """
        Validate a boolean field.
        
        Args:
            data: The data to validate.
            field: The field name.
            required: Whether the field is required.
            
        Returns:
            True if the field is valid, False otherwise.
        """
        if field not in data or data[field] is None:
            if required:
                self.add_error(field, f"{field} is required")
                return False
            return True
        
        value = data[field]
        
        if not isinstance(value, bool):
            if isinstance(value, str):
                if value.lower() in ('true', 'yes', '1', 'y'):
                    data[field] = True
                    return True
                elif value.lower() in ('false', 'no', '0', 'n'):
                    data[field] = False
                    return True
            
            self.add_error(field, f"{field} must be a boolean")
            return False
        
        return True
    
    def validate_enum(
        self,
        data: Dict[str, Any],
        field: str,
        allowed_values: List[Any],
        required: bool = True
    ) -> bool:
        """
        Validate an enum field.
        
        Args:
            data: The data to validate.
            field: The field name.
            allowed_values: The allowed values.
            required: Whether the field is required.
            
        Returns:
            True if the field is valid, False otherwise.
        """
        if field not in data or data[field] is None:
            if required:
                self.add_error(field, f"{field} is required")
                return False
            return True
        
        value = data[field]
        
        if value not in allowed_values:
            self.add_error(
                field,
                f"{field} must be one of {', '.join(str(v) for v in allowed_values)}"
            )
            return False
        
        return True
    
    def validate_foreign_key(
        self,
        data: Dict[str, Any],
        field: str,
        model: Type,
        id_field: str = None,
        required: bool = True
    ) -> bool:
        """
        Validate a foreign key field.
        
        Args:
            data: The data to validate.
            field: The field name.
            model: The model class.
            id_field: The ID field name in the model.
            required: Whether the field is required.
            
        Returns:
            True if the field is valid, False otherwise.
        """
        if field not in data or data[field] is None:
            if required:
                self.add_error(field, f"{field} is required")
                return False
            return True
        
        if self.db is None:
            logger.warning(f"Cannot validate foreign key {field} without database session")
            return True
        
        value = data[field]
        
        if not isinstance(value, int):
            try:
                value = int(value)
                data[field] = value  # Convert to int if possible
            except (ValueError, TypeError):
                self.add_error(field, f"{field} must be an integer")
                return False
        
        id_field = id_field or f"{model.__tablename__}_id"
        
        # Check if the foreign key exists
        exists = self.db.query(model).filter(getattr(model, id_field) == value).first() is not None
        
        if not exists:
            self.add_error(field, f"{model.__name__} with ID {value} does not exist")
            return False
        
        return True
