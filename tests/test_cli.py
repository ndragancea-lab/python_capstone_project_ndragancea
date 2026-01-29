"""
Tests for CLI module
"""

import pytest
import sys
from io import StringIO
from dataforge.cli import create_parser, parse_arguments, display_parameters
from dataforge.logger import setup_logger


def test_create_parser():
    """Test parser creation"""
    parser = create_parser()
    
    assert parser is not None
    assert parser.prog == 'dataforge'


def test_parse_arguments_minimal():
    """Test parsing with minimal arguments (only path)"""
    args = parse_arguments(['.'])
    
    assert args.path_to_save_files == '.'
    assert args.files_count is None
    assert args.file_name is None
    assert args.file_prefix is None
    assert args.data_schema is None
    assert args.data_lines is None
    assert args.clear_path is False
    assert args.multiprocessing is None


def test_parse_arguments_all_options():
    """Test parsing with all options"""
    args = parse_arguments([
        '/tmp/output',
        '--files_count', '5',
        '--file_name', 'test_data',
        '--file_prefix', 'count',
        '--data_schema', '{"id": "int:rand"}',
        '--data_lines', '100',
        '--clear_path',
        '--multiprocessing', '4'
    ])
    
    assert args.path_to_save_files == '/tmp/output'
    assert args.files_count == 5
    assert args.file_name == 'test_data'
    assert args.file_prefix == 'count'
    assert args.data_schema == '{"id": "int:rand"}'
    assert args.data_lines == 100
    assert args.clear_path is True
    assert args.multiprocessing == 4


def test_parse_arguments_file_prefix_choices():
    """Test that file_prefix only accepts valid choices"""
    # Valid choices should work
    for choice in ['count', 'random', 'uuid']:
        args = parse_arguments(['.', '--file_prefix', choice])
        assert args.file_prefix == choice
    
    # Invalid choice should raise SystemExit
    with pytest.raises(SystemExit):
        parse_arguments(['.', '--file_prefix', 'invalid'])


def test_parse_arguments_clear_path_flag():
    """Test clear_path flag behavior"""
    # Without flag - should be False
    args = parse_arguments(['.'])
    assert args.clear_path is False
    
    # With flag - should be True
    args = parse_arguments(['.', '--clear_path'])
    assert args.clear_path is True


def test_parse_arguments_integer_types():
    """Test that integer arguments are parsed as integers"""
    args = parse_arguments([
        '.',
        '--files_count', '10',
        '--data_lines', '500',
        '--multiprocessing', '2'
    ])
    
    assert isinstance(args.files_count, int)
    assert isinstance(args.data_lines, int)
    assert isinstance(args.multiprocessing, int)
    assert args.files_count == 10
    assert args.data_lines == 500
    assert args.multiprocessing == 2


def test_parse_arguments_invalid_integer():
    """Test parsing with invalid integer value"""
    with pytest.raises(SystemExit):
        parse_arguments(['.', '--files_count', 'not_a_number'])


def test_parse_arguments_missing_path():
    """Test that path argument is required"""
    with pytest.raises(SystemExit):
        parse_arguments([])


def test_display_parameters(capsys):
    """Test display_parameters function"""
    logger = setup_logger('test_display')
    
    params = {
        'path_to_save_files': '/tmp/output',
        'files_count': 5,
        'file_name': 'test_data',
        'file_prefix': 'count',
        'data_lines': 100,
        'multiprocessing': 2,
        'clear_path': True,
        'data_schema': '{"id": "int:rand"}'
    }
    
    display_parameters(logger, params)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Check that all parameters are displayed
    assert 'Path to save files: /tmp/output' in output
    assert 'Files count: 5' in output
    assert 'File name: test_data' in output
    assert 'File prefix: count' in output
    assert 'Data lines per file: 100' in output
    assert 'Multiprocessing: 2 process(es)' in output
    assert 'Clear path: True' in output
    assert 'Data schema:' in output


def test_display_parameters_long_schema(capsys):
    """Test display_parameters with very long schema"""
    logger = setup_logger('test_display_long')
    
    # Create a very long schema string
    long_schema = '{"field": "str:rand"}' * 20
    
    params = {
        'path_to_save_files': '.',
        'files_count': 1,
        'file_name': 'data',
        'file_prefix': 'count',
        'data_lines': 100,
        'multiprocessing': 1,
        'clear_path': False,
        'data_schema': long_schema
    }
    
    display_parameters(logger, params)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should truncate long schema with "..."
    assert 'Data schema:' in output
    if len(long_schema) > 100:
        assert '...' in output


def test_parse_arguments_with_equals_sign():
    """Test parsing arguments with equals sign format"""
    args = parse_arguments([
        '.',
        '--files_count=10',
        '--file_name=my_data',
        '--data_lines=500'
    ])
    
    assert args.files_count == 10
    assert args.file_name == 'my_data'
    assert args.data_lines == 500


def test_parse_arguments_mixed_formats():
    """Test mixing space and equals sign formats"""
    args = parse_arguments([
        './output',
        '--files_count=5',
        '--file_name', 'test',
        '--data_lines=100'
    ])
    
    assert args.path_to_save_files == './output'
    assert args.files_count == 5
    assert args.file_name == 'test'
    assert args.data_lines == 100


def test_parser_help_contains_examples():
    """Test that parser help contains usage examples"""
    parser = create_parser()
    help_text = parser.format_help()
    
    assert 'Examples:' in help_text
    assert 'dataforge' in help_text
    assert '--files_count' in help_text


def test_parse_arguments_zero_files_count():
    """Test parsing with files_count=0 (console output mode)"""
    args = parse_arguments(['.', '--files_count', '0'])
    
    assert args.files_count == 0
    # This should be valid for console output mode


def test_parse_arguments_negative_files_count():
    """Test that negative files_count is parsed (validation happens later)"""
    # Parser doesn't validate, just parses
    args = parse_arguments(['.', '--files_count', '-1'])
    
    assert args.files_count == -1
    # Validation will happen in validator module


def test_parse_arguments_relative_path():
    """Test parsing with relative path"""
    args = parse_arguments(['./output'])
    assert args.path_to_save_files == './output'
    
    args = parse_arguments(['../data'])
    assert args.path_to_save_files == '../data'


def test_parse_arguments_absolute_path():
    """Test parsing with absolute path"""
    args = parse_arguments(['/tmp/data'])
    assert args.path_to_save_files == '/tmp/data'
    
    args = parse_arguments(['/home/user/output'])
    assert args.path_to_save_files == '/home/user/output'


def test_parse_arguments_current_directory():
    """Test parsing with current directory"""
    args = parse_arguments(['.'])
    assert args.path_to_save_files == '.'

