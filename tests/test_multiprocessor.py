"""
Tests for multiprocessor module
"""

import pytest
import os
import json
from dataforge.multiprocessor import (
    distribute_work,
    worker_function,
    generate_files_parallel,
    should_use_multiprocessing
)
from dataforge.data_generator import create_generator


# ================ Fixtures ================

@pytest.fixture
def simple_schema():
    """Simple schema for testing"""
    return {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None},
        'name': {'type': 'str', 'strategy': 'rand', 'value': None}
    }


@pytest.fixture
def test_generator(simple_schema):
    """Create a simple generator for testing"""
    return create_generator(simple_schema)


# ================ distribute_work tests ================

@pytest.mark.parametrize("total_files,num_processes,expected", [
    (10, 3, [4, 3, 3]),        # 10 files, 3 processes: 4+3+3
    (7, 2, [4, 3]),            # 7 files, 2 processes: 4+3
    (5, 5, [1, 1, 1, 1, 1]),   # 5 files, 5 processes: 1 each
    (12, 4, [3, 3, 3, 3]),     # 12 files, 4 processes: 3 each
    (10, 1, [10]),             # 10 files, 1 process: all
    (1, 1, [1]),               # 1 file, 1 process
    (15, 4, [4, 4, 4, 3]),     # 15 files, 4 processes: 4+4+4+3
])
def test_distribute_work(total_files, num_processes, expected):
    """Test work distribution across processes"""
    distribution = distribute_work(total_files, num_processes)
    
    assert distribution == expected
    assert sum(distribution) == total_files
    assert len(distribution) == num_processes


def test_distribute_work_sum_equals_total():
    """Test that distribution sums to total files"""
    total_files = 100
    num_processes = 7
    
    distribution = distribute_work(total_files, num_processes)
    
    assert sum(distribution) == total_files
    assert len(distribution) == num_processes


def test_distribute_work_balanced():
    """Test that distribution is balanced (difference <= 1)"""
    distribution = distribute_work(20, 7)
    
    # Maximum difference should be 1
    max_val = max(distribution)
    min_val = min(distribution)
    assert max_val - min_val <= 1


# ================ worker_function tests ================

def test_worker_function_basic(tmp_path, simple_schema):
    """Test basic worker function execution"""
    args = (
        1,  # process_id
        2,  # files_to_create
        {
            'path': str(tmp_path),
            'file_name': 'test',
            'prefix_type': 'count',
            'data_lines': 5,
            'parsed_schema': simple_schema,
            'start_index': 1
        }
    )
    
    files = worker_function(args)
    
    assert len(files) == 2
    assert all(os.path.exists(f) for f in files)
    
    # Check file names
    assert '1_test.json' in files[0]
    assert '2_test.json' in files[1]


def test_worker_function_correct_data_lines(tmp_path, simple_schema):
    """Test that worker creates files with correct number of lines"""
    args = (
        1,
        1,
        {
            'path': str(tmp_path),
            'file_name': 'data',
            'prefix_type': 'count',
            'data_lines': 10,
            'parsed_schema': simple_schema,
            'start_index': 1
        }
    )
    
    files = worker_function(args)
    
    # Check line count
    with open(files[0], 'r') as f:
        lines = f.readlines()
    
    assert len(lines) == 10


def test_worker_function_start_index(tmp_path, simple_schema):
    """Test that worker respects start_index"""
    args = (
        2,  # process_id
        2,  # files_to_create
        {
            'path': str(tmp_path),
            'file_name': 'test',
            'prefix_type': 'count',
            'data_lines': 5,
            'parsed_schema': simple_schema,
            'start_index': 10  # Start from index 10
        }
    )
    
    files = worker_function(args)
    
    # Should create files with indices 10 and 11
    assert '10_test.json' in files[0]
    assert '11_test.json' in files[1]


def test_worker_function_valid_json(tmp_path, simple_schema):
    """Test that worker creates valid JSON data"""
    args = (
        1,
        1,
        {
            'path': str(tmp_path),
            'file_name': 'data',
            'prefix_type': 'count',
            'data_lines': 3,
            'parsed_schema': simple_schema,
            'start_index': 1
        }
    )
    
    files = worker_function(args)
    
    # Read and validate JSON
    with open(files[0], 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            assert 'id' in data
            assert 'name' in data
            assert isinstance(data['id'], int)
            assert isinstance(data['name'], str)


# ================ generate_files_parallel tests ================

def test_generate_files_parallel_basic(tmp_path, simple_schema):
    """Test basic parallel file generation"""
    params = {
        'path': str(tmp_path),
        'file_name': 'data',
        'prefix_type': 'count',
        'files_count': 6,
        'data_lines': 10,
        'multiprocessing': 2,
        'parsed_schema': simple_schema
    }
    
    files = generate_files_parallel(params)
    
    assert len(files) == 6
    assert all(os.path.exists(f) for f in files)


def test_generate_files_parallel_correct_count(tmp_path, simple_schema):
    """Test that parallel generation creates correct number of files"""
    params = {
        'path': str(tmp_path),
        'file_name': 'test',
        'prefix_type': 'count',
        'files_count': 10,
        'data_lines': 5,
        'multiprocessing': 4,
        'parsed_schema': simple_schema
    }
    
    files = generate_files_parallel(params)
    
    assert len(files) == 10


def test_generate_files_parallel_single_process(tmp_path, simple_schema):
    """Test parallel generation with single process"""
    params = {
        'path': str(tmp_path),
        'file_name': 'data',
        'prefix_type': 'count',
        'files_count': 5,
        'data_lines': 10,
        'multiprocessing': 1,
        'parsed_schema': simple_schema
    }
    
    files = generate_files_parallel(params)
    
    assert len(files) == 5


def test_generate_files_parallel_many_processes(tmp_path, simple_schema):
    """Test parallel generation with more processes than files"""
    params = {
        'path': str(tmp_path),
        'file_name': 'data',
        'prefix_type': 'count',
        'files_count': 3,
        'data_lines': 5,
        'multiprocessing': 5,  # More processes than files
        'parsed_schema': simple_schema
    }
    
    files = generate_files_parallel(params)
    
    assert len(files) == 3


def test_generate_files_parallel_data_correctness(tmp_path, simple_schema):
    """Test that parallel generation produces correct data"""
    params = {
        'path': str(tmp_path),
        'file_name': 'test',
        'prefix_type': 'count',
        'files_count': 4,
        'data_lines': 10,
        'multiprocessing': 2,
        'parsed_schema': simple_schema
    }
    
    files = generate_files_parallel(params)
    
    # Check each file
    for filepath in files:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Each file should have 10 lines
        assert len(lines) == 10
        
        # Each line should be valid JSON
        for line in lines:
            data = json.loads(line.strip())
            assert 'id' in data
            assert 'name' in data


def test_generate_files_parallel_file_indices(tmp_path, simple_schema):
    """Test that file indices are sequential"""
    params = {
        'path': str(tmp_path),
        'file_name': 'data',
        'prefix_type': 'count',
        'files_count': 10,
        'data_lines': 5,
        'multiprocessing': 3,
        'parsed_schema': simple_schema
    }
    
    files = generate_files_parallel(params)
    
    # Extract indices from filenames
    indices = []
    for filepath in files:
        filename = os.path.basename(filepath)
        index = int(filename.split('_')[0])
        indices.append(index)
    
    # Indices should be 1 to 10
    indices.sort()
    assert indices == list(range(1, 11))


def test_generate_files_parallel_random_prefix(tmp_path, simple_schema):
    """Test parallel generation with random prefix"""
    params = {
        'path': str(tmp_path),
        'file_name': 'data',
        'prefix_type': 'random',
        'files_count': 5,
        'data_lines': 10,
        'multiprocessing': 2,
        'parsed_schema': simple_schema
    }
    
    files = generate_files_parallel(params)
    
    assert len(files) == 5
    
    # All file names should be unique
    basenames = [os.path.basename(f) for f in files]
    assert len(set(basenames)) == 5


def test_generate_files_parallel_uuid_prefix(tmp_path, simple_schema):
    """Test parallel generation with UUID prefix"""
    params = {
        'path': str(tmp_path),
        'file_name': 'test',
        'prefix_type': 'uuid',
        'files_count': 3,
        'data_lines': 5,
        'multiprocessing': 2,
        'parsed_schema': simple_schema
    }
    
    files = generate_files_parallel(params)
    
    assert len(files) == 3
    
    # Check UUID format in filenames
    for filepath in files:
        basename = os.path.basename(filepath)
        assert '_test.json' in basename
        assert '-' in basename  # UUIDs have dashes


# ================ should_use_multiprocessing tests ================

@pytest.mark.parametrize("files_count,multiprocessing,expected", [
    (10, 4, True),    # Multiple files, multiple processes
    (1, 4, False),    # Single file
    (10, 1, False),   # Single process
    (1, 1, False),    # Single file, single process
    (100, 8, True),   # Many files, many processes
    (2, 2, True),     # Minimum for multiprocessing
])
def test_should_use_multiprocessing(files_count, multiprocessing, expected):
    """Test decision to use multiprocessing"""
    result = should_use_multiprocessing(files_count, multiprocessing)
    assert result == expected


# ================ Integration tests ================

def test_full_multiprocessing_workflow(tmp_path, simple_schema):
    """Test complete multiprocessing workflow"""
    # Test parameters
    total_files = 20
    num_processes = 4
    data_lines = 15
    
    params = {
        'path': str(tmp_path),
        'file_name': 'workflow_test',
        'prefix_type': 'count',
        'files_count': total_files,
        'data_lines': data_lines,
        'multiprocessing': num_processes,
        'parsed_schema': simple_schema
    }
    
    # Generate files in parallel
    files = generate_files_parallel(params)
    
    # Verify count
    assert len(files) == total_files
    
    # Verify all files exist
    assert all(os.path.exists(f) for f in files)
    
    # Verify data in each file
    for filepath in files:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Check line count
        assert len(lines) == data_lines
        
        # Validate JSON
        for line in lines:
            data = json.loads(line.strip())
            assert 'id' in data
            assert 'name' in data
    
    # Verify file indices are sequential
    indices = []
    for filepath in files:
        filename = os.path.basename(filepath)
        index = int(filename.split('_')[0])
        indices.append(index)
    
    indices.sort()
    assert indices == list(range(1, total_files + 1))

