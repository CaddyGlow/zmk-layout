"""ZMK Layout Utilities.

This module provides utility functions for layout operations.
"""

from .json_operations import (
    VariableResolutionContext,
    load_json_data,
    load_layout_file,
    save_json_data,
    save_layout_file,
    should_skip_variable_resolution,
)
from .layer_references import (
    LayoutError,
    OutputPaths,
    prepare_output_paths,
    process_json_file,
    resolve_template_file_path,
)
from .validation import (
    validate_layer_exists,
    validate_layer_has_bindings,
    validate_layer_name_unique,
    validate_output_path,
    validate_position_index,
)


__all__ = [
    # JSON operations
    "VariableResolutionContext",
    "load_layout_file",
    "save_layout_file",
    "load_json_data",
    "save_json_data",
    "should_skip_variable_resolution",
    # Layer references
    "LayoutError",
    "OutputPaths",
    "prepare_output_paths",
    "process_json_file",
    "resolve_template_file_path",
    # Validation
    "validate_layer_exists",
    "validate_layer_has_bindings",
    "validate_layer_name_unique",
    "validate_output_path",
    "validate_position_index",
]
