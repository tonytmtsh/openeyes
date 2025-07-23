"""
Utility functions for the OpenEyes project.
"""

from typing import Any, List, Dict
import json
import os
from pathlib import Path


def helper_function(input_data: Any) -> str:
    """
    A helpful utility function.
    
    Args:
        input_data: Input data of any type
        
    Returns:
        String representation of the input
    """
    return str(input_data)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is not valid JSON
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to a JSON file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path where to save the configuration
    """
    # Create directory if it doesn't exist
    Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=2)


def validate_input(data: Any, required_fields: List[str]) -> bool:
    """
    Validate that input data contains required fields.
    
    Args:
        data: Input data (should be dict-like)
        required_fields: List of required field names
        
    Returns:
        True if all required fields are present, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    return all(field in data for field in required_fields)


def format_output(data: Any, format_type: str = "json") -> str:
    """
    Format output data in the specified format.
    
    Args:
        data: Data to format
        format_type: Output format ("json", "csv", "text")
        
    Returns:
        Formatted string
        
    Raises:
        ValueError: If format_type is not supported
    """
    if format_type == "json":
        return json.dumps(data, indent=2)
    elif format_type == "text":
        return str(data)
    elif format_type == "csv":
        # Basic CSV formatting for simple data
        if isinstance(data, list) and data and isinstance(data[0], dict):
            headers = data[0].keys()
            lines = [",".join(headers)]
            for item in data:
                lines.append(",".join(str(item.get(h, "")) for h in headers))
            return "\n".join(lines)
        else:
            return str(data)
    else:
        raise ValueError(f"Unsupported format type: {format_type}")
