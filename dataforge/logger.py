"""
Logger Setup Module
Configures and manages logging for the application.

This module provides logging functionality with different levels (INFO, WARNING, ERROR)
for tracking all operations in the DataForge utility.
"""

import logging
import sys


def setup_logger(name='dataforge', level=logging.INFO, log_file=None):
    """
    Configure and return a logger instance.
    
    Args:
        name (str): Logger name (default: 'dataforge')
        level (int): Logging level (default: logging.INFO)
        log_file (str, optional): Path to log file for file output
    
    Returns:
        logging.Logger: Configured logger instance
    
    Example:
        >>> logger = setup_logger()
        >>> logger.info("Application started")
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (always added)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (IOError, OSError) as e:
            logger.warning(f"Could not create log file '{log_file}': {e}")
    
    return logger


def log_start(logger, message="DataForge utility started"):
    """
    Log the start of an operation.
    
    Args:
        logger (logging.Logger): Logger instance
        message (str): Message to log
    """
    logger.info("=" * 60)
    logger.info(message)
    logger.info("=" * 60)


def log_completion(logger, message="Operation completed successfully", details=None):
    """
    Log the completion of an operation.
    
    Args:
        logger (logging.Logger): Logger instance
        message (str): Completion message
        details (dict, optional): Additional details to log
    """
    logger.info("-" * 60)
    logger.info(message)
    
    if details:
        for key, value in details.items():
            logger.info(f"  {key}: {value}")
    
    logger.info("=" * 60)


def log_error_and_exit(logger, message, exit_code=1):
    """
    Log an error message and exit the application.
    
    This function follows the requirement to use logging.error() 
    and sys.exit() instead of raising exceptions.
    
    Args:
        logger (logging.Logger): Logger instance
        message (str): Error message
        exit_code (int): Exit code (default: 1)
    """
    logger.error(f"ERROR: {message}")
    logger.error("Application terminated due to error.")
    sys.exit(exit_code)


def log_progress(logger, current, total, item_name="items"):
    """
    Log progress of an operation.
    
    Args:
        logger (logging.Logger): Logger instance
        current (int): Current count
        total (int): Total count
        item_name (str): Name of items being processed
    """
    percentage = (current / total * 100) if total > 0 else 0
    logger.info(f"Progress: {current}/{total} {item_name} ({percentage:.1f}%)")


# Default logger instance
_default_logger = None


def get_logger():
    """
    Get the default logger instance.
    Creates one if it doesn't exist.
    
    Returns:
        logging.Logger: Default logger instance
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_logger()
    return _default_logger
