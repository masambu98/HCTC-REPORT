"""
Professional Logging System for HCTC-CRM
Copyright (c) 2025 - Signature: 8598

Enterprise-grade logging with structured output, file rotation,
and performance monitoring.
"""

import logging
import logging.handlers
import sys
import os
from datetime import datetime
from typing import Optional
from pathlib import Path

from ..config import config


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for console output.
    Signature: 8598
    """
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        """Format log record with colors."""
        if hasattr(record, 'levelname') and record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """
    Structured formatter for JSON output.
    Signature: 8598
    """
    
    def format(self, record):
        """Format log record as structured data."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'signature': '8598'
        }
        
        if hasattr(record, 'extra_data'):
            log_data['extra_data'] = record.extra_data
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return str(log_data)


def setup_logging() -> None:
    """
    Setup professional logging configuration.
    Signature: 8598
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get log level
    log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if config.logging.file_path:
        file_handler = logging.handlers.RotatingFileHandler(
            config.logging.file_path,
            maxBytes=config.logging.max_bytes,
            backupCount=config.logging.backup_count
        )
    else:
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "hctc_crm.log",
            maxBytes=config.logging.max_bytes,
            backupCount=config.logging.backup_count
        )
    
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - Signature: 8598'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "hctc_crm_errors.log",
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Structured log handler for production
    if config.environment.value == "production":
        structured_handler = logging.handlers.RotatingFileHandler(
            log_dir / "hctc_crm_structured.log",
            maxBytes=config.logging.max_bytes,
            backupCount=config.logging.backup_count
        )
        structured_handler.setLevel(log_level)
        structured_formatter = StructuredFormatter()
        structured_handler.setFormatter(structured_formatter)
        root_logger.addHandler(structured_handler)
    
    # Suppress noisy loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"HCTC-CRM Logging System Initialized - Signature: 8598")
    logger.info(f"Log Level: {config.logging.level}")
    logger.info(f"Environment: {config.environment.value}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with proper configuration.
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    return logger


class PerformanceLogger:
    """
    Performance logging utility.
    Signature: 8598
    """
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        self.start_time = None
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self.start_time = datetime.utcnow()
        self.operation = operation
        self.logger.debug(f"Starting operation: {operation}")
    
    def end_timer(self, success: bool = True) -> None:
        """End timing an operation."""
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            status = "SUCCESS" if success else "FAILED"
            self.logger.info(f"Operation {self.operation} {status} in {duration:.3f}s - Signature: 8598")
            self.start_time = None


def log_function_call(func):
    """
    Decorator to log function calls with performance metrics.
    Signature: 8598
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        perf_logger = PerformanceLogger(func.__module__)
        
        perf_logger.start_timer(f"{func.__name__}")
        try:
            result = func(*args, **kwargs)
            perf_logger.end_timer(success=True)
            return result
        except Exception as e:
            perf_logger.end_timer(success=False)
            logger.error(f"Function {func.__name__} failed: {e}")
            raise
    
    return wrapper


def log_api_call(endpoint: str, method: str, status_code: int, duration: float) -> None:
    """
    Log API call with performance metrics.
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        status_code: Response status code
        duration: Request duration in seconds
    """
    logger = logging.getLogger("api")
    logger.info(f"API {method} {endpoint} - Status: {status_code} - Duration: {duration:.3f}s - Signature: 8598")


def log_database_operation(operation: str, table: str, duration: float, success: bool = True) -> None:
    """
    Log database operation with performance metrics.
    
    Args:
        operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
        duration: Operation duration in seconds
        success: Whether operation was successful
    """
    logger = logging.getLogger("database")
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"DB {operation} {table} - {status} - Duration: {duration:.3f}s - Signature: 8598")


def log_message_processing(platform: str, message_type: str, success: bool = True) -> None:
    """
    Log message processing with platform and type information.
    
    Args:
        platform: Message platform (WhatsApp, Facebook)
        message_type: Message type (text, image, etc.)
        success: Whether processing was successful
    """
    logger = logging.getLogger("message_processing")
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Message processing {platform} {message_type} - {status} - Signature: 8598")
