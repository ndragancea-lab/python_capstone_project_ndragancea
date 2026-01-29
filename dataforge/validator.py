"""
Validator Module
Validates all input parameters and data schema.

This module ensures all parameters are valid before data generation begins.
"""

import os
import sys
import json
from dataforge.logger import get_logger


def validate_path(path, must_exist=True):
    """
    Validate that a path exists and is a directory.
    
    Args:
        path (str): Path to validate
        must_exist (bool): If True, path must exist. If False, can be non-existent
    
    Returns:
        str: Absolute path if valid
    
    Raises:
        SystemExit: If path is invalid
    
    Example:
        >>> validate_path('./output')
        '/absolute/path/to/output'
    """
    logger = get_logger()
    
    # Expand user home directory (~) and convert to absolute
    path = os.path.abspath(os.path.expanduser(path))
    
    if must_exist:
        # Check if exists
        if not os.path.exists(path):
            logger.error(f"Path does not exist: {path}")
            sys.exit(1)
        
        # Check if it's a directory
        if not os.path.isdir(path):
            logger.error(f"Path exists but is not a directory: {path}")
            sys.exit(1)
    
    return path


def validate_files_count(files_count):
    """
    Validate files_count parameter.
    
    Args:
        files_count (int): Number of files to generate
    
    Returns:
        int: Validated files_count
    
    Raises:
        SystemExit: If files_count < 0
    
    Example:
        >>> validate_files_count(10)
        10
        >>> validate_files_count(0)  # Console output mode
        0
    """
    logger = get_logger()
    
    if not isinstance(files_count, int):
        logger.error(f"files_count must be an integer, got: {type(files_count).__name__}")
        sys.exit(1)
    
    if files_count < 0:
        logger.error(f"files_count must be >= 0, got: {files_count}")
        sys.exit(1)
    
    if files_count == 0:
        logger.info("files_count is 0: data will be output to console")
    
    return files_count


def validate_data_lines(data_lines):
    """
    Validate data_lines parameter.
    
    Args:
        data_lines (int): Number of data lines per file
    
    Returns:
        int: Validated data_lines
    
    Raises:
        SystemExit: If data_lines <= 0
    
    Example:
        >>> validate_data_lines(1000)
        1000
    """
    logger = get_logger()
    
    if not isinstance(data_lines, int):
        logger.error(f"data_lines must be an integer, got: {type(data_lines).__name__}")
        sys.exit(1)
    
    if data_lines <= 0:
        logger.error(f"data_lines must be > 0, got: {data_lines}")
        sys.exit(1)
    
    return data_lines


def validate_multiprocessing(multiprocessing_count):
    """
    Validate and correct multiprocessing parameter.
    
    Automatically limits to os.cpu_count() if value exceeds available CPUs.
    
    Args:
        multiprocessing_count (int): Number of processes
    
    Returns:
        int: Validated and corrected multiprocessing count
    
    Raises:
        SystemExit: If multiprocessing_count < 1
    
    Example:
        >>> validate_multiprocessing(4)
        4
        >>> validate_multiprocessing(999)  # If cpu_count() = 8
        8
    """
    logger = get_logger()
    
    if not isinstance(multiprocessing_count, int):
        logger.error(f"multiprocessing must be an integer, got: {type(multiprocessing_count).__name__}")
        sys.exit(1)
    
    if multiprocessing_count < 1:
        logger.error(f"multiprocessing must be >= 1, got: {multiprocessing_count}")
        sys.exit(1)
    
    # Get CPU count
    cpu_count = os.cpu_count() or 1
    
    # Limit to CPU count if exceeds
    if multiprocessing_count > cpu_count:
        logger.warning(f"multiprocessing value {multiprocessing_count} exceeds CPU count ({cpu_count})")
        logger.warning(f"Setting multiprocessing to {cpu_count}")
        multiprocessing_count = cpu_count
    
    return multiprocessing_count


def validate_file_name(file_name):
    """
    Validate file_name parameter.
    
    Args:
        file_name (str): Base file name
    
    Returns:
        str: Validated file name
    
    Raises:
        SystemExit: If file_name is invalid
    
    Example:
        >>> validate_file_name('data')
        'data'
    """
    logger = get_logger()
    
    if not isinstance(file_name, str):
        logger.error(f"file_name must be a string, got: {type(file_name).__name__}")
        sys.exit(1)
    
    if not file_name or file_name.strip() == '':
        logger.error("file_name cannot be empty")
        sys.exit(1)
    
    # Check for invalid characters in filename
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in file_name:
            logger.error(f"file_name contains invalid character '{char}': {file_name}")
            sys.exit(1)
    
    return file_name


def validate_file_prefix(file_prefix):
    """
    Validate file_prefix parameter.
    
    Args:
        file_prefix (str): Prefix type (count, random, uuid)
    
    Returns:
        str: Validated file prefix
    
    Raises:
        SystemExit: If file_prefix is invalid
    
    Example:
        >>> validate_file_prefix('count')
        'count'
    """
    logger = get_logger()
    
    valid_prefixes = ['count', 'random', 'uuid']
    
    if file_prefix not in valid_prefixes:
        logger.error(f"file_prefix must be one of {valid_prefixes}, got: {file_prefix}")
        sys.exit(1)
    
    return file_prefix


def validate_schema_basic(schema):
    """
    Basic validation of data schema (JSON format check).
    
    More detailed schema validation will be done in schema_parser module.
    
    Args:
        schema (str or dict): Data schema (JSON string or dict)
    
    Returns:
        dict: Parsed schema if it's a string, or original dict
    
    Raises:
        SystemExit: If schema is not valid JSON
    
    Example:
        >>> validate_schema_basic('{"id": "int:rand"}')
        {'id': 'int:rand'}
    """
    logger = get_logger()
    
    # If it's already a dict, return it
    if isinstance(schema, dict):
        if not schema:
            logger.error("Schema cannot be empty")
            sys.exit(1)
        return schema
    
    # If it's a string, try to parse as JSON
    if isinstance(schema, str):
        if not schema or schema.strip() == '':
            logger.error("Schema string cannot be empty")
            sys.exit(1)
        
        try:
            parsed_schema = json.loads(schema)
            
            if not isinstance(parsed_schema, dict):
                logger.error("Schema must be a JSON object (dict), not array or primitive")
                sys.exit(1)
            
            if not parsed_schema:
                logger.error("Schema cannot be empty")
                sys.exit(1)
            
            return parsed_schema
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema: {e}")
            sys.exit(1)
    
    logger.error(f"Schema must be a string or dict, got: {type(schema).__name__}")
    sys.exit(1)


def validate_all_parameters(params):
    """
    Validate all parameters at once.
    
    Args:
        params (dict): Dictionary of all parameters
    
    Returns:
        dict: Dictionary with validated and corrected parameters
    
    Raises:
        SystemExit: If any parameter is invalid
    
    Example:
        >>> params = {'path_to_save_files': '.', 'files_count': 10, ...}
        >>> validated = validate_all_parameters(params)
    """
    logger = get_logger()
    
    logger.info("Validating all parameters...")
    
    # Create a copy to avoid modifying original
    validated_params = params.copy()
    
    # Validate path (only if files_count > 0, i.e., saving to files)
    if validated_params['files_count'] > 0:
        validated_params['path_to_save_files'] = validate_path(
            validated_params['path_to_save_files']
        )
    
    # Validate files_count
    validated_params['files_count'] = validate_files_count(
        validated_params['files_count']
    )
    
    # Validate data_lines
    validated_params['data_lines'] = validate_data_lines(
        validated_params['data_lines']
    )
    
    # Validate multiprocessing
    validated_params['multiprocessing'] = validate_multiprocessing(
        validated_params['multiprocessing']
    )
    
    # Validate file_name
    validated_params['file_name'] = validate_file_name(
        validated_params['file_name']
    )
    
    # Validate file_prefix
    validated_params['file_prefix'] = validate_file_prefix(
        validated_params['file_prefix']
    )
    
    # Validate schema (basic JSON check)
    if validated_params.get('data_schema'):
        validated_params['data_schema'] = validate_schema_basic(
            validated_params['data_schema']
        )
    
    logger.info("All parameters validated successfully")
    
    return validated_params
