"""Core Layout class for fluent API operations."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from zmk_layout.core.exceptions import ValidationError
from zmk_layout.models.core import LayoutBinding
from zmk_layout.models.metadata import LayoutData


if TYPE_CHECKING:
    from zmk_layout.core.managers import BehaviorManager, LayerManager
    from zmk_layout.generators.keymap_generator import ExportManager
    from zmk_layout.providers import LayoutProviders


class Layout:
    """Main fluent API class for ZMK layout manipulation.

    Provides a chainable interface for layout operations without file I/O:

    Example:
        layout = Layout.from_dict(layout_data_dict)
        layout.layers.add("gaming").set(0, "&kp ESC")
        layout.behaviors.add_hold_tap("hm", "&kp", "&mo")
        output_dict = layout.to_dict()
    """

    def __init__(
        self, layout_data: LayoutData, providers: "LayoutProviders | None" = None
    ) -> None:
        """Initialize Layout with data and providers.

        Args:
            layout_data: Layout data model
            providers: Optional provider dependencies
        """
        self._data = layout_data
        self._providers = providers or self._get_default_providers()
        self._layers = self._create_layer_manager()
        self._behaviors = self._create_behavior_manager()

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], providers: "LayoutProviders | None" = None
    ) -> "Layout":
        """Create Layout from dictionary.

        Args:
            data: Layout data as dictionary
            providers: Optional provider dependencies

        Returns:
            Layout instance
        """
        layout_data = LayoutData.model_validate(data)
        return cls(layout_data, providers)

    @classmethod
    def from_string(
        cls,
        content: str,
        title: str = "Untitled",
        providers: "LayoutProviders | None" = None,
    ) -> "Layout":
        """Create Layout from string content (auto-detects JSON or keymap format).

        Args:
            content: String content (JSON or ZMK keymap)
            title: Optional title for the layout (used for keymap parsing)
            providers: Optional provider dependencies

        Returns:
            Layout instance

        Raises:
            ValueError: If content format cannot be determined or parsed
        """
        import json

        # Try to detect format by content
        content = content.strip()

        # Check if it's JSON (starts with { or [)
        if content.startswith("{") or content.startswith("["):
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    return cls.from_dict(data, providers)
                else:
                    raise ValueError("JSON content must be a dictionary")
            except json.JSONDecodeError:
                pass  # Not JSON, try keymap format

        # Try parsing as keymap
        if "/" in content and "keymap" in content.lower():
            from zmk_layout.parsers.zmk_keymap_parser import (
                ParsingMode,
                ZMKKeymapParser,
            )

            if providers is None:
                from zmk_layout.providers.factory import create_default_providers

                providers = create_default_providers()

            parser = ZMKKeymapParser(
                configuration_provider=providers.configuration, logger=providers.logger
            )

            try:
                parse_result = parser.parse_keymap(
                    content, title=title, mode=ParsingMode.FULL
                )

                # Extract layout data from parse result
                if hasattr(parse_result, "layout_data"):
                    layout_data = parse_result.layout_data
                else:
                    # If parse_result is already LayoutData, use it directly
                    layout_data = (
                        parse_result if isinstance(parse_result, LayoutData) else None
                    )

                # Check if we have valid layout data
                if layout_data is None:
                    raise ValueError("Failed to extract layout data from parse result")

                # Convert to dictionary and create Layout
                layout_dict = layout_data.model_dump(by_alias=True)
                return cls.from_dict(layout_dict, providers)
            except Exception as e:
                raise ValueError(f"Failed to parse as keymap: {e}") from e

        # If we get here, couldn't determine format
        raise ValueError(
            "Could not determine content format (expected JSON or ZMK keymap)"
        )

    @classmethod
    def create_empty(
        cls, keyboard: str, title: str = "", providers: "LayoutProviders | None" = None
    ) -> "Layout":
        """Create empty Layout.

        Args:
            keyboard: Keyboard name
            title: Layout title
            providers: Optional provider dependencies

        Returns:
            Empty Layout instance
        """
        layout_data = LayoutData(
            keyboard=keyboard,
            title=title or f"New {keyboard} Layout",
            layers=[],
            layer_names=[],
        )
        return cls(layout_data, providers)

    @property
    def layers(self) -> "LayerManager":
        """Get layer manager for fluent operations."""
        return self._layers

    @property
    def behaviors(self) -> "BehaviorManager":
        """Get behavior manager for fluent operations."""
        return self._behaviors

    @property
    def data(self) -> LayoutData:
        """Get underlying layout data."""
        return self._data

    def to_dict(self) -> dict[str, Any]:
        """Convert layout to dictionary.

        Returns:
            Layout data as dictionary
        """
        return self._data.model_dump(exclude_none=True)

    @property
    def export(self) -> "ExportManager":
        """Access export functionality with fluent interface.

        Returns:
            Export manager for generating various output formats
        """
        if not hasattr(self, "_export_manager"):
            from zmk_layout.generators.keymap_generator import ExportManager
            self._export_manager = ExportManager(self)
        return self._export_manager

    def validate(self) -> "Layout":
        """Validate layout and return self for chaining.

        Returns:
            Self for method chaining

        Raises:
            ValidationError: If layout is invalid
        """
        # Pydantic validation happens automatically on model access
        # Additional custom validation can be added here
        validation_errors = []

        if not self._data.keyboard:
            validation_errors.append("Keyboard name is required")

        if len(self._data.layers) != len(self._data.layer_names):
            validation_errors.append(
                "Layer count mismatch between layers and layer_names"
            )

        # Check for duplicate layer names
        if len(set(self._data.layer_names)) != len(self._data.layer_names):
            validation_errors.append("Duplicate layer names found")

        # Validate behavior names don't conflict
        if self._data.hold_taps:
            hold_tap_names = [ht.name for ht in self._data.hold_taps]
            if len(set(hold_tap_names)) != len(hold_tap_names):
                validation_errors.append("Duplicate hold-tap behavior names found")

        if validation_errors:
            raise ValidationError("Layout validation failed", validation_errors)

        return self

    def copy(self) -> "Layout":
        """Create a copy of this layout.

        Returns:
            New Layout instance with copied data
        """
        # Deep copy the data
        data_dict = self._data.model_dump()
        new_data = LayoutData.model_validate(data_dict)
        return Layout(new_data, self._providers)

    def _get_default_providers(self) -> "LayoutProviders":
        """Get default providers if none provided."""
        try:
            from zmk_layout.providers.factory import create_default_providers

            return create_default_providers()
        except ImportError:
            # Create minimal providers if factory not available
            from zmk_layout.providers import LayoutProviders
            from zmk_layout.providers.factory import (
                DefaultConfigurationProvider,
                DefaultLogger,
                DefaultTemplateProvider,
            )

            return LayoutProviders(
                configuration=DefaultConfigurationProvider(),
                template=DefaultTemplateProvider(),
                logger=DefaultLogger(),
            )

    def _create_layer_manager(self) -> "LayerManager":
        """Create layer manager instance."""
        from zmk_layout.core.managers import LayerManager

        return LayerManager(self._data, self._providers)

    def _create_behavior_manager(self) -> "BehaviorManager":
        """Create behavior manager instance."""
        from zmk_layout.core.managers import BehaviorManager

        return BehaviorManager(self._data, self._providers)

    def __enter__(self) -> "Layout":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Context manager exit."""
        # No cleanup needed for data-only operations
        pass

    def batch_operation(self, operations: list[Callable[["Layout"], Any]]) -> "Layout":
        """Execute multiple operations in batch and return self for chaining.

        Args:
            operations: List of functions that take Layout as argument

        Returns:
            Self for method chaining

        Example:
            layout.batch_operation([
                lambda l: l.layers.add("gaming"),
                lambda l: l.layers.get("gaming").set(0, "&kp ESC"),
                lambda l: l.behaviors.add_hold_tap("hm", "&kp A", "&mo 1")
            ])
        """
        for operation in operations:
            operation(self)
        return self

    def find_layers(self, predicate: Callable[[str], bool]) -> list[str]:
        """Find layers matching predicate.

        Args:
            predicate: Function that takes layer name and returns bool

        Returns:
            List of matching layer names

        Example:
            gaming_layers = layout.find_layers(lambda name: "game" in name.lower())
        """
        return [name for name in self._data.layer_names if predicate(name)]

    def get_statistics(self) -> dict[str, Any]:
        """Get layout statistics.

        Returns:
            Dictionary with layout statistics
        """
        stats = {
            "keyboard": self._data.keyboard,
            "title": self._data.title,
            "layer_count": len(self._data.layer_names),
            "layer_names": list(self._data.layer_names),
            "total_bindings": sum(len(layer) for layer in self._data.layers),
            "behavior_counts": {
                "hold_taps": len(self._data.hold_taps) if self._data.hold_taps else 0,
                "combos": len(self._data.combos) if self._data.combos else 0,
                "macros": len(self._data.macros) if self._data.macros else 0,
                "tap_dances": len(self._data.tap_dances)
                if self._data.tap_dances
                else 0,
            },
            "total_behaviors": self._behaviors.total_count,
        }

        # Add layer sizes
        if self._data.layers:
            layer_sizes = [len(layer) for layer in self._data.layers]
            stats["layer_sizes"] = dict(
                zip(self._data.layer_names, layer_sizes, strict=False)
            )
            stats["avg_layer_size"] = (
                sum(layer_sizes) / len(layer_sizes) if layer_sizes else 0
            )
            stats["max_layer_size"] = max(layer_sizes) if layer_sizes else 0
            stats["min_layer_size"] = min(layer_sizes) if layer_sizes else 0

        return stats

    def __repr__(self) -> str:
        """String representation."""
        return f"Layout(keyboard='{self._data.keyboard}', layers={len(self._data.layer_names)})"
