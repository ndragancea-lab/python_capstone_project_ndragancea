"""
Data Generator Module
Generates test data based on parsed schema.

This module takes a parsed schema and generates random data according to
the specified types and strategies.
"""

import random
import string
import time
import json
import uuid
from dataforge.logger import get_logger


class DataGenerator:
    """
    Data generator class.
    
    Generates test data based on parsed schema.
    """
    
    def __init__(self, parsed_schema):
        """
        Initialize generator with parsed schema.
        
        Args:
            parsed_schema (dict): Parsed schema from SchemaParser
                Format: {
                    'field_name': {
                        'type': 'str'|'int'|'timestamp',
                        'strategy': 'rand'|'list'|'range'|'static'|'empty',
                        'value': None | list | (min, max) | static_value
                    }
                }
        
        Example:
            >>> schema = {
            ...     'id': {'type': 'int', 'strategy': 'rand', 'value': None},
            ...     'name': {'type': 'str', 'strategy': 'rand', 'value': None}
            ... }
            >>> generator = DataGenerator(schema)
        """
        self.logger = get_logger()
        self.parsed_schema = parsed_schema
        self.logger.debug(f"DataGenerator initialized with {len(parsed_schema)} field(s)")
    
    def generate_line(self):
        """
        Generate one line of data (as dict).
        
        Returns:
            dict: Generated data line with all fields
        
        Example:
            >>> generator.generate_line()
            {'id': 12345, 'name': 'a1b2c3d4', 'timestamp': 1706543210.123}
        """
        line = {}
        
        for field_name, field_config in self.parsed_schema.items():
            value = self._generate_field_value(field_config)
            line[field_name] = value
        
        return line
    
    def generate_lines(self, count):
        """
        Generate multiple lines of data.
        
        Args:
            count (int): Number of lines to generate
        
        Returns:
            list: List of generated data lines
        
        Example:
            >>> lines = generator.generate_lines(10)
            >>> len(lines)
            10
        """
        self.logger.debug(f"Generating {count} line(s) of data")
        
        lines = []
        for _ in range(count):
            line = self.generate_line()
            lines.append(line)
        
        return lines
    
    def generate_line_json(self):
        """
        Generate one line of data as JSON string.
        
        Returns:
            str: JSON string of generated data
        
        Example:
            >>> generator.generate_line_json()
            '{"id": 12345, "name": "test"}'
        """
        line = self.generate_line()
        return json.dumps(line)
    
    def _generate_field_value(self, field_config):
        """
        Generate value for a single field based on its config.
        
        Args:
            field_config (dict): Field configuration from parsed schema
        
        Returns:
            any: Generated value (int, str, float, or None)
        
        Example:
            >>> config = {'type': 'int', 'strategy': 'rand', 'value': None}
            >>> generator._generate_field_value(config)
            42
        """
        field_type = field_config['type']
        strategy = field_config['strategy']
        value = field_config['value']
        
        # Timestamp type
        if field_type == 'timestamp':
            return generate_timestamp()
        
        # String type
        elif field_type == 'str':
            if strategy == 'rand':
                return generate_str_rand()
            elif strategy == 'list':
                return generate_from_list(value)
            elif strategy == 'static':
                return generate_static(value)
            elif strategy == 'empty':
                return generate_empty('str')
        
        # Integer type
        elif field_type == 'int':
            if strategy == 'rand':
                return generate_int_rand()
            elif strategy == 'range':
                min_val, max_val = value
                return generate_int_range(min_val, max_val)
            elif strategy == 'list':
                return generate_from_list(value)
            elif strategy == 'static':
                return generate_static(value)
        
        # Fallback (should not happen with validated schema)
        self.logger.warning(f"Unknown field type/strategy: {field_type}/{strategy}")
        return None


# ================ Generator Functions ================

def generate_timestamp():
    """
    Generate current timestamp.
    
    Returns:
        float: Current Unix timestamp with millisecond precision
    
    Example:
        >>> ts = generate_timestamp()
        >>> isinstance(ts, float)
        True
        >>> ts > 0
        True
    """
    return time.time()


def generate_str_rand():
    """
    Generate random string (UUID-based).
    
    Returns:
        str: Random string (UUID without hyphens, first 8 chars)
    
    Example:
        >>> s = generate_str_rand()
        >>> len(s)
        8
        >>> isinstance(s, str)
        True
    """
    # Generate UUID and take first 8 characters (without hyphens)
    return uuid.uuid4().hex[:8]


def generate_int_rand():
    """
    Generate random integer in default range.
    
    Returns:
        int: Random integer between 0 and 999999
    
    Example:
        >>> n = generate_int_rand()
        >>> isinstance(n, int)
        True
        >>> 0 <= n <= 999999
        True
    """
    return random.randint(0, 999999)


def generate_from_list(values):
    """
    Generate value by randomly selecting from list.
    
    Args:
        values (list): List of possible values
    
    Returns:
        any: Randomly selected value from list
    
    Example:
        >>> values = ['active', 'inactive', 'pending']
        >>> result = generate_from_list(values)
        >>> result in values
        True
    """
    return random.choice(values)


def generate_int_range(min_val, max_val):
    """
    Generate random integer in specified range.
    
    Args:
        min_val (int): Minimum value (inclusive)
        max_val (int): Maximum value (inclusive)
    
    Returns:
        int: Random integer in range [min_val, max_val]
    
    Example:
        >>> n = generate_int_range(18, 65)
        >>> 18 <= n <= 65
        True
    """
    return random.randint(min_val, max_val)


def generate_static(value):
    """
    Return static value as-is.
    
    Args:
        value (any): Static value to return
    
    Returns:
        any: The same value that was passed in
    
    Example:
        >>> generate_static("hello")
        'hello'
        >>> generate_static(42)
        42
    """
    return value


def generate_empty(field_type):
    """
    Generate empty value based on field type.
    
    Args:
        field_type (str): Field type ('str' or other)
    
    Returns:
        str or None: Empty string for 'str', None for others
    
    Example:
        >>> generate_empty('str')
        ''
        >>> generate_empty('int') is None
        True
    """
    if field_type == 'str':
        return ''
    return None


# ================ Convenience Function ================

def create_generator(parsed_schema):
    """
    Convenience function to create DataGenerator instance.
    
    Args:
        parsed_schema (dict): Parsed schema from SchemaParser
    
    Returns:
        DataGenerator: Initialized generator instance
    
    Example:
        >>> schema = {'id': {'type': 'int', 'strategy': 'rand', 'value': None}}
        >>> gen = create_generator(schema)
        >>> isinstance(gen, DataGenerator)
        True
    """
    return DataGenerator(parsed_schema)
