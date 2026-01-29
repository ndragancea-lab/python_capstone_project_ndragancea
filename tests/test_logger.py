"""
Tests for logger module
"""

import pytest
import logging
import sys
from io import StringIO
from dataforge.logger import (
    setup_logger,
    log_start,
    log_completion,
    log_error_and_exit,
    log_progress,
    get_logger
)


def test_setup_logger():
    """Test basic logger setup"""
    logger = setup_logger(name='test_logger', level=logging.INFO)
    
    assert logger is not None
    assert logger.name == 'test_logger'
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0


def test_setup_logger_with_file(tmp_path):
    """Test logger setup with file output"""
    log_file = tmp_path / "test.log"
    logger = setup_logger(name='test_logger_file', log_file=str(log_file))
    
    assert logger is not None
    # Should have both console and file handlers
    assert len(logger.handlers) >= 1
    
    # Test logging to file
    logger.info("Test message")
    
    # Check if file was created and contains message
    assert log_file.exists()
    content = log_file.read_text()
    assert "Test message" in content


def test_setup_logger_with_invalid_file():
    """Test logger setup with invalid file path"""
    # Should not crash, just log a warning
    logger = setup_logger(name='test_invalid', log_file='/invalid/path/file.log')
    assert logger is not None


def test_log_start():
    """Test log_start function"""
    logger = setup_logger(name='test_start')
    
    # Capture output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.handlers = [handler]
    
    log_start(logger, "Test start message")
    
    output = stream.getvalue()
    assert "Test start message" in output
    assert "=" in output


def test_log_completion():
    """Test log_completion function"""
    logger = setup_logger(name='test_completion')
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.handlers = [handler]
    
    details = {'files': 10, 'lines': 1000}
    log_completion(logger, "Test completion", details)
    
    output = stream.getvalue()
    assert "Test completion" in output
    assert "files: 10" in output
    assert "lines: 1000" in output


def test_log_error_and_exit():
    """Test log_error_and_exit function"""
    logger = setup_logger(name='test_error')
    
    # Should exit with code 1
    with pytest.raises(SystemExit) as exc_info:
        log_error_and_exit(logger, "Test error message", exit_code=1)
    
    assert exc_info.value.code == 1


def test_log_progress():
    """Test log_progress function"""
    logger = setup_logger(name='test_progress')
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.handlers = [handler]
    
    log_progress(logger, 50, 100, "files")
    
    output = stream.getvalue()
    assert "50/100" in output
    assert "50.0%" in output
    assert "files" in output


def test_log_progress_zero_total():
    """Test log_progress with zero total"""
    logger = setup_logger(name='test_progress_zero')
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.handlers = [handler]
    
    # Should not crash with zero division
    log_progress(logger, 0, 0, "items")
    
    output = stream.getvalue()
    assert "0/0" in output


def test_get_logger():
    """Test get_logger function"""
    logger1 = get_logger()
    logger2 = get_logger()
    
    # Should return the same instance
    assert logger1 is logger2
    assert logger1.name == 'dataforge'


def test_logger_different_levels():
    """Test logger with different log levels"""
    logger = setup_logger(name='test_levels', level=logging.WARNING)
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.handlers = [handler]
    
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    output = stream.getvalue()
    
    # INFO should not appear (level is WARNING)
    assert "Info message" not in output
    # WARNING and ERROR should appear
    assert "Warning message" in output
    assert "Error message" in output

