"""
Tests for file_manager module
"""

import pytest
import os
import json
import glob
from dataforge.file_manager import (
    generate_file_name,
    write_jsonlines,
    write_to_console,
    clear_directory,
    create_single_file,
    create_multiple_files,
    get_file_stats
)
from dataforge.data_generator import create_generator


# ================ Fixtures ================

@pytest.fixture
def sample_data():
    """Sample data for testing"""
    return [
        {'id': 1, 'name': 'Alice', 'age': 30},
        {'id': 2, 'name': 'Bob', 'age': 25},
        {'id': 3, 'name': 'Charlie', 'age': 35}
    ]


@pytest.fixture
def test_generator():
    """Create a simple generator for testing"""
    schema = {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None},
        'name': {'type': 'str', 'strategy': 'rand', 'value': None}
    }
    return create_generator(schema)


# ================ generate_file_name tests ================

def test_generate_file_name_count():
    """Test file name generation with count prefix"""
    name = generate_file_name('data', 'count', 1)
    assert name == '1_data.json'
    
    name = generate_file_name('test', 'count', 42)
    assert name == '42_test.json'


def test_generate_file_name_random():
    """Test file name generation with random prefix"""
    name = generate_file_name('data', 'random', 0)
    
    # Should have format: xxxxxx_data.json (6 hex chars)
    assert name.endswith('_data.json')
    prefix = name.split('_')[0]
    assert len(prefix) == 6
    assert all(c in '0123456789abcdef' for c in prefix)


def test_generate_file_name_uuid():
    """Test file name generation with UUID prefix"""
    name = generate_file_name('data', 'uuid', 0)
    
    # Should have format: uuid_data.json
    assert name.endswith('_data.json')
    
    # UUID should have dashes
    prefix = name.split('_data.json')[0]
    assert '-' in prefix
    
    # Should be valid UUID format (8-4-4-4-12)
    parts = prefix.split('-')
    assert len(parts) == 5


def test_generate_file_name_invalid_prefix():
    """Test that invalid prefix type raises error"""
    with pytest.raises(SystemExit) as exc_info:
        generate_file_name('data', 'invalid', 1)
    assert exc_info.value.code == 1


def test_generate_file_name_uniqueness():
    """Test that random and UUID prefixes generate unique names"""
    # Random prefixes
    names_random = [generate_file_name('data', 'random', 0) for _ in range(10)]
    assert len(set(names_random)) == 10  # All unique
    
    # UUID prefixes
    names_uuid = [generate_file_name('data', 'uuid', 0) for _ in range(10)]
    assert len(set(names_uuid)) == 10  # All unique


# ================ write_jsonlines tests ================

def test_write_jsonlines_basic(tmp_path, sample_data):
    """Test basic JSON Lines writing"""
    filepath = tmp_path / "test.json"
    
    write_jsonlines(str(filepath), sample_data)
    
    # File should exist
    assert filepath.exists()
    
    # Read and verify content
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    assert len(lines) == 3
    
    # Each line should be valid JSON
    for i, line in enumerate(lines):
        data = json.loads(line.strip())
        assert data == sample_data[i]


def test_write_jsonlines_empty(tmp_path):
    """Test writing empty data"""
    filepath = tmp_path / "empty.json"
    
    write_jsonlines(str(filepath), [])
    
    assert filepath.exists()
    
    # Should be empty file
    assert filepath.stat().st_size == 0


def test_write_jsonlines_single_line(tmp_path):
    """Test writing single line"""
    filepath = tmp_path / "single.json"
    data = [{'id': 1, 'value': 'test'}]
    
    write_jsonlines(str(filepath), data)
    
    with open(filepath, 'r') as f:
        content = f.read().strip()
    
    assert content == '{"id": 1, "value": "test"}'


def test_write_jsonlines_special_characters(tmp_path):
    """Test writing data with special characters"""
    filepath = tmp_path / "special.json"
    data = [
        {'text': 'Hello, "World"!'},
        {'text': 'Line\nBreak'},
        {'text': 'Tab\there'}
    ]
    
    write_jsonlines(str(filepath), data)
    
    # Should be able to read back
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        parsed = json.loads(line.strip())
        assert parsed == data[i]


# ================ write_to_console tests ================

def test_write_to_console(capsys, sample_data):
    """Test console output"""
    write_to_console(sample_data)
    
    captured = capsys.readouterr()
    lines = captured.out.strip().split('\n')
    
    assert len(lines) == 3
    
    # Each line should be valid JSON
    for i, line in enumerate(lines):
        data = json.loads(line)
        assert data == sample_data[i]


def test_write_to_console_empty(capsys):
    """Test console output with empty data"""
    write_to_console([])
    
    captured = capsys.readouterr()
    # Should be empty (only debug log, no data output)
    assert captured.out.strip() == ''


# ================ clear_directory tests ================

def test_clear_directory_basic(tmp_path):
    """Test clearing directory with JSON files"""
    # Create some test files
    (tmp_path / "1_data.json").write_text('{"id": 1}')
    (tmp_path / "2_data.json").write_text('{"id": 2}')
    (tmp_path / "3_data.json").write_text('{"id": 3}')
    (tmp_path / "readme.txt").write_text('Not a JSON file')
    
    # Clear JSON files
    removed = clear_directory(str(tmp_path), '*.json')
    
    assert removed == 3
    
    # JSON files should be gone
    assert not (tmp_path / "1_data.json").exists()
    assert not (tmp_path / "2_data.json").exists()
    assert not (tmp_path / "3_data.json").exists()
    
    # Other file should remain
    assert (tmp_path / "readme.txt").exists()


def test_clear_directory_empty(tmp_path):
    """Test clearing empty directory"""
    removed = clear_directory(str(tmp_path), '*.json')
    
    assert removed == 0


def test_clear_directory_no_matches(tmp_path):
    """Test clearing directory with no matching files"""
    (tmp_path / "file.txt").write_text('test')
    
    removed = clear_directory(str(tmp_path), '*.json')
    
    assert removed == 0
    assert (tmp_path / "file.txt").exists()


def test_clear_directory_custom_pattern(tmp_path):
    """Test clearing with custom pattern"""
    (tmp_path / "data.json").write_text('{}')
    (tmp_path / "backup.bak").write_text('{}')
    (tmp_path / "log.txt").write_text('{}')
    
    # Clear only .bak files
    removed = clear_directory(str(tmp_path), '*.bak')
    
    assert removed == 1
    assert (tmp_path / "data.json").exists()
    assert not (tmp_path / "backup.bak").exists()
    assert (tmp_path / "log.txt").exists()


def test_clear_directory_nonexistent():
    """Test clearing non-existent directory"""
    with pytest.raises(SystemExit) as exc_info:
        clear_directory('/nonexistent/path')
    assert exc_info.value.code == 1


def test_clear_directory_is_file(tmp_path):
    """Test clearing a file path (not directory)"""
    file_path = tmp_path / "file.txt"
    file_path.write_text('test')
    
    with pytest.raises(SystemExit) as exc_info:
        clear_directory(str(file_path))
    assert exc_info.value.code == 1


# ================ create_single_file tests ================

def test_create_single_file_basic(tmp_path, sample_data):
    """Test creating a single file"""
    params = {
        'path': str(tmp_path),
        'file_name': 'test',
        'prefix_type': 'count',
        'index': 1,
        'data': sample_data
    }
    
    filepath = create_single_file(params)
    
    assert filepath == str(tmp_path / '1_test.json')
    assert os.path.exists(filepath)
    
    # Verify content
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    assert len(lines) == 3


def test_create_single_file_different_prefixes(tmp_path):
    """Test creating files with different prefix types"""
    data = [{'id': 1}]
    
    # Count prefix
    params_count = {
        'path': str(tmp_path),
        'file_name': 'data',
        'prefix_type': 'count',
        'index': 5,
        'data': data
    }
    filepath_count = create_single_file(params_count)
    assert '5_data.json' in filepath_count
    assert os.path.exists(filepath_count)
    
    # Random prefix
    params_random = {
        'path': str(tmp_path),
        'file_name': 'data',
        'prefix_type': 'random',
        'index': 0,
        'data': data
    }
    filepath_random = create_single_file(params_random)
    assert '_data.json' in filepath_random
    assert os.path.exists(filepath_random)
    
    # UUID prefix
    params_uuid = {
        'path': str(tmp_path),
        'file_name': 'data',
        'prefix_type': 'uuid',
        'index': 0,
        'data': data
    }
    filepath_uuid = create_single_file(params_uuid)
    assert '_data.json' in filepath_uuid
    assert '-' in filepath_uuid  # UUID has dashes
    assert os.path.exists(filepath_uuid)


# ================ create_multiple_files tests ================

def test_create_multiple_files_basic(tmp_path, test_generator):
    """Test creating multiple files"""
    files = create_multiple_files(
        path=str(tmp_path),
        file_name='data',
        prefix_type='count',
        files_count=3,
        data_lines_per_file=5,
        generator=test_generator
    )
    
    assert len(files) == 3
    
    # Check files exist
    for i, filepath in enumerate(files, 1):
        assert os.path.exists(filepath)
        assert f'{i}_data.json' in filepath
        
        # Check each file has 5 lines
        with open(filepath, 'r') as f:
            lines = f.readlines()
        assert len(lines) == 5


def test_create_multiple_files_different_counts(tmp_path, test_generator):
    """Test creating different number of files"""
    # Single file
    set1_path = tmp_path / 'set1'
    os.makedirs(str(set1_path), exist_ok=True)
    files_1 = create_multiple_files(
        str(set1_path), 'data', 'count', 1, 10, test_generator
    )
    assert len(files_1) == 1
    
    # Multiple files
    set2_path = tmp_path / 'set2'
    os.makedirs(str(set2_path), exist_ok=True)
    files_10 = create_multiple_files(
        str(set2_path), 'data', 'count', 10, 5, test_generator
    )
    assert len(files_10) == 10


def test_create_multiple_files_random_prefix(tmp_path, test_generator):
    """Test creating files with random prefix"""
    files = create_multiple_files(
        str(tmp_path), 'data', 'random', 5, 3, test_generator
    )
    
    assert len(files) == 5
    
    # All files should exist
    for filepath in files:
        assert os.path.exists(filepath)
    
    # File names should be unique
    basenames = [os.path.basename(f) for f in files]
    assert len(set(basenames)) == 5


def test_create_multiple_files_uuid_prefix(tmp_path, test_generator):
    """Test creating files with UUID prefix"""
    files = create_multiple_files(
        str(tmp_path), 'test', 'uuid', 3, 10, test_generator
    )
    
    assert len(files) == 3
    
    # Check UUID format in filenames
    for filepath in files:
        basename = os.path.basename(filepath)
        assert '_test.json' in basename
        assert '-' in basename  # UUIDs have dashes


# ================ get_file_stats tests ================

def test_get_file_stats_existing(tmp_path, sample_data):
    """Test getting stats for existing file"""
    filepath = tmp_path / "data.json"
    write_jsonlines(str(filepath), sample_data)
    
    stats = get_file_stats(str(filepath))
    
    assert stats['exists'] is True
    assert stats['size_bytes'] > 0
    assert stats['lines'] == 3


def test_get_file_stats_nonexistent():
    """Test getting stats for non-existent file"""
    stats = get_file_stats('/nonexistent/file.json')
    
    assert stats['exists'] is False
    assert stats['size_bytes'] == 0
    assert stats['lines'] == 0


def test_get_file_stats_empty(tmp_path):
    """Test getting stats for empty file"""
    filepath = tmp_path / "empty.json"
    filepath.write_text('')
    
    stats = get_file_stats(str(filepath))
    
    assert stats['exists'] is True
    assert stats['size_bytes'] == 0
    assert stats['lines'] == 0


# ================ Integration tests ================

def test_full_workflow_with_clearing(tmp_path, test_generator):
    """Test full workflow: create files, clear, create again"""
    path = str(tmp_path)
    
    # Create initial files
    files1 = create_multiple_files(path, 'data', 'count', 3, 5, test_generator)
    assert len(files1) == 3
    assert all(os.path.exists(f) for f in files1)
    
    # Clear directory
    removed = clear_directory(path, '*.json')
    assert removed == 3
    assert all(not os.path.exists(f) for f in files1)
    
    # Create new files
    files2 = create_multiple_files(path, 'data', 'count', 2, 10, test_generator)
    assert len(files2) == 2
    assert all(os.path.exists(f) for f in files2)


def test_multiple_file_sets_in_same_directory(tmp_path, test_generator):
    """Test creating multiple sets of files in same directory"""
    path = str(tmp_path)
    
    # Create first set
    files1 = create_multiple_files(path, 'set1', 'count', 2, 5, test_generator)
    
    # Create second set with different name
    files2 = create_multiple_files(path, 'set2', 'count', 2, 5, test_generator)
    
    # Both sets should exist
    assert len(files1) == 2
    assert len(files2) == 2
    
    # Check files
    json_files = glob.glob(os.path.join(path, '*.json'))
    assert len(json_files) == 4
    
    # Should have both set1 and set2 files
    set1_files = [f for f in json_files if 'set1' in f]
    set2_files = [f for f in json_files if 'set2' in f]
    assert len(set1_files) == 2
    assert len(set2_files) == 2

