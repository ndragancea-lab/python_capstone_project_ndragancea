"""
Special Additional Tests
Unique tests demonstrating advanced features and edge cases.
"""

import pytest
import os
import json
import time
from dataforge.data_generator import create_generator
from dataforge.schema_parser import parse_schema
from dataforge.file_manager import create_multiple_files
from dataforge.multiprocessor import generate_files_parallel


# ================ Special Test 1: Performance Benchmark ================

def test_performance_single_vs_parallel(tmp_path):
    """
    Special test: Compare single-process vs multi-process performance.
    
    This test demonstrates the performance benefit of multiprocessing
    by measuring time to generate the same amount of data.
    """
    schema = {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None},
        'timestamp': {'type': 'timestamp', 'strategy': 'rand', 'value': None},
        'name': {'type': 'str', 'strategy': 'rand', 'value': None},
        'value': {'type': 'int', 'strategy': 'range', 'value': (0, 1000)}
    }
    
    generator = create_generator(schema)
    files_count = 10
    lines_per_file = 100
    
    # Single process
    single_dir = tmp_path / 'single'
    single_dir.mkdir()
    
    start_single = time.time()
    single_files = create_multiple_files(
        str(single_dir), 'data', 'count', files_count, lines_per_file, generator
    )
    time_single = time.time() - start_single
    
    # Multi process
    multi_dir = tmp_path / 'multi'
    multi_dir.mkdir()
    
    params = {
        'path': str(multi_dir),
        'file_name': 'data',
        'prefix_type': 'count',
        'files_count': files_count,
        'data_lines': lines_per_file,
        'multiprocessing': 4,
        'parsed_schema': schema
    }
    
    start_multi = time.time()
    multi_files = generate_files_parallel(params)
    time_multi = time.time() - start_multi
    
    # Verify both created same number of files
    assert len(single_files) == files_count
    assert len(multi_files) == files_count
    
    # Log performance (for information)
    print(f"\nPerformance comparison:")
    print(f"Single process: {time_single:.3f}s")
    print(f"Multi process (4 cores): {time_multi:.3f}s")
    print(f"Speedup: {time_single/time_multi:.2f}x")


# ================ Special Test 2: Data Consistency ================

def test_data_consistency_across_runs(tmp_path):
    """
    Special test: Verify data consistency across multiple runs.
    
    Tests that running the same operation multiple times produces
    valid data each time, even with random generation.
    """
    schema_str = '{"id":"int:rand","status":"str:[active,inactive]","count":"int:100"}'
    schema = json.loads(schema_str)
    parsed_schema = parse_schema(schema)
    generator = create_generator(parsed_schema)
    
    # Generate data 3 times
    for run in range(3):
        run_dir = tmp_path / f'run_{run}'
        run_dir.mkdir()
        
        files = create_multiple_files(
            str(run_dir), 'test', 'count', 5, 20, generator
        )
        
        # Verify each run
        assert len(files) == 5
        
        for filepath in files:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            assert len(lines) == 20
            
            # Verify data structure in each line
            for line in lines:
                data = json.loads(line.strip())
                assert 'id' in data
                assert 'status' in data
                assert 'count' in data
                
                # Verify types and constraints
                assert isinstance(data['id'], int)
                assert data['status'] in ['active', 'inactive']
                assert data['count'] == 100  # Static value should always be 100


# ================ Special Test 3: Complex Mixed Schema ================

def test_complex_mixed_schema_generation(tmp_path):
    """
    Special test: Generate data with a complex schema mixing all strategies.
    
    This test uses all available types and strategies in one schema
    to verify they work together correctly.
    """
    complex_schema = {
        # Timestamp
        'created_at': {'type': 'timestamp', 'strategy': 'rand', 'value': None},
        'updated_at': {'type': 'timestamp', 'strategy': 'rand', 'value': None},
        
        # Integers with different strategies
        'id': {'type': 'int', 'strategy': 'rand', 'value': None},
        'age': {'type': 'int', 'strategy': 'range', 'value': (18, 65)},
        'priority': {'type': 'int', 'strategy': 'list', 'value': [1, 2, 3, 4, 5]},
        'version': {'type': 'int', 'strategy': 'static', 'value': 1},
        
        # Strings with different strategies
        'username': {'type': 'str', 'strategy': 'rand', 'value': None},
        'status': {'type': 'str', 'strategy': 'list', 'value': ['active', 'inactive', 'pending', 'deleted']},
        'email': {'type': 'str', 'strategy': 'static', 'value': 'test@example.com'},
        'notes': {'type': 'str', 'strategy': 'empty', 'value': ''}
    }
    
    generator = create_generator(complex_schema)
    
    # Generate files
    files = create_multiple_files(
        str(tmp_path), 'complex', 'count', 3, 50, generator
    )
    
    assert len(files) == 3
    
    # Verify complex schema data
    for filepath in files:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 50
        
        for line in lines:
            data = json.loads(line.strip())
            
            # Check all 10 fields exist
            assert len(data) == 10
            
            # Verify timestamps
            assert isinstance(data['created_at'], float)
            assert isinstance(data['updated_at'], float)
            assert data['created_at'] > 0
            assert data['updated_at'] > 0
            
            # Verify integers
            assert isinstance(data['id'], int)
            assert isinstance(data['age'], int)
            assert 18 <= data['age'] <= 65
            assert data['priority'] in [1, 2, 3, 4, 5]
            assert data['version'] == 1
            
            # Verify strings
            assert isinstance(data['username'], str)
            assert len(data['username']) == 8  # UUID-based
            assert data['status'] in ['active', 'inactive', 'pending', 'deleted']
            assert data['email'] == 'test@example.com'
            assert data['notes'] == ''


# ================ Special Test 4: Stress Test ================

def test_stress_large_files(tmp_path):
    """
    Special test: Stress test with large files.
    
    Generates large files to test memory efficiency and stability.
    """
    schema = {
        'id': {'type': 'int', 'strategy': 'rand', 'value': None},
        'data': {'type': 'str', 'strategy': 'rand', 'value': None}
    }
    
    generator = create_generator(schema)
    
    # Generate fewer files but with many lines
    files = create_multiple_files(
        str(tmp_path), 'large', 'count', 2, 1000, generator
    )
    
    assert len(files) == 2
    
    # Verify large files
    for filepath in files:
        # Check file exists and has content
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0
        
        # Count lines
        with open(filepath, 'r') as f:
            line_count = sum(1 for _ in f)
        
        assert line_count == 1000
        
        # Sample verification (first and last lines)
        with open(filepath, 'r') as f:
            first_line = f.readline()
            f.seek(0, 2)  # Go to end
            f.seek(f.tell() - 100, 0)  # Go back 100 bytes
            f.readline()  # Skip partial line
            last_line = f.readline()
        
        # Verify JSON validity
        data_first = json.loads(first_line.strip())
        data_last = json.loads(last_line.strip())
        
        assert 'id' in data_first and 'data' in data_first
        assert 'id' in data_last and 'data' in data_last


# ================ Special Test 5: Edge Cases ================

def test_edge_cases_single_line_single_file(tmp_path):
    """
    Special test: Edge case - single line in single file.
    
    Tests the minimal valid configuration.
    """
    schema = {'value': {'type': 'int', 'strategy': 'static', 'value': 42}}
    generator = create_generator(schema)
    
    files = create_multiple_files(
        str(tmp_path), 'minimal', 'count', 1, 1, generator
    )
    
    assert len(files) == 1
    
    with open(files[0], 'r') as f:
        content = f.read().strip()
    
    data = json.loads(content)
    assert data == {'value': 42}


def test_edge_cases_many_files_few_lines(tmp_path):
    """
    Special test: Edge case - many files with few lines each.
    
    Tests creating many small files.
    """
    schema = {'id': {'type': 'int', 'strategy': 'rand', 'value': None}}
    generator = create_generator(schema)
    
    # 50 files with only 2 lines each
    files = create_multiple_files(
        str(tmp_path), 'small', 'random', 50, 2, generator
    )
    
    assert len(files) == 50
    
    # Verify all files
    for filepath in files:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        assert len(lines) == 2


# ================ Special Test 6: Unique Prefix Verification ================

def test_unique_prefixes_verification(tmp_path):
    """
    Special test: Verify uniqueness of random and UUID prefixes.
    
    Ensures that random and UUID prefixes generate unique names.
    """
    schema = {'id': {'type': 'int', 'strategy': 'rand', 'value': None}}
    generator = create_generator(schema)
    
    # Test random prefixes
    random_dir = tmp_path / 'random'
    random_dir.mkdir()
    random_files = create_multiple_files(
        str(random_dir), 'test', 'random', 100, 5, generator
    )
    
    # Extract prefixes
    random_prefixes = [os.path.basename(f).split('_')[0] for f in random_files]
    
    # All should be unique
    assert len(set(random_prefixes)) == 100
    
    # Test UUID prefixes
    uuid_dir = tmp_path / 'uuid'
    uuid_dir.mkdir()
    uuid_files = create_multiple_files(
        str(uuid_dir), 'test', 'uuid', 50, 5, generator
    )
    
    # Extract prefixes
    uuid_prefixes = [os.path.basename(f).split('_test.json')[0] for f in uuid_files]
    
    # All should be unique and contain dashes (UUID format)
    assert len(set(uuid_prefixes)) == 50
    assert all('-' in prefix for prefix in uuid_prefixes)


# ================ Special Test 7: Data Distribution ================

def test_data_distribution_randomness(tmp_path):
    """
    Special test: Verify random data has good distribution.
    
    Tests that random integers are well-distributed across the range.
    """
    schema = {
        'value': {'type': 'int', 'strategy': 'range', 'value': (0, 9)}
    }
    generator = create_generator(schema)
    
    # Generate one file with many lines
    files = create_multiple_files(
        str(tmp_path), 'dist', 'count', 1, 1000, generator
    )
    
    # Collect all values
    values = []
    with open(files[0], 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            values.append(data['value'])
    
    # Check distribution
    # Each digit (0-9) should appear at least once in 1000 samples
    unique_values = set(values)
    assert len(unique_values) == 10  # All 10 digits should appear
    
    # No value should dominate (> 30% of samples)
    from collections import Counter
    counts = Counter(values)
    for count in counts.values():
        assert count < 300  # Less than 30%

