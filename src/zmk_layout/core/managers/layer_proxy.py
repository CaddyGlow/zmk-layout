"""Layer proxy for individual layer operations."""

from typing import TYPE_CHECKING

from zmk_layout.models.core import LayoutBinding

if TYPE_CHECKING:
    from zmk_layout.models.metadata import LayoutData
    from zmk_layout.providers import LayoutProviders


class LayerProxy:
    """Proxy for individual layer operations with fluent interface."""

    def __init__(self, layout_data: "LayoutData", layer_name: str, providers: "LayoutProviders") -> None:
        """Initialize layer proxy.

        Args:
            layout_data: Layout data containing the layer
            layer_name: Name of the layer to operate on
            providers: Provider dependencies
        """
        self._data = layout_data
        self._layer_name = layer_name
        self._providers = providers

        if layer_name not in self._data.layer_names:
            raise ValueError(f"Layer '{layer_name}' not found")

        self._layer_index = self._data.layer_names.index(layer_name)

    @property
    def name(self) -> str:
        """Get layer name."""
        return self._layer_name

    @property
    def bindings(self) -> list[LayoutBinding]:
        """Get layer bindings."""
        return self._data.layers[self._layer_index]

    @property
    def size(self) -> int:
        """Get number of bindings in layer."""
        return len(self._data.layers[self._layer_index])

    def set(self, index: int, binding: str | LayoutBinding) -> "LayerProxy":
        """Set binding at index and return self for chaining.

        Args:
            index: Key position index
            binding: Binding string or LayoutBinding object

        Returns:
            Self for method chaining

        Raises:
            IndexError: If index out of range
        """
        layer = self._data.layers[self._layer_index]

        # Ensure layer is large enough
        while len(layer) <= index:
            layer.append(LayoutBinding(value="&trans"))

        if isinstance(binding, str):
            layer[index] = LayoutBinding.from_str(binding)
        else:
            layer[index] = binding

        return self

    def set_range(self, start: int, end: int, bindings: list[str | LayoutBinding]) -> "LayerProxy":
        """Set multiple bindings and return self for chaining.

        Args:
            start: Start index (inclusive)
            end: End index (exclusive)
            bindings: List of bindings to set

        Returns:
            Self for method chaining

        Raises:
            ValueError: If bindings count doesn't match range
            IndexError: If range out of bounds
        """
        if end - start != len(bindings):
            raise ValueError(f"Range size {end - start} doesn't match bindings count {len(bindings)}")

        layer = self._data.layers[self._layer_index]

        # Ensure layer is large enough
        while len(layer) < end:
            layer.append(LayoutBinding(value="&trans"))

        for i, binding in enumerate(bindings):
            if isinstance(binding, str):
                layer[start + i] = LayoutBinding.from_str(binding)
            else:
                layer[start + i] = binding

        return self

    def copy_from(self, source_layer: str) -> "LayerProxy":
        """Copy bindings from another layer.

        Args:
            source_layer: Name of source layer to copy from

        Returns:
            Self for method chaining

        Raises:
            ValueError: If source layer not found
        """
        if source_layer not in self._data.layer_names:
            raise ValueError(f"Source layer '{source_layer}' not found")

        source_index = self._data.layer_names.index(source_layer)
        source_bindings = self._data.layers[source_index]

        # Clear current layer and copy bindings
        self._data.layers[self._layer_index].clear()
        for binding in source_bindings:
            self._data.layers[self._layer_index].append(LayoutBinding.model_validate(binding.model_dump()))

        return self

    def append(self, binding: str | LayoutBinding) -> "LayerProxy":
        """Append binding to end of layer.

        Args:
            binding: Binding to append

        Returns:
            Self for method chaining
        """
        if isinstance(binding, str):
            binding = LayoutBinding.from_str(binding)

        self._data.layers[self._layer_index].append(binding)
        return self

    def insert(self, index: int, binding: str | LayoutBinding) -> "LayerProxy":
        """Insert binding at specific position.

        Args:
            index: Position to insert at
            binding: Binding to insert

        Returns:
            Self for method chaining
        """
        if isinstance(binding, str):
            binding = LayoutBinding.from_str(binding)

        self._data.layers[self._layer_index].insert(index, binding)
        return self

    def remove(self, index: int) -> "LayerProxy":
        """Remove binding at index.

        Args:
            index: Index to remove

        Returns:
            Self for method chaining

        Raises:
            IndexError: If index out of range
        """
        if index < 0 or index >= len(self._data.layers[self._layer_index]):
            raise IndexError(f"Index {index} out of range")

        self._data.layers[self._layer_index].pop(index)
        return self

    def clear(self) -> "LayerProxy":
        """Clear all bindings in layer.

        Returns:
            Self for method chaining
        """
        self._data.layers[self._layer_index].clear()
        return self

    def fill(self, binding: str | LayoutBinding, size: int) -> "LayerProxy":
        """Fill layer with binding up to specified size.

        Args:
            binding: Binding to fill with
            size: Target size

        Returns:
            Self for method chaining
        """
        if isinstance(binding, str):
            binding = LayoutBinding.from_str(binding)

        layer = self._data.layers[self._layer_index]
        layer.clear()

        for _ in range(size):
            layer.append(LayoutBinding.model_validate(binding.model_dump()))

        return self

    def pad_to(self, size: int, padding: str | LayoutBinding = "&trans") -> "LayerProxy":
        """Pad layer to specified size with padding binding.

        Args:
            size: Target size
            padding: Binding to pad with (default: &trans)

        Returns:
            Self for method chaining
        """
        if isinstance(padding, str):
            padding = LayoutBinding.from_str(padding)

        layer = self._data.layers[self._layer_index]

        while len(layer) < size:
            layer.append(LayoutBinding.model_validate(padding.model_dump()))

        return self

    def get(self, index: int) -> LayoutBinding:
        """Get binding at index.

        Args:
            index: Index to get

        Returns:
            LayoutBinding at index

        Raises:
            IndexError: If index out of range
        """
        layer = self._data.layers[self._layer_index]
        if index < 0 or index >= len(layer):
            raise IndexError(f"Index {index} out of range")

        return layer[index]

    def __len__(self) -> int:
        """Get number of bindings."""
        return len(self._data.layers[self._layer_index])

    def __getitem__(self, index: int) -> LayoutBinding:
        """Get binding at index."""
        return self.get(index)

    def __setitem__(self, index: int, binding: str | LayoutBinding) -> None:
        """Set binding at index."""
        self.set(index, binding)

    def __repr__(self) -> str:
        """String representation."""
        return f"LayerProxy(layer='{self._layer_name}', size={len(self)})"
