"""Behavior management for fluent API operations."""

from typing import TYPE_CHECKING, Any

from zmk_layout.models.behaviors import (
    ComboBehavior,
    HoldTapBehavior,
    MacroBehavior,
    TapDanceBehavior,
)
from zmk_layout.models.core import LayoutBinding


if TYPE_CHECKING:
    from zmk_layout.models.metadata import LayoutData
    from zmk_layout.providers import LayoutProviders


class BehaviorManager:
    """Manager for behavior operations with fluent interface."""

    def __init__(self, layout_data: "LayoutData", providers: "LayoutProviders") -> None:
        """Initialize behavior manager.

        Args:
            layout_data: Layout data to manage
            providers: Provider dependencies
        """
        self._data = layout_data
        self._providers = providers

    def add_hold_tap(
        self,
        name: str,
        tap: str,
        hold: str,
        tapping_term_ms: int | None = None,
        flavor: str | None = None,
        **kwargs: Any,
    ) -> "BehaviorManager":
        """Add hold-tap behavior and return self for chaining.

        Args:
            name: Behavior name (with or without & prefix)
            tap: Tap binding
            hold: Hold binding
            tapping_term_ms: Tapping term in milliseconds
            flavor: Hold-tap flavor
            **kwargs: Additional hold-tap parameters

        Returns:
            Self for method chaining
        """
        # Ensure name has & prefix
        if not name.startswith("&"):
            name = f"&{name}"

        # Create hold-tap behavior
        hold_tap = HoldTapBehavior(
            name=name,
            bindings=[hold, tap],  # Hold first, then tap
            tappingTermMs=tapping_term_ms,
            flavor=flavor,
            **kwargs,
        )

        # Initialize hold_taps list if needed
        if self._data.hold_taps is None:
            self._data.hold_taps = []

        # Remove existing behavior with same name
        self._data.hold_taps = [ht for ht in self._data.hold_taps if ht.name != name]

        # Add new behavior
        self._data.hold_taps.append(hold_tap)

        return self

    def add_combo(
        self,
        name: str,
        keys: list[int],
        binding: str | LayoutBinding,
        timeout_ms: int | None = None,
        layers: list[int] | None = None,
        **kwargs: Any,
    ) -> "BehaviorManager":
        """Add combo behavior and return self for chaining.

        Args:
            name: Combo name
            keys: List of key positions
            binding: Binding to trigger
            timeout_ms: Combo timeout in milliseconds
            layers: Layers where combo is active (None = all layers)
            **kwargs: Additional combo parameters

        Returns:
            Self for method chaining
        """
        # Convert string binding to LayoutBinding if needed
        layout_binding = (
            LayoutBinding.from_str(binding) if isinstance(binding, str) else binding
        )

        # Create combo behavior
        combo = ComboBehavior(
            name=name,
            keyPositions=keys,
            binding=layout_binding,
            timeoutMs=timeout_ms,
            layers=layers or [-1],  # -1 means all layers
            **kwargs,
        )

        # Initialize combos list if needed
        if self._data.combos is None:
            self._data.combos = []

        # Remove existing combo with same name
        self._data.combos = [c for c in self._data.combos if c.name != name]

        # Add new combo
        self._data.combos.append(combo)

        return self

    def add_macro(
        self,
        name: str,
        sequence: list[str],
        wait_ms: int | None = None,
        tap_ms: int | None = None,
        **kwargs: Any,
    ) -> "BehaviorManager":
        """Add macro behavior and return self for chaining.

        Args:
            name: Macro name (with or without & prefix)
            sequence: List of macro bindings
            wait_ms: Wait time between macro steps
            tap_ms: Tap duration for macro steps
            **kwargs: Additional macro parameters

        Returns:
            Self for method chaining
        """
        # Ensure name has & prefix
        if not name.startswith("&"):
            name = f"&{name}"

        # Convert string bindings to LayoutBinding objects
        layout_bindings = [LayoutBinding.from_str(binding) for binding in sequence]

        # Create macro behavior
        macro = MacroBehavior(
            name=name, bindings=layout_bindings, waitMs=wait_ms, tapMs=tap_ms, **kwargs
        )

        # Initialize macros list if needed
        if self._data.macros is None:
            self._data.macros = []

        # Remove existing macro with same name
        self._data.macros = [m for m in self._data.macros if m.name != name]

        # Add new macro
        self._data.macros.append(macro)

        return self

    def add_tap_dance(
        self,
        name: str,
        bindings: list[str],
        tapping_term_ms: int | None = None,
        **kwargs: Any,
    ) -> "BehaviorManager":
        """Add tap dance behavior and return self for chaining.

        Args:
            name: Tap dance name (with or without & prefix)
            bindings: List of tap dance bindings
            tapping_term_ms: Tapping term in milliseconds
            **kwargs: Additional tap dance parameters

        Returns:
            Self for method chaining
        """
        # Ensure name has & prefix
        if not name.startswith("&"):
            name = f"&{name}"

        # Convert string bindings to LayoutBinding objects
        layout_bindings = [LayoutBinding.from_str(binding) for binding in bindings]

        # Create tap dance behavior
        tap_dance = TapDanceBehavior(
            name=name, bindings=layout_bindings, tappingTermMs=tapping_term_ms, **kwargs
        )

        # Initialize tap_dances list if needed
        if self._data.tap_dances is None:
            self._data.tap_dances = []

        # Remove existing tap dance with same name
        self._data.tap_dances = [td for td in self._data.tap_dances if td.name != name]

        # Add new tap dance
        self._data.tap_dances.append(tap_dance)

        return self

    def remove_hold_tap(self, name: str) -> "BehaviorManager":
        """Remove hold-tap behavior and return self for chaining.

        Args:
            name: Behavior name to remove

        Returns:
            Self for method chaining
        """
        if self._data.hold_taps is not None:
            # Ensure name has & prefix for comparison
            if not name.startswith("&"):
                name = f"&{name}"
            self._data.hold_taps = [
                ht for ht in self._data.hold_taps if ht.name != name
            ]

        return self

    def remove_combo(self, name: str) -> "BehaviorManager":
        """Remove combo behavior and return self for chaining.

        Args:
            name: Combo name to remove

        Returns:
            Self for method chaining
        """
        if self._data.combos is not None:
            self._data.combos = [c for c in self._data.combos if c.name != name]

        return self

    def remove_macro(self, name: str) -> "BehaviorManager":
        """Remove macro behavior and return self for chaining.

        Args:
            name: Macro name to remove

        Returns:
            Self for method chaining
        """
        if self._data.macros is not None:
            # Ensure name has & prefix for comparison
            if not name.startswith("&"):
                name = f"&{name}"
            self._data.macros = [m for m in self._data.macros if m.name != name]

        return self

    def remove_tap_dance(self, name: str) -> "BehaviorManager":
        """Remove tap dance behavior and return self for chaining.

        Args:
            name: Tap dance name to remove

        Returns:
            Self for method chaining
        """
        if self._data.tap_dances is not None:
            # Ensure name has & prefix for comparison
            if not name.startswith("&"):
                name = f"&{name}"
            self._data.tap_dances = [
                td for td in self._data.tap_dances if td.name != name
            ]

        return self

    def clear_all(self) -> "BehaviorManager":
        """Clear all behaviors and return self for chaining.

        Returns:
            Self for method chaining
        """
        if self._data.hold_taps is not None:
            self._data.hold_taps.clear()
        if self._data.combos is not None:
            self._data.combos.clear()
        if self._data.macros is not None:
            self._data.macros.clear()
        if self._data.tap_dances is not None:
            self._data.tap_dances.clear()

        return self

    @property
    def hold_tap_count(self) -> int:
        """Get number of hold-tap behaviors."""
        return len(self._data.hold_taps) if self._data.hold_taps else 0

    @property
    def combo_count(self) -> int:
        """Get number of combo behaviors."""
        return len(self._data.combos) if self._data.combos else 0

    @property
    def macro_count(self) -> int:
        """Get number of macro behaviors."""
        return len(self._data.macros) if self._data.macros else 0

    @property
    def tap_dance_count(self) -> int:
        """Get number of tap dance behaviors."""
        return len(self._data.tap_dances) if self._data.tap_dances else 0

    @property
    def total_count(self) -> int:
        """Get total number of behaviors."""
        return (
            self.hold_tap_count
            + self.combo_count
            + self.macro_count
            + self.tap_dance_count
        )

    def has_hold_tap(self, name: str) -> bool:
        """Check if hold-tap behavior exists."""
        if not self._data.hold_taps:
            return False
        if not name.startswith("&"):
            name = f"&{name}"
        return any(ht.name == name for ht in self._data.hold_taps)

    def has_combo(self, name: str) -> bool:
        """Check if combo behavior exists."""
        if not self._data.combos:
            return False
        return any(c.name == name for c in self._data.combos)

    def has_macro(self, name: str) -> bool:
        """Check if macro behavior exists."""
        if not self._data.macros:
            return False
        if not name.startswith("&"):
            name = f"&{name}"
        return any(m.name == name for m in self._data.macros)

    def has_tap_dance(self, name: str) -> bool:
        """Check if tap dance behavior exists."""
        if not self._data.tap_dances:
            return False
        if not name.startswith("&"):
            name = f"&{name}"
        return any(td.name == name for td in self._data.tap_dances)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"BehaviorManager("
            f"hold_taps={self.hold_tap_count}, "
            f"combos={self.combo_count}, "
            f"macros={self.macro_count}, "
            f"tap_dances={self.tap_dance_count})"
        )
