"""Layer management for fluent API operations."""

from typing import TYPE_CHECKING

from zmk_layout.models.core import LayoutBinding

if TYPE_CHECKING:
    from zmk_layout.models.metadata import LayoutData
    from zmk_layout.providers import LayoutProviders

    from .layer_proxy import LayerProxy


class LayerManager:
    """Manager for layer operations with fluent interface."""

    def __init__(self, layout_data: "LayoutData", providers: "LayoutProviders") -> None:
        """Initialize layer manager.

        Args:
            layout_data: Layout data to manage
            providers: Provider dependencies
        """
        self._data = layout_data
        self._providers = providers

    def add(self, name: str, position: int | None = None) -> "LayerProxy":
        """Add new layer and return proxy for chaining.

        Args:
            name: Layer name
            position: Optional position to insert at (default: append)

        Returns:
            LayerProxy for the new layer

        Raises:
            ValueError: If layer name already exists
        """
        if name in self._data.layer_names:
            raise ValueError(f"Layer '{name}' already exists")

        # Initialize empty layer with default bindings
        empty_layer = []

        if position is None:
            # Append to end
            self._data.layer_names.append(name)
            self._data.layers.append(empty_layer)
        else:
            # Insert at position
            if position < 0 or position > len(self._data.layer_names):
                raise IndexError(f"Position {position} out of range")
            self._data.layer_names.insert(position, name)
            self._data.layers.insert(position, empty_layer)

        return self.get(name)

    def get(self, name: str) -> "LayerProxy":
        """Get layer proxy for chaining operations.

        Args:
            name: Layer name

        Returns:
            LayerProxy for the layer

        Raises:
            ValueError: If layer not found
        """
        if name not in self._data.layer_names:
            raise ValueError(f"Layer '{name}' not found")

        from .layer_proxy import LayerProxy

        return LayerProxy(self._data, name, self._providers)

    def remove(self, name: str) -> "LayerManager":
        """Remove layer and return self for chaining.

        Args:
            name: Layer name to remove

        Returns:
            Self for method chaining

        Raises:
            ValueError: If layer not found
        """
        if name not in self._data.layer_names:
            raise ValueError(f"Layer '{name}' not found")

        index = self._data.layer_names.index(name)
        self._data.layer_names.pop(index)
        self._data.layers.pop(index)

        return self

    def move(self, name: str, position: int) -> "LayerManager":
        """Move layer to new position and return self for chaining.

        Args:
            name: Layer name to move
            position: New position

        Returns:
            Self for method chaining

        Raises:
            ValueError: If layer not found
            IndexError: If position out of range
        """
        if name not in self._data.layer_names:
            raise ValueError(f"Layer '{name}' not found")

        if position < 0 or position >= len(self._data.layer_names):
            raise IndexError(f"Position {position} out of range")

        # Remove from current position
        current_index = self._data.layer_names.index(name)
        layer_name = self._data.layer_names.pop(current_index)
        layer_data = self._data.layers.pop(current_index)

        # Insert at new position
        self._data.layer_names.insert(position, layer_name)
        self._data.layers.insert(position, layer_data)

        return self

    def rename(self, old_name: str, new_name: str) -> "LayerManager":
        """Rename a layer and return self for chaining.

        Args:
            old_name: Current layer name
            new_name: New layer name

        Returns:
            Self for method chaining

        Raises:
            ValueError: If old layer not found or new name exists
        """
        if old_name not in self._data.layer_names:
            raise ValueError(f"Layer '{old_name}' not found")

        if new_name in self._data.layer_names:
            raise ValueError(f"Layer '{new_name}' already exists")

        index = self._data.layer_names.index(old_name)
        self._data.layer_names[index] = new_name

        return self

    def copy(self, source_name: str, target_name: str) -> "LayerProxy":
        """Copy layer to new layer and return proxy for chaining.

        Args:
            source_name: Source layer name
            target_name: Target layer name

        Returns:
            LayerProxy for the new layer

        Raises:
            ValueError: If source not found or target exists
        """
        if source_name not in self._data.layer_names:
            raise ValueError(f"Layer '{source_name}' not found")

        if target_name in self._data.layer_names:
            raise ValueError(f"Layer '{target_name}' already exists")

        # Get source layer data
        source_index = self._data.layer_names.index(source_name)
        source_layer = self._data.layers[source_index]

        # Create copy of layer data
        copied_layer = [LayoutBinding.model_validate(binding.model_dump()) for binding in source_layer]

        # Add new layer
        self._data.layer_names.append(target_name)
        self._data.layers.append(copied_layer)

        return self.get(target_name)

    def clear(self, name: str) -> "LayerProxy":
        """Clear all bindings in layer and return proxy for chaining.

        Args:
            name: Layer name to clear

        Returns:
            LayerProxy for the cleared layer

        Raises:
            ValueError: If layer not found
        """
        if name not in self._data.layer_names:
            raise ValueError(f"Layer '{name}' not found")

        index = self._data.layer_names.index(name)
        self._data.layers[index].clear()

        return self.get(name)

    @property
    def names(self) -> list[str]:
        """Get list of layer names."""
        return list(self._data.layer_names)

    @property
    def count(self) -> int:
        """Get number of layers."""
        return len(self._data.layer_names)

    def __contains__(self, name: str) -> bool:
        """Check if layer exists."""
        return name in self._data.layer_names

    def __len__(self) -> int:
        """Get number of layers."""
        return len(self._data.layer_names)

    def __iter__(self):
        """Iterate over layer names."""
        return iter(self._data.layer_names)
