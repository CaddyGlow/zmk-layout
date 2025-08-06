"""Fluent builder for behavior definitions with immutable pattern."""

from typing import Any, Self

from zmk_layout.models.behaviors import HoldTapBehavior
from zmk_layout.models.types import TemplateNumeric


class BehaviorBuilder:
    """Fluent builder for hold-tap behavior definitions with immutable pattern.

    This builder provides a chainable interface for creating hold-tap behaviors
    (home row mods, layer taps, etc.) with comprehensive configuration options.

    Examples:
        >>> behavior = (BehaviorBuilder("hm_l")
        ...     .description("Left hand home row mod")
        ...     .bindings("&kp", "&kp")
        ...     .tapping_term(200)
        ...     .flavor("balanced")
        ...     .quick_tap(125)
        ...     .positions([1, 2, 3, 4, 5])  # Left hand positions
        ...     .build())
    """

    __slots__ = (
        "_name",
        "_description",
        "_bindings",
        "_tapping_term_ms",
        "_quick_tap_ms",
        "_flavor",
        "_hold_trigger_on_release",
        "_require_prior_idle_ms",
        "_hold_trigger_key_positions",
        "_retro_tap",
        "_tap_behavior",
        "_hold_behavior",
        "__weakref__",
    )

    def __init__(
        self,
        name: str,
        description: str | None = None,
        bindings: tuple[str, ...] | None = None,
        tapping_term_ms: TemplateNumeric = None,
        quick_tap_ms: TemplateNumeric = None,
        flavor: str | None = None,
        hold_trigger_on_release: bool | None = None,
        require_prior_idle_ms: TemplateNumeric = None,
        hold_trigger_key_positions: tuple[int, ...] | None = None,
        retro_tap: bool | None = None,
        tap_behavior: str | None = None,
        hold_behavior: str | None = None,
    ) -> None:
        """Initialize builder with behavior name and optional configuration.

        Args:
            name: Behavior name (e.g., "hm_l", "hrm_r", "layer_tap")
            description: Optional behavior description
            bindings: Immutable tuple of binding behaviors
            tapping_term_ms: Tapping term in milliseconds
            quick_tap_ms: Quick tap term in milliseconds
            flavor: Hold-tap flavor
            hold_trigger_on_release: Whether to trigger on release
            require_prior_idle_ms: Required idle time before activation
            hold_trigger_key_positions: Immutable tuple of key positions
            retro_tap: Enable retro tap
            tap_behavior: Tap behavior override
            hold_behavior: Hold behavior override
        """
        self._name = name
        self._description = description
        self._bindings: tuple[str, ...] = bindings or ()
        self._tapping_term_ms = tapping_term_ms
        self._quick_tap_ms = quick_tap_ms
        self._flavor = flavor
        self._hold_trigger_on_release = hold_trigger_on_release
        self._require_prior_idle_ms = require_prior_idle_ms
        self._hold_trigger_key_positions: tuple[int, ...] = (
            hold_trigger_key_positions or ()
        )
        self._retro_tap = retro_tap
        self._tap_behavior = tap_behavior
        self._hold_behavior = hold_behavior

    def _copy_with(self, **updates: Any) -> Self:
        """Create new instance with updated values (immutable pattern).

        Args:
            **updates: Fields to update in the new instance

        Returns:
            New BehaviorBuilder instance with updated state
        """
        return self.__class__(
            name=self._name,
            description=updates.get("description", self._description),
            bindings=updates.get("bindings", self._bindings),
            tapping_term_ms=updates.get("tapping_term_ms", self._tapping_term_ms),
            quick_tap_ms=updates.get("quick_tap_ms", self._quick_tap_ms),
            flavor=updates.get("flavor", self._flavor),
            hold_trigger_on_release=updates.get(
                "hold_trigger_on_release", self._hold_trigger_on_release
            ),
            require_prior_idle_ms=updates.get(
                "require_prior_idle_ms", self._require_prior_idle_ms
            ),
            hold_trigger_key_positions=updates.get(
                "hold_trigger_key_positions", self._hold_trigger_key_positions
            ),
            retro_tap=updates.get("retro_tap", self._retro_tap),
            tap_behavior=updates.get("tap_behavior", self._tap_behavior),
            hold_behavior=updates.get("hold_behavior", self._hold_behavior),
        )

    def description(self, desc: str) -> Self:
        """Set behavior description - returns new instance.

        Args:
            desc: Description of the behavior's purpose

        Returns:
            New builder instance with description set

        Examples:
            >>> builder = BehaviorBuilder("hm_l").description("Left hand home row mod")
        """
        return self._copy_with(description=desc)

    def bindings(self, hold: str, tap: str) -> Self:
        """Set hold and tap bindings - returns new instance.

        Args:
            hold: Hold binding behavior (e.g., "&kp", "&mo")
            tap: Tap binding behavior (e.g., "&kp", "&trans")

        Returns:
            New builder instance with bindings set

        Examples:
            >>> builder = BehaviorBuilder("hm_l").bindings("&kp", "&kp")
        """
        return self._copy_with(bindings=(hold, tap))

    def tapping_term(self, ms: int) -> Self:
        """Set tapping term - returns new instance.

        Args:
            ms: Tapping term in milliseconds

        Returns:
            New builder instance with tapping term set

        Examples:
            >>> builder = builder.tapping_term(200)
        """
        return self._copy_with(tapping_term_ms=ms)

    def quick_tap(self, ms: int) -> Self:
        """Set quick tap term - returns new instance.

        Args:
            ms: Quick tap term in milliseconds

        Returns:
            New builder instance with quick tap term set

        Examples:
            >>> builder = builder.quick_tap(125)
        """
        return self._copy_with(quick_tap_ms=ms)

    def flavor(self, flavor_type: str) -> Self:
        """Set hold-tap flavor - returns new instance.

        Args:
            flavor_type: Flavor type ("tap-preferred", "hold-preferred", "balanced", "tap-unless-interrupted")

        Returns:
            New builder instance with flavor set

        Raises:
            ValueError: If flavor type is invalid

        Examples:
            >>> builder = builder.flavor("balanced")
        """
        valid_flavors = [
            "tap-preferred",
            "hold-preferred",
            "balanced",
            "tap-unless-interrupted",
        ]
        if flavor_type not in valid_flavors:
            raise ValueError(
                f"Invalid flavor: {flavor_type}. Must be one of {valid_flavors}"
            )
        return self._copy_with(flavor=flavor_type)

    def positions(self, key_positions: list[int] | tuple[int, ...]) -> Self:
        """Set hold trigger key positions - returns new instance.

        Args:
            key_positions: List or tuple of key positions for hold trigger

        Returns:
            New builder instance with positions set

        Examples:
            >>> # Left hand positions for right hand mod
            >>> builder = builder.positions([0, 1, 2, 3, 4, 10, 11, 12, 13, 14])
        """
        positions_tuple = (
            tuple(key_positions) if isinstance(key_positions, list) else key_positions
        )
        return self._copy_with(hold_trigger_key_positions=positions_tuple)

    def retro_tap(self, enabled: bool = True) -> Self:
        """Enable/disable retro tap - returns new instance.

        Args:
            enabled: Whether to enable retro tap

        Returns:
            New builder instance with retro tap configured

        Examples:
            >>> builder = builder.retro_tap(True)
        """
        return self._copy_with(retro_tap=enabled)

    def hold_trigger_on_release(self, enabled: bool = True) -> Self:
        """Enable/disable hold trigger on release - returns new instance.

        Args:
            enabled: Whether to trigger on release

        Returns:
            New builder instance with hold trigger configured

        Examples:
            >>> builder = builder.hold_trigger_on_release(True)
        """
        return self._copy_with(hold_trigger_on_release=enabled)

    def require_prior_idle(self, ms: int) -> Self:
        """Set required prior idle time - returns new instance.

        Args:
            ms: Required idle time in milliseconds

        Returns:
            New builder instance with idle time set

        Examples:
            >>> builder = builder.require_prior_idle(150)
        """
        return self._copy_with(require_prior_idle_ms=ms)

    def tap_behavior(self, behavior: str) -> Self:
        """Override tap behavior - returns new instance.

        Args:
            behavior: Tap behavior override

        Returns:
            New builder instance with tap behavior set

        Examples:
            >>> builder = builder.tap_behavior("&kp")
        """
        return self._copy_with(tap_behavior=behavior)

    def hold_behavior(self, behavior: str) -> Self:
        """Override hold behavior - returns new instance.

        Args:
            behavior: Hold behavior override

        Returns:
            New builder instance with hold behavior set

        Examples:
            >>> builder = builder.hold_behavior("&mo")
        """
        return self._copy_with(hold_behavior=behavior)

    def build(self) -> HoldTapBehavior:
        """Build the final HoldTapBehavior instance.

        Returns:
            Constructed HoldTapBehavior

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        if len(self._bindings) != 2:
            raise ValueError(
                f"Hold-tap behavior requires exactly 2 bindings, found {len(self._bindings)}"
            )

        # Build the behavior
        return HoldTapBehavior(
            name=self._name,
            description=self._description or "",
            bindings=list(self._bindings),
            tappingTermMs=self._tapping_term_ms,
            quickTapMs=self._quick_tap_ms,
            flavor=self._flavor,
            holdTriggerOnRelease=self._hold_trigger_on_release,
            requirePriorIdleMs=self._require_prior_idle_ms,
            holdTriggerKeyPositions=list(self._hold_trigger_key_positions)
            if self._hold_trigger_key_positions
            else None,
            retroTap=self._retro_tap,
            tapBehavior=self._tap_behavior,
            holdBehavior=self._hold_behavior,
        )

    def __repr__(self) -> str:
        """Useful representation for debugging.

        Returns:
            String representation of builder state
        """
        return (
            f"BehaviorBuilder(name='{self._name}', "
            f"bindings={len(self._bindings)}, "
            f"flavor='{self._flavor or 'none'}', "
            f"positions={len(self._hold_trigger_key_positions)})"
        )
