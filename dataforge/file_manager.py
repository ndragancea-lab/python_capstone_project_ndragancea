"""
File Manager Module
Manages file operations for test data generation.

This module handles:
- File name generation with different prefix types
- Writing data to files in JSON Lines format
- Console output
- Directory cleanup
"""

import os
import sys
import json
import uuid
import random
import glob
from dataforge.logger import get_logger


def generate_file_name(base_name, prefix_type, index):
    """
    Generate file name with specified prefix type.
    
    Args:
        base_name (str): Base name for the file
        prefix_type (str): Type of prefix ('count', 'random', 'uuid')
        index (int): Index number for 'count' prefix type
    
    Returns:
        str: Generated file name with .json extension
    
    Raises:
        SystemExit: If prefix_type is invalid
    
    Examples:
        >>> generate_file_name('data', 'count', 1)
        '1_data.json'
        
        >>> generate_file_name('data', 'random', 0)
        '5a3b1c_data.json'  # Random 6-char hex
        
        >>> generate_file_name('data', 'uuid', 0)
        'a1b2c3d4-e5f6-..._data.json'  # UUID
    """
    logger = get_logger()
    
    if prefix_type == 'count':
        # Sequential numbering: 1_data.json, 2_data.json, ...
        file_name = f"{index}_{base_name}.json"
    
    elif prefix_type == 'random':
        # Random 6-character hex prefix
        random_prefix = ''.join(random.choices('0123456789abcdef', k=6))
        file_name = f"{random_prefix}_{base_name}.json"
    
    elif prefix_type == 'uuid':
        # UUID prefix (full UUID)
        uuid_prefix = str(uuid.uuid4())
        file_name = f"{uuid_prefix}_{base_name}.json"
    
    else:
        logger.error(f"Invalid prefix_type: {prefix_type}. Must be 'count', 'random', or 'uuid'")
        sys.exit(1)
    
    return file_name


def write_jsonlines(filepath, data_lines):
    """
    Write data lines to file in JSON Lines format.
    
    Each line is a separate JSON object.
    
    Args:
        filepath (str): Full path to the file
        data_lines (list): List of dictionaries to write
    
    Returns:
        None
    
    Raises:
        SystemExit: If file writing fails
    
    Example:
        >>> data = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        >>> write_jsonlines('/path/to/file.json', data)
    """
    logger = get_logger()
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for line_data in data_lines:
                json_line = json.dumps(line_data)
                f.write(json_line + '\n')
        
        logger.info(f"File written: {filepath} ({len(data_lines)} lines)")
    
    except IOError as e:
        logger.error(f"Failed to write file {filepath}: {e}")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error writing file {filepath}: {e}")
        sys.exit(1)


def write_to_console(data_lines):
    """
    Write data lines to console in JSON format.
    
    Args:
        data_lines (list): List of dictionaries to output
    
    Returns:
        None
    
    Example:
        >>> data = [{'id': 1}, {'id': 2}]
        >>> write_to_console(data)
        {"id": 1}
        {"id": 2}
    """
    logger = get_logger()
    
    logger.debug(f"Writing {len(data_lines)} line(s) to console")
    
    for line_data in data_lines:
        print(json.dumps(line_data))


def clear_directory(path, file_pattern='*.json'):
    """
    Clear directory by removing files matching pattern.
    
    Args:
        path (str): Directory path to clear
        file_pattern (str): File pattern to match (default: '*.json')
    
    Returns:
        int: Number of files removed
    
    Raises:
        SystemExit: If directory doesn't exist or clearing fails
    
    Example:
        >>> clear_directory('/path/to/dir')
        3  # Removed 3 JSON files
    """
    logger = get_logger()
    
    # Validate path
    if not os.path.exists(path):
        logger.error(f"Directory does not exist: {path}")
        sys.exit(1)
    
    if not os.path.isdir(path):
        logger.error(f"Path is not a directory: {path}")
        sys.exit(1)
    
    # Find matching files
    pattern = os.path.join(path, file_pattern)
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        logger.info(f"No files matching '{file_pattern}' found in {path}")
        return 0
    
    # Remove files
    removed_count = 0
    for file_path in matching_files:
        try:
            os.remove(file_path)
            logger.debug(f"Removed: {os.path.basename(file_path)}")
            removed_count += 1
        except Exception as e:
            logger.warning(f"Failed to remove {file_path}: {e}")
    
    logger.info(f"Cleared {removed_count} file(s) from {path}")
    return removed_count


def create_single_file(params):
    """
    Create a single file with generated data.
    
    Args:
        params (dict): Parameters dictionary containing:
            - path (str): Directory path
            - file_name (str): Base file name
            - prefix_type (str): Prefix type ('count', 'random', 'uuid')
            - index (int): File index (for 'count' prefix)
            - data (list): List of data lines to write
    
    Returns:
        str: Full path to created file
    
    Raises:
        SystemExit: If file creation fails
    
    Example:
        >>> params = {
        ...     'path': '/tmp',
        ...     'file_name': 'data',
        ...     'prefix_type': 'count',
        ...     'index': 1,
        ...     'data': [{'id': 1}, {'id': 2}]
        ... }
        >>> filepath = create_single_file(params)
        >>> filepath
        '/tmp/1_data.json'
    """
    logger = get_logger()
    
    # Extract parameters
    directory = params['path']
    base_name = params['file_name']
    prefix_type = params['prefix_type']
    index = params['index']
    data_lines = params['data']
    
    # Generate file name
    file_name = generate_file_name(base_name, prefix_type, index)
    
    # Create full path
    filepath = os.path.join(directory, file_name)
    
    # Write data to file
    write_jsonlines(filepath, data_lines)
    
    return filepath


def create_multiple_files(path, file_name, prefix_type, files_count, data_lines_per_file, generator):
    """
    Create multiple files with generated data.
    
    Args:
        path (str): Directory path
        file_name (str): Base file name
        prefix_type (str): Prefix type ('count', 'random', 'uuid')
        files_count (int): Number of files to create
        data_lines_per_file (int): Number of data lines per file
        generator: DataGenerator instance
    
    Returns:
        list: List of created file paths
    
    Example:
        >>> from dataforge.data_generator import create_generator
        >>> schema = {'id': {'type': 'int', 'strategy': 'rand', 'value': None}}
        >>> gen = create_generator(schema)
        >>> files = create_multiple_files('.', 'data', 'count', 3, 10, gen)
        >>> len(files)
        3
    """
    logger = get_logger()
    
    logger.info(f"Creating {files_count} file(s) with {data_lines_per_file} lines each")
    
    created_files = []
    
    for i in range(1, files_count + 1):
        # Generate data for this file
        data_lines = generator.generate_lines(data_lines_per_file)
        
        # Create file
        params = {
            'path': path,
            'file_name': file_name,
            'prefix_type': prefix_type,
            'index': i,
            'data': data_lines
        }
        
        filepath = create_single_file(params)
        created_files.append(filepath)
        
        logger.debug(f"Created file {i}/{files_count}: {os.path.basename(filepath)}")
    
    logger.info(f"Successfully created {len(created_files)} file(s)")
    
    return created_files


def get_file_stats(filepath):
    """
    Get statistics about a file.
    
    Args:
        filepath (str): Path to the file
    
    Returns:
        dict: File statistics (size, lines, exists)
    
    Example:
        >>> stats = get_file_stats('/path/to/file.json')
        >>> stats
        {'exists': True, 'size_bytes': 1024, 'lines': 10}
    """
    if not os.path.exists(filepath):
        return {
            'exists': False,
            'size_bytes': 0,
            'lines': 0
        }
    
    size_bytes = os.path.getsize(filepath)
    
    # Count lines
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = sum(1 for _ in f)
    except Exception:
        lines = 0
    
    return {
        'exists': True,
        'size_bytes': size_bytes,
        'lines': lines
    }
