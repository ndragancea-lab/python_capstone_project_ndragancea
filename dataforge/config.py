"""
Configuration Manager Module
Handles loading and managing default configuration from default.ini file.

This module reads default values from the configuration file and provides
them to other parts of the application.
"""

import configparser
import os
import json
from dataforge.logger import get_logger


# Default configuration file name
DEFAULT_CONFIG_FILE = 'default.ini'


def load_default_config(config_file=None):
    """
    Load configuration from default.ini file.
    
    Args:
        config_file (str, optional): Path to config file. 
                                      If None, searches for default.ini in current directory.
    
    Returns:
        configparser.ConfigParser: Loaded configuration object
        
    Raises:
        SystemExit: If config file doesn't exist or cannot be read
    
    Example:
        >>> config = load_default_config()
        >>> files_count = config.getint('DEFAULT', 'files_count')
    """
    logger = get_logger()
    
    # Determine config file path
    if config_file is None:
        config_file = DEFAULT_CONFIG_FILE
    
    # Check if file exists
    if not os.path.exists(config_file):
        logger.warning(f"Configuration file '{config_file}' not found. Using hardcoded defaults.")
        return get_hardcoded_defaults()
    
    # Load configuration
    config = configparser.ConfigParser()
    
    try:
        config.read(config_file, encoding='utf-8')
        logger.info(f"Configuration loaded from '{config_file}'")
        return config
    except Exception as e:
        logger.warning(f"Error reading config file '{config_file}': {e}. Using hardcoded defaults.")
        return get_hardcoded_defaults()


def get_hardcoded_defaults():
    """
    Get hardcoded default configuration when default.ini is not available.
    
    Returns:
        configparser.ConfigParser: Configuration with hardcoded defaults
    """
    config = configparser.ConfigParser()
    
    config['DEFAULT'] = {
        'files_count': '10',
        'file_name': 'generated_data',
        'file_prefix': 'count',
        'data_lines': '1000',
        'multiprocessing': '1'
    }
    
    config['SCHEMA'] = {
        'default_schema': '{"id": "int:rand", "timestamp": "timestamp:", "value": "str:rand"}'
    }
    
    return config


def get_config_value(config, section, key, fallback=None):
    """
    Get a configuration value with fallback.
    
    Args:
        config (configparser.ConfigParser): Configuration object
        section (str): Configuration section
        key (str): Configuration key
        fallback: Fallback value if key doesn't exist
    
    Returns:
        str: Configuration value or fallback
    
    Example:
        >>> config = load_default_config()
        >>> file_name = get_config_value(config, 'DEFAULT', 'file_name', 'data')
    """
    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return fallback


def get_config_int(config, section, key, fallback=0):
    """
    Get an integer configuration value with fallback.
    
    Args:
        config (configparser.ConfigParser): Configuration object
        section (str): Configuration section
        key (str): Configuration key
        fallback (int): Fallback value if key doesn't exist
    
    Returns:
        int: Configuration value or fallback
    """
    try:
        return config.getint(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return fallback


def create_default_config(config_file=None):
    """
    Create a default.ini file if it doesn't exist.
    
    Args:
        config_file (str, optional): Path to config file to create.
                                      If None, creates default.ini in current directory.
    
    Returns:
        bool: True if file was created, False if it already exists
    
    Example:
        >>> if create_default_config():
        ...     print("Config file created")
    """
    logger = get_logger()
    
    if config_file is None:
        config_file = DEFAULT_CONFIG_FILE
    
    # Don't overwrite existing file
    if os.path.exists(config_file):
        logger.info(f"Configuration file '{config_file}' already exists.")
        return False
    
    # Create default configuration
    config = configparser.ConfigParser()
    
    config['DEFAULT'] = {
        'files_count': '10',
        'file_name': 'generated_data',
        'file_prefix': 'count',
        'data_lines': '1000',
        'multiprocessing': '1'
    }
    
    config['SCHEMA'] = {
        'default_schema': '{"id": "int:rand", "timestamp": "timestamp:", "value": "str:rand"}'
    }
    
    # Write to file
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("# DataForge Default Configuration\n")
            f.write("# All parameter names match command line argument names\n\n")
            config.write(f)
        
        logger.info(f"Created default configuration file: {config_file}")
        return True
    
    except (IOError, OSError) as e:
        logger.warning(f"Could not create config file '{config_file}': {e}")
        return False


def merge_config_with_args(config, args):
    """
    Merge configuration from default.ini with command line arguments.
    Command line arguments take precedence over config values.
    
    Args:
        config (configparser.ConfigParser): Configuration object
        args (argparse.Namespace): Parsed command line arguments
    
    Returns:
        dict: Merged configuration as dictionary
    
    Example:
        >>> config = load_default_config()
        >>> args = parser.parse_args()
        >>> params = merge_config_with_args(config, args)
    """
    # Start with config values
    params = {
        'path_to_save_files': args.path_to_save_files,
        'files_count': get_config_int(config, 'DEFAULT', 'files_count', 10),
        'file_name': get_config_value(config, 'DEFAULT', 'file_name', 'generated_data'),
        'file_prefix': get_config_value(config, 'DEFAULT', 'file_prefix', 'count'),
        'data_lines': get_config_int(config, 'DEFAULT', 'data_lines', 1000),
        'multiprocessing': get_config_int(config, 'DEFAULT', 'multiprocessing', 1),
        'clear_path': args.clear_path,
        'data_schema': get_config_value(config, 'SCHEMA', 'default_schema', None)
    }
    
    # Override with command line arguments if provided
    if args.files_count is not None:
        params['files_count'] = args.files_count
    
    if args.file_name is not None:
        params['file_name'] = args.file_name
    
    if args.file_prefix is not None:
        params['file_prefix'] = args.file_prefix
    
    if args.data_lines is not None:
        params['data_lines'] = args.data_lines
    
    if args.multiprocessing is not None:
        params['multiprocessing'] = args.multiprocessing
    
    if args.data_schema is not None:
        params['data_schema'] = args.data_schema
    
    return params
