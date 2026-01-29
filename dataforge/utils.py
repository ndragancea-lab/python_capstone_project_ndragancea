"""
Utilities Module
Helper functions and common utilities used across the application.
"""

import json
import os
import sys
from dataforge.logger import get_logger


def is_json_file(schema_string):
    """
    Check if the provided string is a path to a JSON file or a JSON string.
    
    Args:
        schema_string (str): String to check
    
    Returns:
        bool: True if it's a file path that exists, False otherwise
    
    Example:
        >>> is_json_file('./schema.json')  # If file exists
        True
        >>> is_json_file('{"key": "value"}')
        False
    """
    # Check if it looks like a file path
    if schema_string.endswith('.json') or '/' in schema_string or '\\' in schema_string:
        return os.path.exists(schema_string) and os.path.isfile(schema_string)
    return False


def load_json_from_file(file_path):
    """
    Load JSON data from a file.
    
    Args:
        file_path (str): Path to JSON file
    
    Returns:
        dict: Parsed JSON data
    
    Raises:
        SystemExit: If file cannot be read or JSON is invalid
    
    Example:
        >>> data = load_json_from_file('./schema.json')
    """
    logger = get_logger()
    
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    if not os.path.isfile(file_path):
        logger.error(f"Path is not a file: {file_path}")
        sys.exit(1)
    
    # Try to read and parse JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded JSON from file: {file_path}")
        return data
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file '{file_path}': {e}")
        sys.exit(1)
    
    except (IOError, OSError) as e:
        logger.error(f"Error reading file '{file_path}': {e}")
        sys.exit(1)


def parse_json_string(json_string):
    """
    Parse a JSON string into a Python object.
    
    Args:
        json_string (str): JSON string to parse
    
    Returns:
        dict: Parsed JSON data
    
    Raises:
        SystemExit: If JSON is invalid
    
    Example:
        >>> data = parse_json_string('{"key": "value"}')
    """
    logger = get_logger()
    
    try:
        data = json.loads(json_string)
        logger.info("JSON string parsed successfully")
        return data
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON string: {e}")
        logger.error(f"Provided string: {json_string[:100]}...")
        sys.exit(1)


def load_schema(schema_input):
    """
    Load schema from either a file path or a JSON string.
    
    This is a convenience function that handles both cases.
    
    Args:
        schema_input (str): Either a path to JSON file or a JSON string
    
    Returns:
        dict: Parsed schema data
    
    Raises:
        SystemExit: If schema cannot be loaded or parsed
    
    Example:
        >>> schema = load_schema('./schema.json')  # From file
        >>> schema = load_schema('{"field": "str:rand"}')  # From string
    """
    logger = get_logger()
    
    if is_json_file(schema_input):
        logger.info(f"Loading schema from file: {schema_input}")
        return load_json_from_file(schema_input)
    else:
        logger.info("Parsing schema from command line string")
        return parse_json_string(schema_input)


def safe_exit(logger, message, exit_code=1):
    """
    Safely exit the application with an error message.
    
    This function logs the error and exits without raising exceptions,
    following the project requirement.
    
    Args:
        logger: Logger instance
        message (str): Error message
        exit_code (int): Exit code (default: 1)
    
    Example:
        >>> safe_exit(logger, "Invalid parameter value")
    """
    logger.error(f"ERROR: {message}")
    logger.error("Application terminated due to error.")
    sys.exit(exit_code)


def ensure_directory_exists(path):
    """
    Ensure that a directory exists, create it if it doesn't.
    
    Args:
        path (str): Directory path
    
    Returns:
        bool: True if directory exists or was created successfully
    
    Raises:
        SystemExit: If directory cannot be created
    
    Example:
        >>> ensure_directory_exists('./output')
    """
    logger = get_logger()
    
    # Expand user home directory (~)
    path = os.path.expanduser(path)
    
    # If path already exists
    if os.path.exists(path):
        if os.path.isdir(path):
            return True
        else:
            logger.error(f"Path exists but is not a directory: {path}")
            sys.exit(1)
    
    # Try to create directory
    try:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")
        return True
    
    except (IOError, OSError) as e:
        logger.error(f"Cannot create directory '{path}': {e}")
        sys.exit(1)


def validate_file_path(path):
    """
    Validate that a path exists and is a directory.
    
    Args:
        path (str): Path to validate
    
    Returns:
        str: Absolute path if valid
    
    Raises:
        SystemExit: If path is invalid
    
    Example:
        >>> abs_path = validate_file_path('./output')
    """
    logger = get_logger()
    
    # Expand user home directory (~) and convert to absolute
    path = os.path.abspath(os.path.expanduser(path))
    
    # Check if exists
    if not os.path.exists(path):
        logger.error(f"Path does not exist: {path}")
        sys.exit(1)
    
    # Check if it's a directory
    if not os.path.isdir(path):
        logger.error(f"Path exists but is not a directory: {path}")
        sys.exit(1)
    
    return path


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
    
    Returns:
        str: Formatted size string
    
    Example:
        >>> format_file_size(1024)
        '1.00 KB'
        >>> format_file_size(1048576)
        '1.00 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_absolute_path(path):
    """
    Convert relative path to absolute path.
    
    Args:
        path (str): Relative or absolute path
    
    Returns:
        str: Absolute path
    
    Example:
        >>> get_absolute_path('.')
        '/Users/user/current/directory'
        >>> get_absolute_path('./output')
        '/Users/user/current/directory/output'
    """
    return os.path.abspath(os.path.expanduser(path))


def count_lines_in_file(file_path):
    """
    Count number of lines in a file.
    
    Args:
        file_path (str): Path to file
    
    Returns:
        int: Number of lines in file
    
    Example:
        >>> count = count_lines_in_file('./data.json')
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except (IOError, OSError):
        return 0
