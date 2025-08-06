"""Fluent builder for macro definitions with immutable pattern."""

from typing import Any, Self

from zmk_layout.models.behaviors import MacroBehavior
from zmk_layout.models.core import LayoutBinding
from zmk_layout.models.types import ParamValue


class MacroBuilder:
    """Fluent builder for macro definitions with immutable pattern.

    This builder provides a chainable interface for creating macro behaviors
    (sequences of key presses and releases).

    Examples:
        >>> macro = (MacroBuilder("vim_save")
        ...     .description("Save file in vim")
        ...     .tap("&kp ESC")      # Escape insert mode
        ...     .wait(10)
        ...     .tap("&kp COLON")    # Enter command mode
        ...     .tap("&kp W")        # Write command
        ...     .tap("&kp ENTER")    # Execute
        ...     .build())
    """

    __slots__ = (
        "_name",
        "_description",
        "_wait_ms",
        "_tap_ms",
        "_bindings",
        "_params",
        "__weakref__",
    )

    def __init__(
        self,
        name: str,
        description: str | None = None,
        wait_ms: int | None = None,
        tap_ms: int | None = None,
        bindings: tuple[LayoutBinding, ...] | None = None,
        params: tuple[ParamValue, ...] | None = None,
    ) -> None:
        """Initialize builder with macro name and optional configuration.

        Args:
            name: Macro name (e.g., "vim_save", "email_sig")
            description: Optional macro description
            wait_ms: Default wait time between actions
            tap_ms: Default tap duration
            bindings: Immutable tuple of binding actions
            params: Immutable tuple of macro parameters
        """
        self._name = name
        self._description = description
        self._wait_ms = wait_ms
        self._tap_ms = tap_ms
        self._bindings: tuple[LayoutBinding, ...] = bindings or ()
        self._params: tuple[ParamValue, ...] | None = params

    def _copy_with(self, **updates: Any) -> Self:
        """Create new instance with updated values (immutable pattern).

        Args:
            **updates: Fields to update in the new instance

        Returns:
            New MacroBuilder instance with updated state
        """
        return self.__class__(
            name=self._name,
            description=updates.get("description", self._description),
            wait_ms=updates.get("wait_ms", self._wait_ms),
            tap_ms=updates.get("tap_ms", self._tap_ms),
            bindings=updates.get("bindings", self._bindings),
            params=updates.get("params", self._params),
        )

    def description(self, desc: str) -> Self:
        """Set macro description - returns new instance.

        Args:
            desc: Description of the macro's purpose

        Returns:
            New builder instance with description set

        Examples:
            >>> builder = MacroBuilder("vim_save").description("Save file in vim")
        """
        return self._copy_with(description=desc)

    def wait(self, ms: int) -> Self:
        """Set default wait time between actions - returns new instance.

        Args:
            ms: Wait time in milliseconds

        Returns:
            New builder instance with wait time set

        Examples:
            >>> builder = builder.wait(10)
        """
        return self._copy_with(wait_ms=ms)

    def tap_time(self, ms: int) -> Self:
        """Set default tap duration - returns new instance.

        Args:
            ms: Tap duration in milliseconds

        Returns:
            New builder instance with tap time set

        Examples:
            >>> builder = builder.tap_time(5)
        """
        return self._copy_with(tap_ms=ms)

    def tap(self, binding: str | LayoutBinding) -> Self:
        """Add tap action - returns new instance.

        This adds a key press and release action to the macro.

        Args:
            binding: Binding string or LayoutBinding object

        Returns:
            New builder instance with tap action added

        Examples:
            >>> builder = builder.tap("&kp A")
            >>> builder = builder.tap(LayoutBinding.from_str("&kp SPACE"))
        """
        binding_obj = LayoutBinding.from_str(binding) if isinstance(binding, str) else binding
        return self._copy_with(bindings=self._bindings + (binding_obj,))

    def press(self, binding: str | LayoutBinding) -> Self:
        """Add press action - returns new instance.

        This adds a key press (without release) action to the macro.

        Args:
            binding: Binding string or LayoutBinding object

        Returns:
            New builder instance with press action added

        Examples:
            >>> builder = builder.press("&kp LSHIFT")  # Hold shift
        """
        if isinstance(binding, str):
            # Convert to press-only binding (implementation specific)
            binding_obj = LayoutBinding.from_str(f"&macro_press {binding}")
        else:
            from zmk_layout.models.core import LayoutParam

            binding_obj = LayoutBinding(
                value="&macro_press",
                params=[LayoutParam(value=binding.value, params=binding.params)],
            )
        return self._copy_with(bindings=self._bindings + (binding_obj,))

    def release(self, binding: str | LayoutBinding) -> Self:
        """Add release action - returns new instance.

        This adds a key release action to the macro.

        Args:
            binding: Binding string or LayoutBinding object

        Returns:
            New builder instance with release action added

        Examples:
            >>> builder = builder.release("&kp LSHIFT")  # Release shift
        """
        if isinstance(binding, str):
            # Convert to release-only binding (implementation specific)
            binding_obj = LayoutBinding.from_str(f"&macro_release {binding}")
        else:
            from zmk_layout.models.core import LayoutParam

            binding_obj = LayoutBinding(
                value="&macro_release",
                params=[LayoutParam(value=binding.value, params=binding.params)],
            )
        return self._copy_with(bindings=self._bindings + (binding_obj,))

    def wait_action(self, ms: int) -> Self:
        """Add explicit wait action - returns new instance.

        This adds a wait/pause to the macro sequence.

        Args:
            ms: Wait duration in milliseconds

        Returns:
            New builder instance with wait action added

        Examples:
            >>> builder = builder.wait_action(100)  # Wait 100ms
        """
        from zmk_layout.models.core import LayoutParam

        wait_binding = LayoutBinding(
            value="&macro_wait",
            params=[LayoutParam(value=str(ms), params=[])],
        )
        return self._copy_with(bindings=self._bindings + (wait_binding,))

    def sequence(self, *bindings: str | LayoutBinding) -> Self:
        """Add sequence of tap actions - returns new instance.

        Convenience method to add multiple tap actions at once.

        Args:
            *bindings: Variable number of binding strings or LayoutBinding objects

        Returns:
            New builder instance with all tap actions added

        Examples:
            >>> builder = builder.sequence("&kp H", "&kp E", "&kp L", "&kp L", "&kp O")
        """
        new_bindings = list(self._bindings)
        for binding in bindings:
            if isinstance(binding, str):
                new_bindings.append(LayoutBinding.from_str(binding))
            else:
                new_bindings.append(binding)
        return self._copy_with(bindings=tuple(new_bindings))

    def params(self, *params: ParamValue) -> Self:
        """Set macro parameters - returns new instance.

        Args:
            *params: Variable number of parameter values

        Returns:
            New builder instance with parameters set

        Examples:
            >>> builder = builder.params("param1", 42)
        """
        return self._copy_with(params=params)

    def build(self) -> MacroBehavior:
        """Build the final MacroBehavior instance.

        Returns:
            Constructed MacroBehavior

        Raises:
            ValueError: If validation fails
        """
        # Validate parameter count
        if self._params and len(self._params) > 2:
            raise ValueError(f"Macro cannot have more than 2 parameters, found {len(self._params)}")

        # Build the macro
        return MacroBehavior(
            name=self._name,
            description=self._description or "",
            waitMs=self._wait_ms,
            tapMs=self._tap_ms,
            bindings=list(self._bindings),
            params=list(self._params) if self._params else None,
        )

    def __repr__(self) -> str:
        """Useful representation for debugging.

        Returns:
            String representation of builder state
        """
        return (
            f"MacroBuilder(name='{self._name}', "
            f"actions={len(self._bindings)}, "
            f"wait={self._wait_ms}ms, "
            f"tap={self._tap_ms}ms)"
        )
