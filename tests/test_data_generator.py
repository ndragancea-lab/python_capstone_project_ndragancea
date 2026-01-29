"""
Tests for data_generator module
"""

import pytest
import json
import time
from dataforge.data_generator import (
    DataGenerator,
    generate_timestamp,
    generate_str_rand,
    generate_int_rand,
    generate_from_list,
    generate_int_range,
    generate_static,
    generate_empty,
    create_generator
)


# ================ Generator functions tests ================

def test_generate_timestamp():
    """Test timestamp generation"""
    ts = generate_timestamp()
    
    assert isinstance(ts, float)
    assert ts > 0
    
    # Should be close to current time
    current_time = time.time()
    assert abs(ts - current_time) < 1  # Within 1 second


def test_generate_str_rand():
    """Test random string generation"""
    s = generate_str_rand()
    
    assert isinstance(s, str)
    assert len(s) == 8
    
    # Should be different each time (with very high probability)
    s2 = generate_str_rand()
    assert s != s2  # Very unlikely to be the same


def test_generate_int_rand():
    """Test random integer generation"""
    n = generate_int_rand()
    
    assert isinstance(n, int)
    assert 0 <= n <= 999999


def test_generate_int_rand_distribution():
    """Test that random integers have good distribution"""
    values = [generate_int_rand() for _ in range(100)]
    
    # All should be in range
    assert all(0 <= v <= 999999 for v in values)
    
    # Should have variety (at least 50 unique values out of 100)
    assert len(set(values)) >= 50


@pytest.mark.parametrize("values,expected_in", [
    (['a', 'b', 'c'], ['a', 'b', 'c']),
    ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
    (['active', 'inactive'], ['active', 'inactive']),
    ([100], [100]),  # Single value
])
def test_generate_from_list(values, expected_in):
    """Test generation from list"""
    result = generate_from_list(values)
    assert result in expected_in


def test_generate_from_list_distribution():
    """Test that list selection has good distribution"""
    values = ['a', 'b', 'c']
    results = [generate_from_list(values) for _ in range(100)]
    
    # All results should be from the list
    assert all(r in values for r in results)
    
    # Should have all values represented (with high probability)
    assert 'a' in results
    assert 'b' in results
    assert 'c' in results


@pytest.mark.parametrize("min_val,max_val", [
    (0, 10),
    (1, 100),
    (18, 65),
    (-10, 10),
    (-100, -50),
])
def test_generate_int_range(min_val, max_val):
    """Test integer range generation"""
    n = generate_int_range(min_val, max_val)
    
    assert isinstance(n, int)
    assert min_val <= n <= max_val


def test_generate_int_range_distribution():
    """Test that range generation covers the range"""
    results = [generate_int_range(1, 5) for _ in range(100)]
    
    # All should be in range
    assert all(1 <= r <= 5 for r in results)
    
    # Should cover most of the range
    unique_values = set(results)
    assert len(unique_values) >= 3  # At least 3 out of 5 values


@pytest.mark.parametrize("value,expected", [
    ("hello", "hello"),
    (42, 42),
    (3.14, 3.14),
    (True, True),
    (None, None),
])
def test_generate_static(value, expected):
    """Test static value generation"""
    result = generate_static(value)
    assert result == expected


def test_generate_empty_str():
    """Test empty string generation"""
    result = generate_empty('str')
    assert result == ''
    assert isinstance(result, str)


def test_generate_empty_other():
    """Test empty value for non-string types"""
    result = generate_empty('int')
    assert result is None
    
    result = generate_empty('timestamp')
    assert result is None


# ================ DataGenerator class tests ================

def test_data_generator_init():
    """Test DataGenerator initialization"""
    schema = {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None},
        'name': {'type': 'str', 'strategy': 'rand', 'value': None}
    }
    
    gen = DataGenerator(schema)
    
    assert gen.parsed_schema == schema
    assert len(gen.parsed_schema) == 2


def test_generate_line_timestamp():
    """Test generating line with timestamp field"""
    schema = {
        'created_at': {'type': 'timestamp', 'strategy': 'rand', 'value': None}
    }
    
    gen = DataGenerator(schema)
    line = gen.generate_line()
    
    assert 'created_at' in line
    assert isinstance(line['created_at'], float)
    assert line['created_at'] > 0


def test_generate_line_str_rand():
    """Test generating line with random string"""
    schema = {
        'name': {'type': 'str', 'strategy': 'rand', 'value': None}
    }
    
    gen = DataGenerator(schema)
    line = gen.generate_line()
    
    assert 'name' in line
    assert isinstance(line['name'], str)
    assert len(line['name']) == 8


def test_generate_line_str_list():
    """Test generating line with string from list"""
    schema = {
        'status': {'type': 'str', 'strategy': 'list', 'value': ['active', 'inactive']}
    }
    
    gen = DataGenerator(schema)
    line = gen.generate_line()
    
    assert 'status' in line
    assert line['status'] in ['active', 'inactive']


def test_generate_line_str_static():
    """Test generating line with static string"""
    schema = {
        'email': {'type': 'str', 'strategy': 'static', 'value': 'test@example.com'}
    }
    
    gen = DataGenerator(schema)
    line = gen.generate_line()
    
    assert 'email' in line
    assert line['email'] == 'test@example.com'


def test_generate_line_str_empty():
    """Test generating line with empty string"""
    schema = {
        'description': {'type': 'str', 'strategy': 'empty', 'value': ''}
    }
    
    gen = DataGenerator(schema)
    line = gen.generate_line()
    
    assert 'description' in line
    assert line['description'] == ''


def test_generate_line_int_rand():
    """Test generating line with random integer"""
    schema = {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None}
    }
    
    gen = DataGenerator(schema)
    line = gen.generate_line()
    
    assert 'id' in line
    assert isinstance(line['id'], int)
    assert 0 <= line['id'] <= 999999


def test_generate_line_int_range():
    """Test generating line with integer in range"""
    schema = {
        'age': {'type': 'int', 'strategy': 'range', 'value': (18, 65)}
    }
    
    gen = DataGenerator(schema)
    line = gen.generate_line()
    
    assert 'age' in line
    assert isinstance(line['age'], int)
    assert 18 <= line['age'] <= 65


def test_generate_line_int_list():
    """Test generating line with integer from list"""
    schema = {
        'priority': {'type': 'int', 'strategy': 'list', 'value': [1, 2, 3, 4, 5]}
    }
    
    gen = DataGenerator(schema)
    line = gen.generate_line()
    
    assert 'priority' in line
    assert line['priority'] in [1, 2, 3, 4, 5]


def test_generate_line_int_static():
    """Test generating line with static integer"""
    schema = {
        'count': {'type': 'int', 'strategy': 'static', 'value': 100}
    }
    
    gen = DataGenerator(schema)
    line = gen.generate_line()
    
    assert 'count' in line
    assert line['count'] == 100


def test_generate_line_complex_schema():
    """Test generating line with complex schema (multiple fields)"""
    schema = {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None},
        'timestamp': {'type': 'timestamp', 'strategy': 'rand', 'value': None},
        'name': {'type': 'str', 'strategy': 'rand', 'value': None},
        'age': {'type': 'int', 'strategy': 'range', 'value': (18, 65)},
        'status': {'type': 'str', 'strategy': 'list', 'value': ['active', 'inactive']},
        'email': {'type': 'str', 'strategy': 'static', 'value': 'test@example.com'},
        'count': {'type': 'int', 'strategy': 'static', 'value': 10}
    }
    
    gen = DataGenerator(schema)
    line = gen.generate_line()
    
    # Check all fields present
    assert len(line) == 7
    assert 'id' in line
    assert 'timestamp' in line
    assert 'name' in line
    assert 'age' in line
    assert 'status' in line
    assert 'email' in line
    assert 'count' in line
    
    # Check types
    assert isinstance(line['id'], int)
    assert isinstance(line['timestamp'], float)
    assert isinstance(line['name'], str)
    assert isinstance(line['age'], int)
    assert isinstance(line['status'], str)
    assert isinstance(line['email'], str)
    assert isinstance(line['count'], int)
    
    # Check values
    assert 0 <= line['id'] <= 999999
    assert line['timestamp'] > 0
    assert len(line['name']) == 8
    assert 18 <= line['age'] <= 65
    assert line['status'] in ['active', 'inactive']
    assert line['email'] == 'test@example.com'
    assert line['count'] == 10


def test_generate_lines_count():
    """Test generating multiple lines"""
    schema = {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None}
    }
    
    gen = DataGenerator(schema)
    
    # Generate 10 lines
    lines = gen.generate_lines(10)
    
    assert len(lines) == 10
    assert all('id' in line for line in lines)
    assert all(isinstance(line['id'], int) for line in lines)


def test_generate_lines_variety():
    """Test that multiple lines have variety"""
    schema = {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None},
        'name': {'type': 'str', 'strategy': 'rand', 'value': None}
    }
    
    gen = DataGenerator(schema)
    lines = gen.generate_lines(50)
    
    # Check IDs have variety
    ids = [line['id'] for line in lines]
    assert len(set(ids)) >= 40  # At least 40 unique IDs out of 50
    
    # Check names have variety
    names = [line['name'] for line in lines]
    assert len(set(names)) >= 40  # At least 40 unique names out of 50


def test_generate_line_json():
    """Test generating line as JSON string"""
    schema = {
        'id': {'type': 'int', 'strategy': 'static', 'value': 42},
        'name': {'type': 'str', 'strategy': 'static', 'value': 'test'}
    }
    
    gen = DataGenerator(schema)
    json_str = gen.generate_line_json()
    
    # Should be valid JSON
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    
    # Check content
    assert parsed['id'] == 42
    assert parsed['name'] == 'test'


def test_generate_line_json_complex():
    """Test JSON generation with complex types"""
    schema = {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None},
        'timestamp': {'type': 'timestamp', 'strategy': 'rand', 'value': None},
        'name': {'type': 'str', 'strategy': 'rand', 'value': None}
    }
    
    gen = DataGenerator(schema)
    json_str = gen.generate_line_json()
    
    # Should be valid JSON
    parsed = json.loads(json_str)
    
    # Check all fields present
    assert 'id' in parsed
    assert 'timestamp' in parsed
    assert 'name' in parsed


# ================ Consistency tests ================

def test_static_values_consistent():
    """Test that static values are consistent across generations"""
    schema = {
        'email': {'type': 'str', 'strategy': 'static', 'value': 'test@example.com'},
        'count': {'type': 'int', 'strategy': 'static', 'value': 100}
    }
    
    gen = DataGenerator(schema)
    lines = gen.generate_lines(10)
    
    # All emails should be the same
    emails = [line['email'] for line in lines]
    assert all(email == 'test@example.com' for email in emails)
    
    # All counts should be the same
    counts = [line['count'] for line in lines]
    assert all(count == 100 for count in counts)


def test_empty_values_consistent():
    """Test that empty values are consistent"""
    schema = {
        'description': {'type': 'str', 'strategy': 'empty', 'value': ''}
    }
    
    gen = DataGenerator(schema)
    lines = gen.generate_lines(10)
    
    # All descriptions should be empty string
    descriptions = [line['description'] for line in lines]
    assert all(desc == '' for desc in descriptions)


# ================ Integration tests ================

def test_create_generator_function():
    """Test create_generator convenience function"""
    schema = {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None}
    }
    
    gen = create_generator(schema)
    
    assert isinstance(gen, DataGenerator)
    assert gen.parsed_schema == schema


def test_end_to_end_generation():
    """Test end-to-end generation process"""
    # Simulate a typical schema
    schema = {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None},
        'created_at': {'type': 'timestamp', 'strategy': 'rand', 'value': None},
        'username': {'type': 'str', 'strategy': 'rand', 'value': None},
        'age': {'type': 'int', 'strategy': 'range', 'value': (18, 65)},
        'status': {'type': 'str', 'strategy': 'list', 'value': ['active', 'inactive', 'pending']},
        'role': {'type': 'str', 'strategy': 'static', 'value': 'user'}
    }
    
    gen = create_generator(schema)
    
    # Generate 100 lines
    lines = gen.generate_lines(100)
    
    # Verify count
    assert len(lines) == 100
    
    # Verify all lines have all fields
    for line in lines:
        assert len(line) == 6
        assert all(field in line for field in schema.keys())
    
    # Verify types
    for line in lines:
        assert isinstance(line['id'], int)
        assert isinstance(line['created_at'], float)
        assert isinstance(line['username'], str)
        assert isinstance(line['age'], int)
        assert isinstance(line['status'], str)
        assert isinstance(line['role'], str)
    
    # Verify ranges and values
    for line in lines:
        assert 0 <= line['id'] <= 999999
        assert line['created_at'] > 0
        assert len(line['username']) == 8
        assert 18 <= line['age'] <= 65
        assert line['status'] in ['active', 'inactive', 'pending']
        assert line['role'] == 'user'

