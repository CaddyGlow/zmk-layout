"""Core layout operations and file processing utilities."""

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar


if TYPE_CHECKING:
    from ..providers import ConfigurationProvider, FileProvider, LayoutLogger

from ..models import LayoutData


T = TypeVar("T")


class OutputPaths:
    """Output file paths for ZMK compilation."""

    def __init__(self, keymap: Path, conf: Path, json: Path):
        self.keymap = keymap
        self.conf = conf
        self.json = json


class LayoutError(Exception):
    """Error in layout processing."""

    pass


def prepare_output_paths(
    output_file_prefix: str | Path,
    configuration_provider: "ConfigurationProvider | None" = None,
) -> OutputPaths:
    """Prepare standardized output file paths.

    Given an output file prefix (which can be a path and base name),
    generates an OutputPaths object with standardized paths.

    Args:
        output_file_prefix: Base path and name for output files (str or Path)
        configuration_provider: Optional configuration provider for file extensions

    Returns:
        OutputPaths with standardized paths for keymap, conf, and json files

    Examples:
        >>> prepare_output_paths("/tmp/my_keymap")
        OutputPaths(
            keymap=PosixPath('/tmp/my_keymap.keymap'),
            conf=PosixPath('/tmp/my_keymap.conf'),
            json=PosixPath('/tmp/my_keymap.json')
        )
    """
    output_prefix_path = Path(output_file_prefix).resolve()

    # Extract directory and base name
    output_dir = output_prefix_path.parent
    base_name = output_prefix_path.name

    # Generate paths with appropriate extensions
    keymap_path = output_dir / f"{base_name}.keymap"
    conf_path = output_dir / f"{base_name}.conf"
    json_path = output_dir / f"{base_name}.json"

    return OutputPaths(
        keymap=keymap_path,
        conf=conf_path,
        json=json_path,
    )


def process_json_file(
    file_path: Path,
    operation_name: str,
    operation_func: Callable[[LayoutData], T],
    file_provider: "FileProvider",
    logger: "LayoutLogger | None" = None,
    process_templates: bool = True,
) -> T:
    """Process a JSON keymap file with error handling and validation.

    Args:
        file_path: Path to the JSON file to process
        operation_name: Human-readable name of the operation for error messages
        operation_func: Function that takes LayoutData and returns result
        file_provider: File provider for reading operations
        logger: Optional logger for status messages
        process_templates: Whether to process Jinja2 templates (default: True)

    Returns:
        Result from the operation function

    Raises:
        LayoutError: If file loading, validation, or operation fails
    """
    try:
        if logger:
            logger.info(f"{operation_name} from {file_path}...")

        # Load with or without template processing based on parameter
        from .json_operations import load_layout_file

        layout_data = load_layout_file(
            file_path,
            file_provider,
            skip_template_processing=(not process_templates),
        )

        # Perform the operation
        return operation_func(layout_data)

    except Exception as e:
        if logger:
            logger.error(f"{operation_name} failed: {e}")
        raise LayoutError(f"{operation_name} failed: {e}") from e


def resolve_template_file_path(
    keyboard_name: str,
    template_file: str,
    configuration_provider: "ConfigurationProvider | None" = None,
) -> Path:
    """Resolve a template file path relative to keyboard configuration directories.

    Args:
        keyboard_name: Name of the keyboard configuration
        template_file: Relative path to the template file
        configuration_provider: Optional configuration provider for search paths

    Returns:
        Resolved absolute path to the template file

    Raises:
        LayoutError: If the template file cannot be found
    """
    template_path_obj = Path(template_file)

    # If absolute path, validate and use as-is
    if template_path_obj.is_absolute():
        if template_path_obj.exists():
            return template_path_obj.resolve()
        raise LayoutError(f"Template file not found: {template_file}")

    # Get search paths from provider or use default
    search_paths = (
        configuration_provider.get_search_paths()
        if configuration_provider
        else [Path.cwd()]
    )

    # Try to resolve relative to keyboard configuration directories
    for search_path in search_paths:
        # Try relative to keyboard directory (for modular configs)
        keyboard_dir = search_path / keyboard_name
        if keyboard_dir.exists() and keyboard_dir.is_dir():
            keyboard_relative = keyboard_dir / template_path_obj
            if keyboard_relative.exists():
                return keyboard_relative.resolve()

        # Try relative to search path root
        search_relative = search_path / template_path_obj
        if search_relative.exists():
            return search_relative.resolve()

    raise LayoutError(
        f"Template file not found: {template_file}. "
        f"Searched relative to keyboard '{keyboard_name}' directories in: "
        f"{[str(p) for p in search_paths]}"
    )
