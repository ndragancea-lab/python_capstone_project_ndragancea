"""
Tests for validator module
"""

import pytest
import os
from dataforge.validator import (
    validate_path,
    validate_files_count,
    validate_data_lines,
    validate_multiprocessing,
    validate_file_name,
    validate_file_prefix,
    validate_schema_basic,
    validate_all_parameters
)


# ================ validate_path tests ================

def test_validate_path_existing_directory(tmp_path):
    """Test validation of existing directory"""
    result = validate_path(str(tmp_path))
    assert os.path.isabs(result)
    assert os.path.isdir(result)


def test_validate_path_nonexistent():
    """Test validation of non-existent path"""
    with pytest.raises(SystemExit) as exc_info:
        validate_path('/nonexistent/path/that/does/not/exist')
    assert exc_info.value.code == 1


def test_validate_path_file_not_directory(tmp_path):
    """Test that path must be a directory, not a file"""
    file_path = tmp_path / "file.txt"
    file_path.write_text("test")
    
    with pytest.raises(SystemExit) as exc_info:
        validate_path(str(file_path))
    assert exc_info.value.code == 1


def test_validate_path_current_directory():
    """Test validation of current directory"""
    result = validate_path('.')
    assert os.path.isabs(result)
    assert os.path.isdir(result)


# ================ validate_files_count tests ================

@pytest.mark.parametrize("files_count,expected", [
    (0, 0),      # Console output mode
    (1, 1),      # Single file
    (10, 10),    # Multiple files
    (100, 100),  # Many files
])
def test_validate_files_count_valid(files_count, expected):
    """Test validation of valid files_count values"""
    result = validate_files_count(files_count)
    assert result == expected


@pytest.mark.parametrize("files_count", [-1, -10, -100])
def test_validate_files_count_negative(files_count):
    """Test that negative files_count raises error"""
    with pytest.raises(SystemExit) as exc_info:
        validate_files_count(files_count)
    assert exc_info.value.code == 1


def test_validate_files_count_not_integer():
    """Test that files_count must be integer"""
    with pytest.raises(SystemExit):
        validate_files_count("10")
    
    with pytest.raises(SystemExit):
        validate_files_count(10.5)


# ================ validate_data_lines tests ================

@pytest.mark.parametrize("data_lines,expected", [
    (1, 1),
    (10, 10),
    (100, 100),
    (1000, 1000),
    (10000, 10000),
])
def test_validate_data_lines_valid(data_lines, expected):
    """Test validation of valid data_lines values"""
    result = validate_data_lines(data_lines)
    assert result == expected


@pytest.mark.parametrize("data_lines", [0, -1, -10])
def test_validate_data_lines_invalid(data_lines):
    """Test that data_lines must be > 0"""
    with pytest.raises(SystemExit) as exc_info:
        validate_data_lines(data_lines)
    assert exc_info.value.code == 1


def test_validate_data_lines_not_integer():
    """Test that data_lines must be integer"""
    with pytest.raises(SystemExit):
        validate_data_lines("100")
    
    with pytest.raises(SystemExit):
        validate_data_lines(100.5)


# ================ validate_multiprocessing tests ================

@pytest.mark.parametrize("mp_count,expected", [
    (1, 1),
    (2, 2),
    (4, 4),
])
def test_validate_multiprocessing_valid(mp_count, expected):
    """Test validation of valid multiprocessing values"""
    result = validate_multiprocessing(mp_count)
    assert result == expected
    assert result <= os.cpu_count()


def test_validate_multiprocessing_exceeds_cpu_count():
    """Test that multiprocessing is limited to cpu_count"""
    cpu_count = os.cpu_count() or 1
    very_large_value = cpu_count + 100
    
    result = validate_multiprocessing(very_large_value)
    
    # Should be limited to cpu_count
    assert result == cpu_count


@pytest.mark.parametrize("mp_count", [0, -1, -10])
def test_validate_multiprocessing_invalid(mp_count):
    """Test that multiprocessing must be >= 1"""
    with pytest.raises(SystemExit) as exc_info:
        validate_multiprocessing(mp_count)
    assert exc_info.value.code == 1


def test_validate_multiprocessing_not_integer():
    """Test that multiprocessing must be integer"""
    with pytest.raises(SystemExit):
        validate_multiprocessing("4")
    
    with pytest.raises(SystemExit):
        validate_multiprocessing(4.5)


# ================ validate_file_name tests ================

@pytest.mark.parametrize("file_name", [
    "data",
    "test_data",
    "my-data",
    "data_123",
    "DATA",
])
def test_validate_file_name_valid(file_name):
    """Test validation of valid file names"""
    result = validate_file_name(file_name)
    assert result == file_name


@pytest.mark.parametrize("file_name", [
    "data/file",      # Contains /
    "data\\file",     # Contains \
    "data:file",      # Contains :
    "data*file",      # Contains *
    "data?file",      # Contains ?
    "data\"file",     # Contains "
    "data<file",      # Contains <
    "data>file",      # Contains >
    "data|file",      # Contains |
])
def test_validate_file_name_invalid_chars(file_name):
    """Test that file names with invalid characters raise error"""
    with pytest.raises(SystemExit) as exc_info:
        validate_file_name(file_name)
    assert exc_info.value.code == 1


def test_validate_file_name_empty():
    """Test that empty file name raises error"""
    with pytest.raises(SystemExit):
        validate_file_name("")
    
    with pytest.raises(SystemExit):
        validate_file_name("   ")


def test_validate_file_name_not_string():
    """Test that file_name must be string"""
    with pytest.raises(SystemExit):
        validate_file_name(123)
    
    with pytest.raises(SystemExit):
        validate_file_name(None)


# ================ validate_file_prefix tests ================

@pytest.mark.parametrize("prefix", ['count', 'random', 'uuid'])
def test_validate_file_prefix_valid(prefix):
    """Test validation of valid file prefixes"""
    result = validate_file_prefix(prefix)
    assert result == prefix


@pytest.mark.parametrize("prefix", ['invalid', 'COUNT', 'Random', 'sequential', ''])
def test_validate_file_prefix_invalid(prefix):
    """Test that invalid prefixes raise error"""
    with pytest.raises(SystemExit) as exc_info:
        validate_file_prefix(prefix)
    assert exc_info.value.code == 1


# ================ validate_schema_basic tests ================

def test_validate_schema_basic_valid_string():
    """Test validation of valid JSON schema string"""
    schema = '{"name": "str:rand", "age": "int:rand"}'
    result = validate_schema_basic(schema)
    
    assert isinstance(result, dict)
    assert 'name' in result
    assert 'age' in result


def test_validate_schema_basic_valid_dict():
    """Test validation of valid schema dict"""
    schema = {"name": "str:rand", "age": "int:rand"}
    result = validate_schema_basic(schema)
    
    assert result == schema
    assert isinstance(result, dict)


def test_validate_schema_basic_invalid_json():
    """Test that invalid JSON raises error"""
    with pytest.raises(SystemExit) as exc_info:
        validate_schema_basic('{"invalid": json}')
    assert exc_info.value.code == 1


def test_validate_schema_basic_empty_string():
    """Test that empty schema string raises error"""
    with pytest.raises(SystemExit):
        validate_schema_basic('')
    
    with pytest.raises(SystemExit):
        validate_schema_basic('   ')


def test_validate_schema_basic_empty_dict():
    """Test that empty schema dict raises error"""
    with pytest.raises(SystemExit) as exc_info:
        validate_schema_basic({})
    assert exc_info.value.code == 1


def test_validate_schema_basic_not_dict():
    """Test that schema must be a dict (object), not array or primitive"""
    # Array
    with pytest.raises(SystemExit):
        validate_schema_basic('["value1", "value2"]')
    
    # String primitive
    with pytest.raises(SystemExit):
        validate_schema_basic('"just a string"')
    
    # Number primitive
    with pytest.raises(SystemExit):
        validate_schema_basic('123')


# ================ validate_all_parameters tests ================

def test_validate_all_parameters_valid(tmp_path):
    """Test validation of all valid parameters"""
    params = {
        'path_to_save_files': str(tmp_path),
        'files_count': 10,
        'file_name': 'test_data',
        'file_prefix': 'count',
        'data_lines': 100,
        'multiprocessing': 2,
        'clear_path': False,
        'data_schema': '{"id": "int:rand"}'
    }
    
    result = validate_all_parameters(params)
    
    assert os.path.isabs(result['path_to_save_files'])
    assert result['files_count'] == 10
    assert result['file_name'] == 'test_data'
    assert result['file_prefix'] == 'count'
    assert result['data_lines'] == 100
    assert result['multiprocessing'] == 2
    assert isinstance(result['data_schema'], dict)


def test_validate_all_parameters_console_mode(tmp_path):
    """Test validation with files_count=0 (console mode)"""
    params = {
        'path_to_save_files': '.',  # Path not validated in console mode
        'files_count': 0,
        'file_name': 'test',
        'file_prefix': 'count',
        'data_lines': 50,
        'multiprocessing': 1,
        'clear_path': False,
        'data_schema': '{"test": "str:rand"}'
    }
    
    result = validate_all_parameters(params)
    
    assert result['files_count'] == 0


def test_validate_all_parameters_multiprocessing_correction():
    """Test that multiprocessing is corrected if exceeds cpu_count"""
    cpu_count = os.cpu_count() or 1
    
    params = {
        'path_to_save_files': '.',
        'files_count': 0,  # Console mode, path not validated
        'file_name': 'data',
        'file_prefix': 'uuid',
        'data_lines': 100,
        'multiprocessing': cpu_count + 100,  # Way over cpu_count
        'clear_path': False,
        'data_schema': '{"id": "int:rand"}'
    }
    
    result = validate_all_parameters(params)
    
    # Should be corrected to cpu_count
    assert result['multiprocessing'] == cpu_count


def test_validate_all_parameters_invalid_files_count():
    """Test that invalid files_count raises error"""
    params = {
        'path_to_save_files': '.',
        'files_count': -5,  # Invalid
        'file_name': 'data',
        'file_prefix': 'count',
        'data_lines': 100,
        'multiprocessing': 1,
        'clear_path': False,
        'data_schema': '{"id": "int:rand"}'
    }
    
    with pytest.raises(SystemExit):
        validate_all_parameters(params)


def test_validate_all_parameters_invalid_data_lines():
    """Test that invalid data_lines raises error"""
    params = {
        'path_to_save_files': '.',
        'files_count': 0,
        'file_name': 'data',
        'file_prefix': 'count',
        'data_lines': 0,  # Invalid (must be > 0)
        'multiprocessing': 1,
        'clear_path': False,
        'data_schema': '{"id": "int:rand"}'
    }
    
    with pytest.raises(SystemExit):
        validate_all_parameters(params)

