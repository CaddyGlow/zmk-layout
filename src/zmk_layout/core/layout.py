"""Core Layout class for fluent API operations."""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from zmk_layout.models.metadata import LayoutData

if TYPE_CHECKING:
    from zmk_layout.core.managers import BehaviorManager, LayerManager
    from zmk_layout.providers import LayoutProviders


class Layout:
    """Main fluent API class for ZMK layout manipulation.

    Provides a chainable interface for layout operations:

    Example:
        layout = Layout.from_file("my_layout.json")
        layout.layers.add("gaming").set(0, "&kp ESC")
        layout.behaviors.add_hold_tap("hm", "&kp", "&mo")
        layout.save("output.json")
    """

    def __init__(self, layout_data: LayoutData, providers: "LayoutProviders | None" = None) -> None:
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
    def from_file(cls, source: str | Path, providers: "LayoutProviders | None" = None) -> "Layout":
        """Create Layout from file.

        Args:
            source: Path to JSON layout file
            providers: Optional provider dependencies

        Returns:
            Layout instance
        """
        # Load JSON file and validate as LayoutData
        with open(Path(source), encoding="utf-8") as f:
            data = json.load(f)
        layout_data = LayoutData.model_validate(data)
        return cls(layout_data, providers)

    @classmethod
    def from_dict(cls, data: dict[str, Any], providers: "LayoutProviders | None" = None) -> "Layout":
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
    def create_empty(cls, keyboard: str, title: str = "", providers: "LayoutProviders | None" = None) -> "Layout":
        """Create empty Layout.

        Args:
            keyboard: Keyboard name
            title: Layout title
            providers: Optional provider dependencies

        Returns:
            Empty Layout instance
        """
        layout_data = LayoutData(keyboard=keyboard, title=title or f"New {keyboard} Layout", layers=[], layer_names=[])
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

    def save(self, output: str | Path) -> "Layout":
        """Save layout and return self for chaining.

        Args:
            output: Output file path

        Returns:
            Self for method chaining
        """
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict and save as JSON
        layout_dict = self._data.model_dump(exclude_none=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(layout_dict, f, indent=2, ensure_ascii=False)

        return self

    def validate(self) -> "Layout":
        """Validate layout and return self for chaining.

        Returns:
            Self for method chaining

        Raises:
            ValidationError: If layout is invalid
        """
        # Pydantic validation happens automatically on model access
        # Additional custom validation can be added here
        if not self._data.keyboard:
            raise ValueError("Keyboard name is required")

        if len(self._data.layers) != len(self._data.layer_names):
            raise ValueError("Layer count mismatch between layers and layer_names")

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

            return LayoutProviders()

    def _create_layer_manager(self) -> "LayerManager":
        """Create layer manager instance."""
        from zmk_layout.core.managers import LayerManager

        return LayerManager(self._data, self._providers)

    def _create_behavior_manager(self) -> "BehaviorManager":
        """Create behavior manager instance."""
        from zmk_layout.core.managers import BehaviorManager

        return BehaviorManager(self._data, self._providers)

    def __repr__(self) -> str:
        """String representation."""
        return f"Layout(keyboard='{self._data.keyboard}', layers={len(self._data.layer_names)})"
