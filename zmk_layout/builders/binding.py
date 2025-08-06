"""Fluent builder for LayoutBinding objects with immutable pattern and thread safety."""

import weakref
from threading import RLock
from typing import TYPE_CHECKING, Any, Self

from zmk_layout.models.types import ParamValue


if TYPE_CHECKING:
    from ..models.core import LayoutBinding


class BuildError(Exception):
    """Enhanced error with builder state context for debugging."""

    def __init__(self, message: str, builder_state: dict[str, Any] | None = None) -> None:
        self.builder_state = builder_state
        details = f"\nBuilder state: {builder_state}" if builder_state else ""
        suggestion = "\nSuggestion: Check binding syntax and parameter structure"
        super().__init__(f"{message}{details}{suggestion}")


class LayoutBindingBuilder:
    """Advanced fluent builder for complex bindings with thread safety.

    This builder uses an immutable pattern where each method returns a new
    instance with updated state. Thread-safe caching is implemented to
    optimize performance for repeated patterns.

    Examples:
        >>> builder = LayoutBindingBuilder("&kp")
        >>> binding = builder.modifier("LC").modifier("LS").key("A").build()
        >>> print(binding.to_str())
        &kp LC(LS(A))

        >>> binding = LayoutBindingBuilder("&mt").param("LCTRL").param("ESC").build()
        >>> print(binding.to_str())
        &mt LCTRL ESC
    """

    # Class-level cache for performance
    _cache_lock = RLock()
    _result_cache: weakref.WeakValueDictionary[int, Any] = weakref.WeakValueDictionary()

    __slots__ = ("_behavior", "_params", "_modifiers", "__weakref__")  # Memory optimization

    def __init__(
        self,
        behavior: str,
        params: tuple[Any, ...] | None = None,
        modifiers: tuple[str, ...] | None = None,
    ) -> None:
        """Initialize builder with behavior and optional state.

        Args:
            behavior: The ZMK behavior (e.g., "&kp", "&mt", "&lt")
            params: Immutable tuple of parameters
            modifiers: Immutable tuple of modifiers
        """
        self._behavior = behavior if behavior.startswith("&") else f"&{behavior}"
        self._params: tuple[Any, ...] = params or ()
        self._modifiers: tuple[str, ...] = modifiers or ()

    def _copy_with(self, **updates: Any) -> Self:
        """Create new instance with updated values (immutable pattern).

        Args:
            **updates: Fields to update in the new instance

        Returns:
            New LayoutBindingBuilder instance with updated state
        """
        return self.__class__(
            behavior=self._behavior,
            params=updates.get("params", self._params),
            modifiers=updates.get("modifiers", self._modifiers),
        )

    def param(self, value: ParamValue) -> Self:
        """Add simple parameter - returns new instance.

        Args:
            value: Parameter value (string or integer)

        Returns:
            New builder instance with added parameter

        Examples:
            >>> builder = LayoutBindingBuilder("&kp").param("A")
            >>> builder = LayoutBindingBuilder("&lt").param(1).param("SPACE")
        """
        from ..models.core import LayoutParam

        new_param = LayoutParam(value=value, params=[])
        return self._copy_with(params=self._params + (new_param,))

    def modifier(self, mod: str) -> Self:
        """Add modifier to chain - returns new instance.

        Modifiers are accumulated and applied when key() is called.

        Args:
            mod: Modifier name (e.g., "LC", "LS", "LA", "LG")

        Returns:
            New builder instance with added modifier

        Examples:
            >>> builder = LayoutBindingBuilder("&kp").modifier("LC").modifier("LS")
        """
        return self._copy_with(modifiers=self._modifiers + (mod,))

    def nested_param(self, parent: str, child: ParamValue) -> Self:
        """Add nested parameter like LC(A) - returns new instance.

        Args:
            parent: Parent parameter name
            child: Child parameter value

        Returns:
            New builder instance with nested parameter

        Examples:
            >>> builder = LayoutBindingBuilder("&kp").nested_param("LC", "A")
        """
        from ..models.core import LayoutParam

        child_param = LayoutParam(value=child, params=[])
        nested = LayoutParam(value=parent, params=[child_param])
        return self._copy_with(params=self._params + (nested,))

    def key(self, key: str) -> Self:
        """Set final key (terminal for modifiers) - returns new instance.

        If modifiers have been accumulated, this creates a nested structure.
        Otherwise, it adds a simple parameter.

        Args:
            key: Key code or name

        Returns:
            New builder instance with key parameter

        Examples:
            >>> # With modifiers
            >>> builder = LayoutBindingBuilder("&kp").modifier("LC").key("A")
            >>> # Result: &kp LC(A)

            >>> # Without modifiers
            >>> builder = LayoutBindingBuilder("&kp").key("SPACE")
            >>> # Result: &kp SPACE
        """
        from ..models.core import LayoutParam

        if self._modifiers:
            # Build nested modifier chain: LC(LS(key))
            result = LayoutParam(value=key, params=[])
            for mod in reversed(self._modifiers):
                result = LayoutParam(value=mod, params=[result])
            return self._copy_with(params=self._params + (result,), modifiers=())
        else:
            new_param = LayoutParam(value=key, params=[])
            return self._copy_with(params=self._params + (new_param,))

    def hold_tap(self, hold: ParamValue, tap: ParamValue) -> Self:
        """Add hold-tap parameters - returns new instance.

        Convenience method for mod-tap and layer-tap behaviors.

        Args:
            hold: Hold behavior or layer
            tap: Tap key code

        Returns:
            New builder instance with hold-tap parameters

        Examples:
            >>> builder = LayoutBindingBuilder("&mt").hold_tap("LCTRL", "ESC")
            >>> builder = LayoutBindingBuilder("&lt").hold_tap(1, "SPACE")
        """
        from ..models.core import LayoutParam

        hold_param = LayoutParam(value=hold, params=[])
        tap_param = LayoutParam(value=tap, params=[])
        return self._copy_with(params=self._params + (hold_param, tap_param))

    def _get_cache_key(self) -> int:
        """Generate cache key for current builder state.

        Returns:
            Hash of current state for cache lookup
        """
        # Convert params to hashable format (string representation)
        param_strs = tuple(str(p) for p in self._params) if self._params else ()
        return hash((self._behavior, param_strs, self._modifiers))

    def build(self) -> "LayoutBinding":
        """Build final LayoutBinding with caching and thread safety.

        Returns:
            Constructed LayoutBinding instance

        Raises:
            BuildError: If binding construction fails
        """
        from ..models.core import LayoutBinding

        cache_key = self._get_cache_key()

        # Check cache first
        with self._cache_lock:
            cached = self._result_cache.get(cache_key)
            if cached is not None:
                return cached  # type: ignore[no-any-return]

        # Build new instance
        try:
            result = LayoutBinding(value=self._behavior, params=list(self._params))
        except Exception as e:
            # Enhanced error with builder state context
            raise BuildError(
                f"Failed to build LayoutBinding: {e}",
                builder_state={
                    "behavior": self._behavior,
                    "params": [str(p) for p in self._params],
                    "modifiers": list(self._modifiers),
                },
            ) from e

        # Cache result
        with self._cache_lock:
            self._result_cache[cache_key] = result

        return result

    def __repr__(self) -> str:
        """Useful representation for debugging.

        Returns:
            String representation of builder state
        """
        return (
            f"LayoutBindingBuilder(behavior='{self._behavior}', "
            f"params={len(self._params)}, modifiers={list(self._modifiers)})"
        )
