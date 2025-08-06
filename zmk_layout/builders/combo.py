"""Fluent builder for combo definitions with immutable pattern."""

from typing import Any, Self

from zmk_layout.models.behaviors import ComboBehavior
from zmk_layout.models.core import LayoutBinding
from zmk_layout.models.types import LayerIndex


class ComboBuilder:
    """Fluent builder for combo definitions with immutable pattern.

    This builder provides a chainable interface for creating combo behaviors
    (multi-key combinations that trigger specific actions).

    Examples:
        >>> combo = (ComboBuilder("copy")
        ...     .description("Copy shortcut")
        ...     .positions([12, 13])  # Z + X positions
        ...     .binding("&kp LC(C)")
        ...     .timeout(50)
        ...     .layers([0, 1])  # Only on base and nav layers
        ...     .build())
    """

    __slots__ = (
        "_name",
        "_description",
        "_timeout_ms",
        "_key_positions",
        "_layers",
        "_binding",
        "_behavior",
        "__weakref__",
    )

    def __init__(
        self,
        name: str,
        description: str | None = None,
        timeout_ms: int | None = None,
        key_positions: tuple[int, ...] | None = None,
        layers: tuple[LayerIndex, ...] | None = None,
        binding: LayoutBinding | None = None,
        behavior: str | None = None,
    ) -> None:
        """Initialize builder with combo name and optional configuration.

        Args:
            name: Combo name (e.g., "copy", "paste", "undo")
            description: Optional combo description
            timeout_ms: Timeout in milliseconds
            key_positions: Immutable tuple of key positions
            layers: Immutable tuple of layer indices where combo is active
            binding: The binding to trigger
            behavior: Optional behavior override
        """
        self._name = name
        self._description = description
        self._timeout_ms = timeout_ms
        self._key_positions: tuple[int, ...] = key_positions or ()
        self._layers: tuple[LayerIndex, ...] | None = layers
        self._binding = binding
        self._behavior = behavior

    def _copy_with(self, **updates: Any) -> Self:
        """Create new instance with updated values (immutable pattern).

        Args:
            **updates: Fields to update in the new instance

        Returns:
            New ComboBuilder instance with updated state
        """
        return self.__class__(
            name=self._name,
            description=updates.get("description", self._description),
            timeout_ms=updates.get("timeout_ms", self._timeout_ms),
            key_positions=updates.get("key_positions", self._key_positions),
            layers=updates.get("layers", self._layers),
            binding=updates.get("binding", self._binding),
            behavior=updates.get("behavior", self._behavior),
        )

    def description(self, desc: str) -> Self:
        """Set combo description - returns new instance.

        Args:
            desc: Description of the combo's purpose

        Returns:
            New builder instance with description set

        Examples:
            >>> builder = ComboBuilder("copy").description("Copy to clipboard")
        """
        return self._copy_with(description=desc)

    def positions(self, positions: list[int] | tuple[int, ...]) -> Self:
        """Set key positions for combo - returns new instance.

        Args:
            positions: List or tuple of key positions that trigger the combo

        Returns:
            New builder instance with positions set

        Examples:
            >>> builder = builder.positions([12, 13])  # Z + X keys
        """
        positions_tuple = tuple(positions) if isinstance(positions, list) else positions
        return self._copy_with(key_positions=positions_tuple)

    def binding(self, binding: str | LayoutBinding) -> Self:
        """Set combo binding - returns new instance.

        Args:
            binding: Binding string or LayoutBinding object

        Returns:
            New builder instance with binding set

        Examples:
            >>> builder = builder.binding("&kp LC(C)")  # Ctrl+C
            >>> builder = builder.binding(LayoutBinding.from_str("&kp ESC"))
        """
        binding_obj = (
            LayoutBinding.from_str(binding) if isinstance(binding, str) else binding
        )
        return self._copy_with(binding=binding_obj)

    def timeout(self, ms: int) -> Self:
        """Set combo timeout - returns new instance.

        Args:
            ms: Timeout in milliseconds

        Returns:
            New builder instance with timeout set

        Examples:
            >>> builder = builder.timeout(50)
        """
        return self._copy_with(timeout_ms=ms)

    def layers(
        self, layer_indices: list[LayerIndex] | tuple[LayerIndex, ...] | None
    ) -> Self:
        """Set layers where combo is active - returns new instance.

        Args:
            layer_indices: List/tuple of layer indices, or None for all layers

        Returns:
            New builder instance with layers set

        Examples:
            >>> builder = builder.layers([0, 1])  # Only on layers 0 and 1
            >>> builder = builder.layers(None)    # Active on all layers
        """
        if layer_indices is None:
            layers_tuple = None
        else:
            layers_tuple = (
                tuple(layer_indices)
                if isinstance(layer_indices, list)
                else layer_indices
            )
        return self._copy_with(layers=layers_tuple)

    def behavior_override(self, behavior: str) -> Self:
        """Set behavior override - returns new instance.

        Args:
            behavior: Behavior code override

        Returns:
            New builder instance with behavior set

        Examples:
            >>> builder = builder.behavior_override("&custom_combo")
        """
        return self._copy_with(behavior=behavior)

    def build(self) -> ComboBehavior:
        """Build the final ComboBehavior instance.

        Returns:
            Constructed ComboBehavior

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        if not self._key_positions:
            raise ValueError("Combo must have at least one key position")
        if not self._binding:
            raise ValueError("Combo must have a binding")

        # Build the combo
        return ComboBehavior(
            name=self._name,
            description=self._description or "",
            timeoutMs=self._timeout_ms,
            keyPositions=list(self._key_positions),
            layers=list(self._layers) if self._layers is not None else None,
            binding=self._binding,
            behavior=self._behavior,
        )

    def __repr__(self) -> str:
        """Useful representation for debugging.

        Returns:
            String representation of builder state
        """
        return (
            f"ComboBuilder(name='{self._name}', "
            f"positions={list(self._key_positions) if self._key_positions else []}, "
            f"binding={'set' if self._binding else 'none'}, "
            f"layers={list(self._layers) if self._layers else 'all'})"
        )
