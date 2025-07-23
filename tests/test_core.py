"""
Tests for the core module.
"""

import pytest
from openeyes.core import OpenEyes, main


class TestOpenEyes:
    """Test cases for the OpenEyes class."""
    
    def test_init_default(self):
        """Test OpenEyes initialization with default config."""
        app = OpenEyes()
        assert app.config == {}
    
    def test_init_with_config(self):
        """Test OpenEyes initialization with custom config."""
        config = {"test": "value"}
        app = OpenEyes(config)
        assert app.config == config
    
    def test_process(self):
        """Test the process method."""
        app = OpenEyes()
        test_data = "test_input"
        result = app.process(test_data)
        assert result == test_data
    
    def test_get_version(self):
        """Test version retrieval."""
        app = OpenEyes()
        version = app.get_version()
        assert isinstance(version, str)
        assert version == "0.1.0"


def test_main_function(capsys):
    """Test the main function output."""
    main()
    captured = capsys.readouterr()
    assert "OpenEyes is running!" in captured.out


def test_main_function_no_exception():
    """Test that main function runs without exceptions."""
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")
