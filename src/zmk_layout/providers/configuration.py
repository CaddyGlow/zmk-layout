"""Configuration provider protocol for layout domain abstraction."""

from typing import Any, Protocol


class SystemBehavior:
    """Simplified system behavior representation for standalone library.
    
    This is a minimal implementation to avoid circular dependencies.
    External implementations should provide their own SystemBehavior classes.
    """
    
    def __init__(self, name: str, description: str = "", **kwargs: Any):
        self.name = name
        self.description = description
        self.properties = kwargs


class ConfigurationProvider(Protocol):
    """Protocol for providing keyboard configuration to the layout domain.

    This abstraction enables the layout library to operate independently
    of the specific profile/configuration system implementation.
    """

    def get_behavior_definitions(self) -> list[SystemBehavior]:
        """Get all available ZMK behaviors for validation and registration.

        Returns:
            List of SystemBehavior objects with behavior definitions
        """
        ...

    def get_include_files(self) -> list[str]:
        """Get required include files for ZMK compilation.

        Returns:
            List of include file paths (e.g., ["zmk/include/dt-bindings/zmk/keys.h"])
        """
        ...

    def get_validation_rules(self) -> dict[str, Any]:
        """Get keyboard-specific validation rules and constraints.

        Returns:
            Dictionary containing validation configuration such as:
            - max_layers: Maximum number of layers supported
            - key_positions: Available key position indices
            - supported_behaviors: Behavior codes that are valid
        """
        ...

    def get_template_context(self) -> dict[str, Any]:
        """Get context data for template processing during generation.

        Returns:
            Dictionary with template variables such as:
            - keyboard_name: Name identifier for the keyboard
            - firmware_version: ZMK firmware version
            - key_position_header: Key position definitions
            - system_behaviors_dts: System behavior device tree nodes
        """
        ...

    def get_kconfig_options(self) -> dict[str, Any]:
        """Get available kconfig options for configuration generation.

        Returns:
            Dictionary mapping option names to their configurations
        """
        ...

    def get_formatting_config(self) -> dict[str, Any]:
        """Get formatting preferences for generated files.

        Returns:
            Dictionary with formatting options such as:
            - key_gap: Spacing between keys in keymap
            - base_indent: Base indentation for generated content
            - rows: Row configuration for keymap formatting
        """
        ...