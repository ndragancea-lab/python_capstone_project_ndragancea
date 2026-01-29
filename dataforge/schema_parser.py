"""
Schema Parser Module
Parses data schema and converts it to internal representation.

Schema format: {"field_name": "type:value"}

Supported types:
- timestamp: generates timestamps
- str: generates strings
- int: generates integers

Supported strategies:
- rand: random values (timestamp:, str:rand, int:rand)
- list: values from list (str:[val1,val2], int:[1,2,3])
- range: values in range (int:rand(min,max))
- static: static value (str:hello, int:42)
- empty: empty string (str:)
"""

import sys
import re
from dataforge.logger import get_logger


class SchemaParser:
    """
    Schema parser class.
    
    Parses schema dictionary and converts to internal representation.
    """
    
    # Supported types
    VALID_TYPES = ['timestamp', 'str', 'int']
    
    # Supported strategies
    VALID_STRATEGIES = ['rand', 'list', 'range', 'static', 'empty']
    
    def __init__(self, schema):
        """
        Initialize parser with schema.
        
        Args:
            schema (dict): Schema dictionary {"field_name": "type:value"}
        """
        self.logger = get_logger()
        self.schema = schema
        self.parsed_schema = {}
    
    def parse(self):
        """
        Parse entire schema.
        
        Returns:
            dict: Parsed schema with structure:
                {
                    'field_name': {
                        'type': 'str'|'int'|'timestamp',
                        'strategy': 'rand'|'list'|'range'|'static'|'empty',
                        'value': None | list | (from, to) | static_value
                    }
                }
        
        Raises:
            SystemExit: If schema is invalid
        
        Example:
            >>> parser = SchemaParser({"name": "str:rand", "age": "int:rand(18,65)"})
            >>> parsed = parser.parse()
            >>> parsed['name']
            {'type': 'str', 'strategy': 'rand', 'value': None}
        """
        self.logger.info("Parsing schema...")
        
        if not isinstance(self.schema, dict):
            self.logger.error(f"Schema must be a dict, got: {type(self.schema).__name__}")
            sys.exit(1)
        
        if not self.schema:
            self.logger.error("Schema cannot be empty")
            sys.exit(1)
        
        for field_name, field_definition in self.schema.items():
            self.logger.debug(f"Parsing field: {field_name} = {field_definition}")
            self.parsed_schema[field_name] = self.parse_field(field_name, field_definition)
        
        self.logger.info(f"Schema parsed successfully: {len(self.parsed_schema)} field(s)")
        return self.parsed_schema
    
    def parse_field(self, field_name, field_definition):
        """
        Parse a single field definition.
        
        Args:
            field_name (str): Name of the field
            field_definition (str): Field definition (e.g., "str:rand", "int:rand(1,10)")
        
        Returns:
            dict: Parsed field structure
        
        Raises:
            SystemExit: If field definition is invalid
        
        Example:
            >>> parser.parse_field("age", "int:rand(18,65)")
            {'type': 'int', 'strategy': 'range', 'value': (18, 65)}
        """
        if not isinstance(field_definition, str):
            self.logger.error(f"Field '{field_name}': definition must be a string, got: {type(field_definition).__name__}")
            sys.exit(1)
        
        # Split type and value
        data_type, value_part = self._split_type_value(field_name, field_definition)
        
        # Validate type
        self._validate_type(field_name, data_type)
        
        # Parse value based on type
        if data_type == 'timestamp':
            return self._parse_timestamp_value(field_name, value_part)
        elif data_type == 'str':
            return self._parse_str_value(field_name, value_part)
        elif data_type == 'int':
            return self._parse_int_value(field_name, value_part)
    
    def _split_type_value(self, field_name, field_definition):
        """
        Split field definition into type and value parts.
        
        Args:
            field_name (str): Name of the field
            field_definition (str): Field definition
        
        Returns:
            tuple: (type, value_part)
        
        Raises:
            SystemExit: If definition format is invalid
        
        Example:
            >>> parser._split_type_value("name", "str:rand")
            ('str', 'rand')
        """
        if ':' not in field_definition:
            self.logger.error(f"Field '{field_name}': definition must be in format 'type:value', got: {field_definition}")
            sys.exit(1)
        
        parts = field_definition.split(':', 1)
        data_type = parts[0].strip()
        value_part = parts[1] if len(parts) > 1 else ''
        
        return data_type, value_part
    
    def _validate_type(self, field_name, data_type):
        """
        Validate data type.
        
        Args:
            field_name (str): Name of the field
            data_type (str): Data type to validate
        
        Raises:
            SystemExit: If type is invalid
        """
        if data_type not in self.VALID_TYPES:
            self.logger.error(f"Field '{field_name}': invalid type '{data_type}'. Valid types: {self.VALID_TYPES}")
            sys.exit(1)
    
    def _parse_timestamp_value(self, field_name, value_part):
        """
        Parse timestamp field value.
        
        Timestamp only supports empty value (random timestamps).
        
        Args:
            field_name (str): Name of the field
            value_part (str): Value part (should be empty)
        
        Returns:
            dict: {'type': 'timestamp', 'strategy': 'rand', 'value': None}
        
        Example:
            >>> parser._parse_timestamp_value("created_at", "")
            {'type': 'timestamp', 'strategy': 'rand', 'value': None}
        """
        # Timestamp only supports empty value (random)
        if value_part and value_part.strip():
            self.logger.warning(f"Field '{field_name}': timestamp type only supports empty value. Ignoring: {value_part}")
        
        return {
            'type': 'timestamp',
            'strategy': 'rand',
            'value': None
        }
    
    def _parse_str_value(self, field_name, value_part):
        """
        Parse string field value.
        
        Supported formats:
        - str: or str:rand -> random strings
        - str:[val1,val2,val3] -> list of values
        - str:hello -> static value "hello"
        
        Args:
            field_name (str): Name of the field
            value_part (str): Value part
        
        Returns:
            dict: Parsed field structure
        
        Example:
            >>> parser._parse_str_value("name", "rand")
            {'type': 'str', 'strategy': 'rand', 'value': None}
            >>> parser._parse_str_value("status", "[active,inactive]")
            {'type': 'str', 'strategy': 'list', 'value': ['active', 'inactive']}
        """
        value_part = value_part.strip()
        
        # Empty value -> empty string
        if not value_part:
            return {
                'type': 'str',
                'strategy': 'empty',
                'value': ''
            }
        
        # rand -> random strings
        if value_part == 'rand':
            return {
                'type': 'str',
                'strategy': 'rand',
                'value': None
            }
        
        # [val1,val2,val3] -> list
        if value_part.startswith('[') and value_part.endswith(']'):
            values = self._parse_list(field_name, value_part)
            return {
                'type': 'str',
                'strategy': 'list',
                'value': values
            }
        
        # Static value
        return {
            'type': 'str',
            'strategy': 'static',
            'value': value_part
        }
    
    def _parse_int_value(self, field_name, value_part):
        """
        Parse integer field value.
        
        Supported formats:
        - int:rand -> random integers
        - int:rand(min,max) -> random in range
        - int:[1,2,3] -> list of values
        - int:42 -> static value 42
        
        Args:
            field_name (str): Name of the field
            value_part (str): Value part
        
        Returns:
            dict: Parsed field structure
        
        Raises:
            SystemExit: If format is invalid
        
        Example:
            >>> parser._parse_int_value("age", "rand(18,65)")
            {'type': 'int', 'strategy': 'range', 'value': (18, 65)}
        """
        value_part = value_part.strip()
        
        # Empty value not allowed for int
        if not value_part:
            self.logger.error(f"Field '{field_name}': int type requires a value")
            sys.exit(1)
        
        # rand(min,max) -> range
        range_match = re.match(r'rand\((-?\d+),(-?\d+)\)', value_part)
        if range_match:
            min_val = int(range_match.group(1))
            max_val = int(range_match.group(2))
            
            if min_val >= max_val:
                self.logger.error(f"Field '{field_name}': range minimum ({min_val}) must be less than maximum ({max_val})")
                sys.exit(1)
            
            return {
                'type': 'int',
                'strategy': 'range',
                'value': (min_val, max_val)
            }
        
        # rand -> random integers (large range)
        if value_part == 'rand':
            return {
                'type': 'int',
                'strategy': 'rand',
                'value': None
            }
        
        # [1,2,3] -> list
        if value_part.startswith('[') and value_part.endswith(']'):
            values = self._parse_list(field_name, value_part)
            # Convert to integers
            try:
                int_values = [int(v) for v in values]
                return {
                    'type': 'int',
                    'strategy': 'list',
                    'value': int_values
                }
            except ValueError as e:
                self.logger.error(f"Field '{field_name}': list contains non-integer values: {e}")
                sys.exit(1)
        
        # Static integer value
        try:
            static_value = int(value_part)
            return {
                'type': 'int',
                'strategy': 'static',
                'value': static_value
            }
        except ValueError:
            self.logger.error(f"Field '{field_name}': invalid integer value: {value_part}")
            sys.exit(1)
    
    def _parse_list(self, field_name, list_str):
        """
        Parse list notation [val1,val2,val3].
        
        Args:
            field_name (str): Name of the field
            list_str (str): List string "[val1,val2,val3]"
        
        Returns:
            list: List of values (as strings)
        
        Raises:
            SystemExit: If list is empty
        
        Example:
            >>> parser._parse_list("status", "[active,inactive,pending]")
            ['active', 'inactive', 'pending']
        """
        # Remove brackets
        content = list_str[1:-1].strip()
        
        if not content:
            self.logger.error(f"Field '{field_name}': list cannot be empty")
            sys.exit(1)
        
        # Split by comma and strip whitespace
        values = [v.strip() for v in content.split(',')]
        
        # Remove empty values
        values = [v for v in values if v]
        
        if not values:
            self.logger.error(f"Field '{field_name}': list cannot be empty")
            sys.exit(1)
        
        return values


def parse_schema(schema):
    """
    Convenience function to parse schema.
    
    Args:
        schema (dict): Schema dictionary
    
    Returns:
        dict: Parsed schema
    
    Example:
        >>> schema = {"name": "str:rand", "age": "int:rand(18,65)"}
        >>> parsed = parse_schema(schema)
    """
    parser = SchemaParser(schema)
    return parser.parse()
