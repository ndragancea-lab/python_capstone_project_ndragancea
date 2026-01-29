"""
Tests for config module
"""

import pytest
import configparser
from argparse import Namespace
from dataforge.config import (
    load_default_config,
    get_hardcoded_defaults,
    get_config_value,
    get_config_int,
    create_default_config,
    merge_config_with_args
)


def test_get_hardcoded_defaults():
    """Test hardcoded defaults creation"""
    config = get_hardcoded_defaults()
    
    assert config is not None
    assert isinstance(config, configparser.ConfigParser)
    
    # Check DEFAULT section values (DEFAULT is special, always exists)
    assert config.get('DEFAULT', 'files_count') == '10'
    assert config.get('DEFAULT', 'file_name') == 'generated_data'
    assert config.get('DEFAULT', 'file_prefix') == 'count'
    assert config.get('DEFAULT', 'data_lines') == '1000'
    assert config.get('DEFAULT', 'multiprocessing') == '1'
    
    # Check SCHEMA section
    assert config.has_section('SCHEMA')
    assert 'default_schema' in config['SCHEMA']


def test_load_default_config_file_exists():
    """Test loading config from existing default.ini"""
    # Should load the actual default.ini from project root
    config = load_default_config('default.ini')
    
    assert config is not None
    assert isinstance(config, configparser.ConfigParser)


def test_load_default_config_file_not_exists():
    """Test loading config when file doesn't exist"""
    config = load_default_config('nonexistent.ini')
    
    # Should return hardcoded defaults without crashing
    assert config is not None
    assert isinstance(config, configparser.ConfigParser)


def test_get_config_value():
    """Test getting config value with fallback"""
    config = get_hardcoded_defaults()
    
    # Existing value
    value = get_config_value(config, 'DEFAULT', 'file_name', 'fallback')
    assert value == 'generated_data'
    
    # Non-existing value - should return fallback
    value = get_config_value(config, 'DEFAULT', 'nonexistent', 'fallback')
    assert value == 'fallback'
    
    # Non-existing section - should return fallback
    value = get_config_value(config, 'NONEXISTENT', 'key', 'fallback')
    assert value == 'fallback'


def test_get_config_int():
    """Test getting integer config value"""
    config = get_hardcoded_defaults()
    
    # Existing integer value
    value = get_config_int(config, 'DEFAULT', 'files_count', 0)
    assert value == 10
    assert isinstance(value, int)
    
    # Non-existing value - should return fallback
    value = get_config_int(config, 'DEFAULT', 'nonexistent', 999)
    assert value == 999


def test_create_default_config(tmp_path):
    """Test creating default config file"""
    config_file = tmp_path / "test_default.ini"
    
    # Create config file
    result = create_default_config(str(config_file))
    
    assert result is True
    assert config_file.exists()
    
    # Load and verify content
    config = configparser.ConfigParser()
    config.read(str(config_file))
    
    # DEFAULT section always exists, check its values
    assert config.get('DEFAULT', 'files_count') == '10'


def test_create_default_config_already_exists(tmp_path):
    """Test creating config when file already exists"""
    config_file = tmp_path / "existing.ini"
    config_file.write_text("[DEFAULT]\ntest=value\n")
    
    # Should not overwrite
    result = create_default_config(str(config_file))
    
    assert result is False
    # Original content should be preserved
    assert "test=value" in config_file.read_text()


def test_merge_config_with_args_cli_overrides():
    """Test merging config with CLI args - CLI should override"""
    config = get_hardcoded_defaults()
    
    # Create args with some values set
    args = Namespace(
        path_to_save_files='./output',
        files_count=5,  # Override default (10)
        file_name='custom_name',  # Override default
        file_prefix=None,  # Use default
        data_schema=None,  # Use default
        data_lines=None,  # Use default
        multiprocessing=None,  # Use default
        clear_path=True
    )
    
    params = merge_config_with_args(config, args)
    
    # Check CLI overrides
    assert params['files_count'] == 5  # From CLI
    assert params['file_name'] == 'custom_name'  # From CLI
    
    # Check config defaults
    assert params['file_prefix'] == 'count'  # From config
    assert params['data_lines'] == 1000  # From config
    assert params['multiprocessing'] == 1  # From config
    
    # Check flags
    assert params['clear_path'] is True
    assert params['path_to_save_files'] == './output'


def test_merge_config_with_args_all_defaults():
    """Test merging when all args use defaults"""
    config = get_hardcoded_defaults()
    
    args = Namespace(
        path_to_save_files='.',
        files_count=None,
        file_name=None,
        file_prefix=None,
        data_schema=None,
        data_lines=None,
        multiprocessing=None,
        clear_path=False
    )
    
    params = merge_config_with_args(config, args)
    
    # All should come from config
    assert params['files_count'] == 10
    assert params['file_name'] == 'generated_data'
    assert params['file_prefix'] == 'count'
    assert params['data_lines'] == 1000
    assert params['multiprocessing'] == 1
    assert params['clear_path'] is False


def test_merge_config_with_args_all_cli():
    """Test merging when all args are provided via CLI"""
    config = get_hardcoded_defaults()
    
    args = Namespace(
        path_to_save_files='/tmp/data',
        files_count=20,
        file_name='my_data',
        file_prefix='uuid',
        data_schema='{"test": "str:rand"}',
        data_lines=500,
        multiprocessing=4,
        clear_path=True
    )
    
    params = merge_config_with_args(config, args)
    
    # All should come from CLI
    assert params['path_to_save_files'] == '/tmp/data'
    assert params['files_count'] == 20
    assert params['file_name'] == 'my_data'
    assert params['file_prefix'] == 'uuid'
    assert params['data_schema'] == '{"test": "str:rand"}'
    assert params['data_lines'] == 500
    assert params['multiprocessing'] == 4
    assert params['clear_path'] is True

