"""
End-to-End Integration Tests
Tests the complete workflow of the DataForge utility.
"""

import pytest
import os
import json
import subprocess
import glob


# ================ Fixtures ================

@pytest.fixture
def test_schema_simple():
    """Simple schema for testing"""
    return {
        "id": "int:rand",
        "name": "str:rand"
    }


@pytest.fixture
def test_schema_complex():
    """Complex schema with all field types"""
    return {
        "id": "int:rand",
        "timestamp": "timestamp:",
        "username": "str:rand",
        "age": "int:rand(18,65)",
        "status": "str:[active,inactive,pending]",
        "priority": "int:[1,2,3,4,5]",
        "email": "str:test@example.com",
        "count": "int:100",
        "description": "str:"
    }


@pytest.fixture
def schema_file(tmp_path, test_schema_simple):
    """Create a temporary schema file"""
    schema_path = tmp_path / "schema.json"
    with open(schema_path, 'w') as f:
        json.dump(test_schema_simple, f)
    return str(schema_path)


# ================ Console Mode Tests ================

def test_console_mode_basic(capsys):
    """Test basic console output mode"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', '.',
            '--files_count=0',
            '--data_lines=3',
            '--data_schema={"id":"int:rand","name":"str:rand"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    # Check that JSON data was output
    lines = [line for line in result.stdout.split('\n') if line.strip() and line.startswith('{')]
    assert len(lines) == 3
    
    # Verify each line is valid JSON
    for line in lines:
        data = json.loads(line)
        assert 'id' in data
        assert 'name' in data


def test_console_mode_different_schema(capsys):
    """Test console mode with different schema"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', '.',
            '--files_count=0',
            '--data_lines=2',
            '--data_schema={"timestamp":"timestamp:","status":"str:[active,inactive]"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    lines = [line for line in result.stdout.split('\n') if line.strip() and line.startswith('{')]
    assert len(lines) == 2
    
    for line in lines:
        data = json.loads(line)
        assert 'timestamp' in data
        assert 'status' in data
        assert data['status'] in ['active', 'inactive']


# ================ File Mode Tests ================

def test_file_mode_single_file(tmp_path):
    """Test creating a single file"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=1',
            '--file_name=test',
            '--data_lines=10',
            '--file_prefix=count',
            '--data_schema={"id":"int:rand"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    # Check file was created
    files = list(tmp_path.glob('*_test.json'))
    assert len(files) == 1
    
    # Check file content
    with open(files[0], 'r') as f:
        lines = f.readlines()
    assert len(lines) == 10
    
    # Verify JSON validity
    for line in lines:
        data = json.loads(line.strip())
        assert 'id' in data


def test_file_mode_multiple_files(tmp_path):
    """Test creating multiple files"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=5',
            '--file_name=data',
            '--data_lines=20',
            '--file_prefix=count',
            '--data_schema={"id":"int:rand","name":"str:rand"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    # Check files were created
    files = sorted(tmp_path.glob('*_data.json'))
    assert len(files) == 5
    
    # Check each file
    for i, filepath in enumerate(files, 1):
        # Check filename
        assert f'{i}_data.json' in str(filepath)
        
        # Check content
        with open(filepath, 'r') as f:
            lines = f.readlines()
        assert len(lines) == 20


def test_file_mode_random_prefix(tmp_path):
    """Test file generation with random prefix"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=3',
            '--file_name=random',
            '--data_lines=5',
            '--file_prefix=random',
            '--data_schema={"id":"int:rand"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    files = list(tmp_path.glob('*_random.json'))
    assert len(files) == 3
    
    # Check that prefixes are different
    prefixes = [f.name.split('_')[0] for f in files]
    assert len(set(prefixes)) == 3  # All unique


def test_file_mode_uuid_prefix(tmp_path):
    """Test file generation with UUID prefix"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=2',
            '--file_name=uuid',
            '--data_lines=10',
            '--file_prefix=uuid',
            '--data_schema={"id":"int:rand"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    files = list(tmp_path.glob('*_uuid.json'))
    assert len(files) == 2
    
    # Check UUID format (contains dashes)
    for f in files:
        assert '-' in f.name


# ================ Clear Path Tests ================

def test_clear_path_functionality(tmp_path):
    """Test clear_path removes existing files"""
    # Create some existing files
    for i in range(3):
        filepath = tmp_path / f'{i}_old.json'
        filepath.write_text('{"old": true}')
    
    # Generate new files with clear_path
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=2',
            '--file_name=new',
            '--data_lines=5',
            '--file_prefix=count',
            '--clear_path',
            '--data_schema={"id":"int:rand"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    # Old files should be gone
    old_files = list(tmp_path.glob('*_old.json'))
    assert len(old_files) == 0
    
    # New files should exist
    new_files = list(tmp_path.glob('*_new.json'))
    assert len(new_files) == 2


# ================ Multiprocessing Tests ================

def test_multiprocessing_mode(tmp_path):
    """Test parallel file generation"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=10',
            '--file_name=parallel',
            '--data_lines=50',
            '--file_prefix=count',
            '--multiprocessing=4',
            '--data_schema={"id":"int:rand","name":"str:rand"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    # Check all files were created
    files = list(tmp_path.glob('*_parallel.json'))
    assert len(files) == 10
    
    # Check each file has correct number of lines
    for filepath in files:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        assert len(lines) == 50


def test_multiprocessing_sequential_indices(tmp_path):
    """Test that multiprocessing creates files with sequential indices"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=8',
            '--file_name=test',
            '--data_lines=10',
            '--file_prefix=count',
            '--multiprocessing=3',
            '--data_schema={"id":"int:rand"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    files = list(tmp_path.glob('*_test.json'))
    assert len(files) == 8
    
    # Extract indices
    indices = [int(f.name.split('_')[0]) for f in files]
    indices.sort()
    
    # Should be 1 through 8
    assert indices == list(range(1, 9))


# ================ Schema Tests ================

def test_schema_from_file(tmp_path, schema_file):
    """Test loading schema from file"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=1',
            '--file_name=fromfile',
            '--data_lines=5',
            '--file_prefix=count',
            f'--data_schema={schema_file}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    files = list(tmp_path.glob('*_fromfile.json'))
    assert len(files) == 1
    
    # Verify content matches schema
    with open(files[0], 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            assert 'id' in data
            assert 'name' in data


def test_complex_schema(tmp_path, test_schema_complex):
    """Test with complex schema containing all field types"""
    schema_str = json.dumps(test_schema_complex)
    
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=2',
            '--file_name=complex',
            '--data_lines=10',
            '--file_prefix=count',
            f'--data_schema={schema_str}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    
    files = list(tmp_path.glob('*_complex.json'))
    assert len(files) == 2
    
    # Verify all fields are present and correct types
    with open(files[0], 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            
            # Check all fields exist
            assert 'id' in data
            assert 'timestamp' in data
            assert 'username' in data
            assert 'age' in data
            assert 'status' in data
            assert 'priority' in data
            assert 'email' in data
            assert 'count' in data
            assert 'description' in data
            
            # Check types and ranges
            assert isinstance(data['id'], int)
            assert isinstance(data['timestamp'], float)
            assert isinstance(data['username'], str)
            assert 18 <= data['age'] <= 65
            assert data['status'] in ['active', 'inactive', 'pending']
            assert data['priority'] in [1, 2, 3, 4, 5]
            assert data['email'] == 'test@example.com'
            assert data['count'] == 100
            assert data['description'] == ''


# ================ Error Handling Tests ================

def test_invalid_files_count():
    """Test that invalid files_count is rejected"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', '.',
            '--files_count=-5',
            '--data_schema={"id":"int:rand"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 1
    assert 'files_count must be >= 0' in result.stdout


def test_invalid_data_lines():
    """Test that invalid data_lines is rejected"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', '.',
            '--files_count=0',
            '--data_lines=0',
            '--data_schema={"id":"int:rand"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 1
    assert 'data_lines must be > 0' in result.stdout


def test_invalid_schema():
    """Test that invalid schema is rejected"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', '.',
            '--files_count=0',
            '--data_lines=1',
            '--data_schema=invalid json'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 1


# ================ Performance Tests ================

def test_large_batch_generation(tmp_path):
    """Test generating a large batch of files"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=20',
            '--file_name=batch',
            '--data_lines=100',
            '--file_prefix=count',
            '--multiprocessing=4',
            '--data_schema={"id":"int:rand","name":"str:rand","timestamp":"timestamp:"}'
        ],
        capture_output=True,
        text=True,
        timeout=30  # 30 second timeout
    )
    
    assert result.returncode == 0
    
    files = list(tmp_path.glob('*_batch.json'))
    assert len(files) == 20
    
    # Verify total lines
    total_lines = 0
    for filepath in files:
        with open(filepath, 'r') as f:
            total_lines += len(f.readlines())
    
    assert total_lines == 2000  # 20 files * 100 lines


# ================ Configuration Tests ================

def test_default_configuration():
    """Test that default configuration is loaded"""
    result = subprocess.run(
        [
            'python3', '-m', 'dataforge', '.',
            '--files_count=0',
            '--data_lines=1',
            '--data_schema={"id":"int:rand"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert 'Loading configuration from default.ini' in result.stdout


# ================ Full Workflow Test ================

def test_complete_workflow(tmp_path):
    """Test complete workflow from start to finish"""
    # Step 1: Create initial batch
    result1 = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=5',
            '--file_name=workflow',
            '--data_lines=20',
            '--file_prefix=count',
            '--data_schema={"id":"int:rand","name":"str:rand","status":"str:[active,inactive]"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result1.returncode == 0
    files1 = list(tmp_path.glob('*_workflow.json'))
    assert len(files1) == 5
    
    # Step 2: Clear and create new batch with multiprocessing
    result2 = subprocess.run(
        [
            'python3', '-m', 'dataforge', str(tmp_path),
            '--files_count=10',
            '--file_name=workflow',
            '--data_lines=50',
            '--file_prefix=random',
            '--multiprocessing=3',
            '--clear_path',
            '--data_schema={"id":"int:rand","timestamp":"timestamp:","value":"int:rand(1,100)"}'
        ],
        capture_output=True,
        text=True
    )
    
    assert result2.returncode == 0
    files2 = list(tmp_path.glob('*_workflow.json'))
    assert len(files2) == 10  # Old files cleared, new files created
    
    # Verify new files have correct structure
    for filepath in files2:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        assert len(lines) == 50
        
        # Check first line structure
        data = json.loads(lines[0].strip())
        assert 'id' in data
        assert 'timestamp' in data
        assert 'value' in data
        assert 1 <= data['value'] <= 100

