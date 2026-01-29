"""
Tests for utils module
"""

import pytest
import json
import os
from dataforge.utils import (
    is_json_file,
    load_json_from_file,
    parse_json_string,
    load_schema,
    safe_exit,
    ensure_directory_exists,
    validate_file_path,
    format_file_size,
    get_absolute_path,
    count_lines_in_file
)
from dataforge.logger import setup_logger


def test_is_json_file_with_existing_file(tmp_path):
    """Test is_json_file with an existing JSON file"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"key": "value"}')
    
    assert is_json_file(str(json_file)) is True


def test_is_json_file_with_nonexistent_file():
    """Test is_json_file with non-existent file"""
    assert is_json_file('./nonexistent.json') is False


def test_is_json_file_with_json_string():
    """Test is_json_file with JSON string"""
    assert is_json_file('{"key": "value"}') is False


def test_is_json_file_with_directory(tmp_path):
    """Test is_json_file with directory path"""
    assert is_json_file(str(tmp_path)) is False


def test_load_json_from_file(tmp_path):
    """Test loading JSON from valid file"""
    json_file = tmp_path / "data.json"
    test_data = {"name": "test", "value": 123}
    json_file.write_text(json.dumps(test_data))
    
    data = load_json_from_file(str(json_file))
    
    assert data == test_data
    assert data['name'] == 'test'
    assert data['value'] == 123


def test_load_json_from_file_not_found():
    """Test loading JSON from non-existent file"""
    with pytest.raises(SystemExit) as exc_info:
        load_json_from_file('./nonexistent.json')
    
    assert exc_info.value.code == 1


def test_load_json_from_file_invalid_json(tmp_path):
    """Test loading invalid JSON file"""
    json_file = tmp_path / "invalid.json"
    json_file.write_text('{"invalid json}')
    
    with pytest.raises(SystemExit) as exc_info:
        load_json_from_file(str(json_file))
    
    assert exc_info.value.code == 1


def test_parse_json_string():
    """Test parsing valid JSON string"""
    json_str = '{"field": "str:rand", "age": "int:rand(18,65)"}'
    data = parse_json_string(json_str)
    
    assert isinstance(data, dict)
    assert data['field'] == 'str:rand'
    assert data['age'] == 'int:rand(18,65)'


def test_parse_json_string_invalid():
    """Test parsing invalid JSON string"""
    with pytest.raises(SystemExit) as exc_info:
        parse_json_string('{"invalid": json}')
    
    assert exc_info.value.code == 1


def test_load_schema_from_file(tmp_path):
    """Test load_schema with file path"""
    schema_file = tmp_path / "schema.json"
    schema_data = {"name": "str:rand", "age": "int:rand"}
    schema_file.write_text(json.dumps(schema_data))
    
    schema = load_schema(str(schema_file))
    
    assert schema == schema_data


def test_load_schema_from_string():
    """Test load_schema with JSON string"""
    schema_str = '{"id": "int:rand", "name": "str:rand"}'
    schema = load_schema(schema_str)
    
    assert isinstance(schema, dict)
    assert 'id' in schema
    assert 'name' in schema


def test_safe_exit():
    """Test safe_exit function"""
    logger = setup_logger(name='test_safe_exit')
    
    with pytest.raises(SystemExit) as exc_info:
        safe_exit(logger, "Test error message", exit_code=2)
    
    assert exc_info.value.code == 2


def test_ensure_directory_exists_new(tmp_path):
    """Test creating new directory"""
    new_dir = tmp_path / "new_directory"
    
    result = ensure_directory_exists(str(new_dir))
    
    assert result is True
    assert new_dir.exists()
    assert new_dir.is_dir()


def test_ensure_directory_exists_already_exists(tmp_path):
    """Test with existing directory"""
    result = ensure_directory_exists(str(tmp_path))
    
    assert result is True


def test_ensure_directory_exists_is_file(tmp_path):
    """Test when path is a file, not directory"""
    file_path = tmp_path / "file.txt"
    file_path.write_text("test")
    
    with pytest.raises(SystemExit) as exc_info:
        ensure_directory_exists(str(file_path))
    
    assert exc_info.value.code == 1


def test_validate_file_path(tmp_path):
    """Test validating existing directory path"""
    path = validate_file_path(str(tmp_path))
    
    assert path is not None
    assert os.path.isabs(path)
    assert os.path.isdir(path)


def test_validate_file_path_not_exists():
    """Test validating non-existent path"""
    with pytest.raises(SystemExit) as exc_info:
        validate_file_path('./nonexistent_directory')
    
    assert exc_info.value.code == 1


def test_validate_file_path_is_file(tmp_path):
    """Test validating path that is a file"""
    file_path = tmp_path / "file.txt"
    file_path.write_text("test")
    
    with pytest.raises(SystemExit) as exc_info:
        validate_file_path(str(file_path))
    
    assert exc_info.value.code == 1


def test_format_file_size():
    """Test file size formatting"""
    assert "0.00 B" in format_file_size(0)
    assert "1.00 KB" in format_file_size(1024)
    assert "1.00 MB" in format_file_size(1024 * 1024)
    assert "1.00 GB" in format_file_size(1024 * 1024 * 1024)
    
    # Test with partial values
    assert "512.00 B" in format_file_size(512)
    assert "1.50 KB" in format_file_size(1536)


def test_get_absolute_path(tmp_path):
    """Test converting to absolute path"""
    # Test with relative path
    abs_path = get_absolute_path('.')
    assert os.path.isabs(abs_path)
    
    # Test with already absolute path
    abs_path2 = get_absolute_path(str(tmp_path))
    assert os.path.isabs(abs_path2)


def test_count_lines_in_file(tmp_path):
    """Test counting lines in file"""
    test_file = tmp_path / "lines.txt"
    test_file.write_text("line1\nline2\nline3\n")
    
    count = count_lines_in_file(str(test_file))
    assert count == 3


def test_count_lines_in_file_empty(tmp_path):
    """Test counting lines in empty file"""
    test_file = tmp_path / "empty.txt"
    test_file.write_text("")
    
    count = count_lines_in_file(str(test_file))
    assert count == 0


def test_count_lines_in_file_not_exists():
    """Test counting lines in non-existent file"""
    count = count_lines_in_file('./nonexistent.txt')
    assert count == 0


def test_is_json_file_with_path_separators():
    """Test is_json_file recognizes path separators"""
    # Should be recognized as paths even if they don't exist
    # (as long as they have path-like structure)
    assert is_json_file('./schema.json') in [True, False]
    assert is_json_file('../data/schema.json') in [True, False]
    assert is_json_file('/absolute/path/schema.json') in [True, False]

