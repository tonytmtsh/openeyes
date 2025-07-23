"""
Tests for the utils module.
"""

import pytest
import json
import tempfile
import os
from openeyes.utils import (
    helper_function,
    load_config,
    save_config,
    validate_input,
    format_output
)


class TestHelperFunction:
    """Test cases for helper_function."""
    
    def test_helper_function_string(self):
        """Test helper function with string input."""
        result = helper_function("test")
        assert result == "test"
    
    def test_helper_function_number(self):
        """Test helper function with number input."""
        result = helper_function(42)
        assert result == "42"
    
    def test_helper_function_dict(self):
        """Test helper function with dict input."""
        test_dict = {"key": "value"}
        result = helper_function(test_dict)
        assert "key" in result and "value" in result


class TestConfigOperations:
    """Test cases for configuration loading and saving."""
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        test_config = {"test": "value", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            # Save config
            save_config(test_config, temp_path)
            
            # Load config
            loaded_config = load_config(temp_path)
            
            assert loaded_config == test_config
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_config_file_not_found(self):
        """Test loading config when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_file.json")
    
    def test_load_config_invalid_json(self):
        """Test loading config with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write("invalid json content")
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_config(temp_path)
        finally:
            os.unlink(temp_path)


class TestValidateInput:
    """Test cases for input validation."""
    
    def test_validate_input_valid(self):
        """Test validation with valid input."""
        data = {"field1": "value1", "field2": "value2", "field3": "value3"}
        required_fields = ["field1", "field2"]
        assert validate_input(data, required_fields) is True
    
    def test_validate_input_missing_field(self):
        """Test validation with missing required field."""
        data = {"field1": "value1"}
        required_fields = ["field1", "field2"]
        assert validate_input(data, required_fields) is False
    
    def test_validate_input_not_dict(self):
        """Test validation with non-dict input."""
        data = "not a dict"
        required_fields = ["field1"]
        assert validate_input(data, required_fields) is False
    
    def test_validate_input_empty_requirements(self):
        """Test validation with empty requirements."""
        data = {"field1": "value1"}
        required_fields = []
        assert validate_input(data, required_fields) is True


class TestFormatOutput:
    """Test cases for output formatting."""
    
    def test_format_output_json(self):
        """Test JSON formatting."""
        data = {"key": "value"}
        result = format_output(data, "json")
        assert '"key"' in result and '"value"' in result
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed == data
    
    def test_format_output_text(self):
        """Test text formatting."""
        data = {"key": "value"}
        result = format_output(data, "text")
        assert isinstance(result, str)
        assert "key" in result
    
    def test_format_output_csv_dict_list(self):
        """Test CSV formatting with list of dictionaries."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = format_output(data, "csv")
        lines = result.split("\n")
        assert "name,age" in lines[0]
        assert "Alice,30" in lines[1]
        assert "Bob,25" in lines[2]
    
    def test_format_output_csv_simple(self):
        """Test CSV formatting with simple data."""
        data = "simple string"
        result = format_output(data, "csv")
        assert result == "simple string"
    
    def test_format_output_invalid_format(self):
        """Test formatting with invalid format type."""
        data = {"key": "value"}
        with pytest.raises(ValueError):
            format_output(data, "invalid_format")
