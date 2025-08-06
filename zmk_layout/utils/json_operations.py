"""JSON data operations for layout data."""

import json
from typing import Any, Optional, Union

from ..models import LayoutData


# Module-level flag to control variable resolution
_skip_variable_resolution = False


class VariableResolutionContext:
    """Context manager for controlling variable resolution during operations."""

    def __init__(self, skip: bool = True) -> None:
        self.skip = skip
        self.old_value: bool | None = None

    def __enter__(self) -> "VariableResolutionContext":
        global _skip_variable_resolution
        self.old_value = _skip_variable_resolution
        _skip_variable_resolution = self.skip
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        global _skip_variable_resolution
        if self.old_value is not None:
            _skip_variable_resolution = self.old_value


def parse_layout_data(
    data: str | dict[str, Any],
    skip_variable_resolution: bool = False,
) -> LayoutData:
    """Parse and validate layout data from JSON string or dictionary.

    Args:
        data: JSON string or dictionary containing layout data
        skip_variable_resolution: Whether to skip variable resolution during validation

    Returns:
        LayoutData instance

    Raises:
        json.JSONDecodeError: If data is invalid JSON string
        ValueError: If data is invalid layout data
    """
    global _skip_variable_resolution

    try:
        # Parse JSON string if needed
        if isinstance(data, str):
            parsed_data = json.loads(data)
        else:
            parsed_data = data

        # Set the module flag before validation
        old_skip_value = _skip_variable_resolution
        _skip_variable_resolution = skip_variable_resolution

        try:
            return LayoutData.model_validate(parsed_data)
        finally:
            # Restore the original flag value
            _skip_variable_resolution = old_skip_value

    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON data: {e.msg}", e.doc, e.pos) from e
    except Exception as e:
        raise ValueError(f"Invalid layout data: {e}") from e


def should_skip_variable_resolution() -> bool:
    """Check if variable resolution should be skipped."""
    return _skip_variable_resolution


def serialize_layout_data(
    layout_data: LayoutData, indent: int = 2, ensure_ascii: bool = False
) -> str:
    """Serialize layout data to JSON string with proper formatting.

    Args:
        layout_data: LayoutData instance to serialize
        indent: Number of spaces for indentation (default: 2)
        ensure_ascii: Whether to escape non-ASCII characters (default: False)

    Returns:
        JSON string representation of layout data
    """
    # Use Pydantic's serialization with aliases and sorted fields
    with VariableResolutionContext(skip=True):
        return json.dumps(
            layout_data.model_dump(by_alias=True, exclude_unset=True, mode="json"),
            indent=indent,
            ensure_ascii=ensure_ascii,
        )


def parse_json_data(json_string: str) -> dict[str, Any]:
    """Parse JSON string into dictionary.

    Args:
        json_string: JSON string to parse

    Returns:
        Dictionary with JSON data

    Raises:
        json.JSONDecodeError: If string contains invalid JSON
        ValueError: If JSON does not contain a dictionary
    """
    try:
        data = json.loads(json_string)
        if not isinstance(data, dict):
            raise ValueError("JSON data does not contain a dictionary")
        return data
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON data: {e.msg}", e.doc, e.pos) from e


def serialize_json_data(
    data: dict[str, Any] | list[Any], indent: int = 2, ensure_ascii: bool = False
) -> str:
    """Serialize data to JSON string.

    Args:
        data: Data to serialize as JSON
        indent: Number of spaces for indentation (default: 2)
        ensure_ascii: Whether to escape non-ASCII characters (default: False)

    Returns:
        JSON string representation of data
    """
    return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
