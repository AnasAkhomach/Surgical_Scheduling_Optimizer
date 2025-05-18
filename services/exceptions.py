"""
Custom exceptions for the surgery scheduling application.

This module defines custom exceptions that are used throughout the application
to provide more specific error information and better error handling.
"""


class SurgerySchedulerError(Exception):
    """Base exception for all surgery scheduler errors."""
    
    def __init__(self, message="An error occurred in the surgery scheduler"):
        self.message = message
        super().__init__(self.message)


class DatabaseError(SurgerySchedulerError):
    """Exception raised for database-related errors."""
    
    def __init__(self, message="A database error occurred", original_exception=None):
        self.original_exception = original_exception
        if original_exception:
            message = f"{message}: {str(original_exception)}"
        super().__init__(message)


class ValidationError(SurgerySchedulerError):
    """Exception raised for validation errors."""
    
    def __init__(self, message="Validation error", errors=None):
        self.errors = errors or {}
        if errors:
            error_details = ", ".join(f"{k}: {v}" for k, v in errors.items())
            message = f"{message}: {error_details}"
        super().__init__(message)


class ResourceNotFoundError(SurgerySchedulerError):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, resource_type, resource_id):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message)


class ResourceConflictError(SurgerySchedulerError):
    """Exception raised when there is a conflict with an existing resource."""
    
    def __init__(self, resource_type, details=None):
        self.resource_type = resource_type
        self.details = details
        message = f"Conflict with existing {resource_type}"
        if details:
            message = f"{message}: {details}"
        super().__init__(message)


class SchedulingError(SurgerySchedulerError):
    """Exception raised for scheduling-related errors."""
    
    def __init__(self, message="Error in scheduling operation", details=None):
        self.details = details
        if details:
            message = f"{message}: {details}"
        super().__init__(message)


class NotificationError(SurgerySchedulerError):
    """Exception raised for notification-related errors."""
    
    def __init__(self, message="Error sending notification", original_exception=None):
        self.original_exception = original_exception
        if original_exception:
            message = f"{message}: {str(original_exception)}"
        super().__init__(message)


class CalendarError(SurgerySchedulerError):
    """Exception raised for calendar-related errors."""
    
    def __init__(self, message="Error in calendar operation", original_exception=None):
        self.original_exception = original_exception
        if original_exception:
            message = f"{message}: {str(original_exception)}"
        super().__init__(message)


class AuthorizationError(SurgerySchedulerError):
    """Exception raised for authorization-related errors."""
    
    def __init__(self, message="Authorization error", user_id=None, resource=None):
        self.user_id = user_id
        self.resource = resource
        if user_id and resource:
            message = f"{message}: User {user_id} not authorized for {resource}"
        super().__init__(message)


class ConfigurationError(SurgerySchedulerError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message="Configuration error", setting=None):
        self.setting = setting
        if setting:
            message = f"{message}: {setting}"
        super().__init__(message)
