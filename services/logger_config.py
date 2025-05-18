"""
Logger configuration for the surgery scheduling application.

This module provides a consistent logging configuration for the entire application.
It sets up loggers with appropriate handlers and formatters.
"""

import os
import logging
import logging.handlers
import json
from datetime import datetime


class StructuredLogFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in a structured JSON format.
    
    This formatter is useful for log aggregation and analysis tools.
    """
    
    def format(self, record):
        """
        Format the log record as a JSON string.
        
        Args:
            record: The log record to format.
            
        Returns:
            A JSON string representation of the log record.
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info),
            }
        
        # Add extra fields if available
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


def setup_logging(log_level=None, log_file=None, structured=False):
    """
    Set up logging for the application.
    
    Args:
        log_level: The logging level (default: INFO).
        log_file: Path to the log file (default: logs/surgery_scheduler.log).
        structured: Whether to use structured JSON logging (default: False).
    """
    # Determine log level
    log_level = log_level or os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Determine log file
    log_file = log_file or os.getenv('LOG_FILE', 'logs/surgery_scheduler.log')
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    
    # Create file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=5
    )
    file_handler.setLevel(numeric_level)
    
    # Create formatter
    if structured:
        formatter = StructuredLogFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Set formatter for handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Create application logger
    logger = logging.getLogger('surgery_scheduler')
    logger.setLevel(numeric_level)
    
    return logger


# Create default logger
logger = setup_logging()
