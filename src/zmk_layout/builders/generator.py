"""Fluent builders for ZMK generation with immutable pattern and thread safety."""

from typing import TYPE_CHECKING, Any, Self

from zmk_layout.models.behaviors import (
    ComboBehavior,
    HoldTapBehavior,
    MacroBehavior,
    TapDanceBehavior,
)

if TYPE_CHECKING:
    from zmk_layout.generators.zmk_generator import ZMKGenerator
    from zmk_layout.models.metadata import LayoutData

    # Type aliases for external dependencies
    KeyboardProfile = Any


class ZMKGeneratorBuilder:
    """Fluent builder for ZMK file generation with immutable pattern.

    This builder provides a fluent interface for configuring and executing
    ZMK file generation. Each method returns a new instance with updated state.

    Examples:
        >>> builder = ZMKGeneratorBuilder(generator)
        >>> result = (builder
        ...     .with_profile(keyboard_profile)
        ...     .with_layout(layout_data)
        ...     .add_behavior(hold_tap_behavior)
        ...     .add_combo(combo_behavior)
        ...     .generate())
    """

    __slots__ = (
        "_generator",
        "_profile",
        "_layout_data",
        "_behaviors",
        "_combos",
        "_macros",
        "_tap_dances",
        "_options",
        "__weakref__",
    )

    def __init__(
        self,
        generator: "ZMKGenerator",
        profile: "KeyboardProfile | None" = None,
        layout_data: "LayoutData | None" = None,
        behaviors: tuple[HoldTapBehavior, ...] | None = None,
        combos: tuple[ComboBehavior, ...] | None = None,
        macros: tuple[MacroBehavior, ...] | None = None,
        tap_dances: tuple[TapDanceBehavior, ...] | None = None,
        options: dict[str, Any] | None = None,
    ) -> None:
        """Initialize builder with generator and optional state.

        Args:
            generator: The ZMK generator instance to use
            profile: Optional keyboard profile
            layout_data: Optional layout data
            behaviors: Immutable tuple of hold-tap behaviors
            combos: Immutable tuple of combo behaviors
            macros: Immutable tuple of macro behaviors
            tap_dances: Immutable tuple of tap-dance behaviors
            options: Generation options
        """
        self._generator = generator
        self._profile: KeyboardProfile | None = profile
        self._layout_data: LayoutData | None = layout_data
        self._behaviors: tuple[HoldTapBehavior, ...] = behaviors or ()
        self._combos: tuple[ComboBehavior, ...] = combos or ()
        self._macros: tuple[MacroBehavior, ...] = macros or ()
        self._tap_dances: tuple[TapDanceBehavior, ...] = tap_dances or ()
        self._options: dict[str, Any] = options or {}

    def _copy_with(self, **updates: Any) -> Self:
        """Create new instance with updated values (immutable pattern).

        Args:
            **updates: Fields to update in the new instance

        Returns:
            New ZMKGeneratorBuilder instance with updated state
        """
        return self.__class__(
            generator=self._generator,
            profile=updates.get("profile", self._profile),
            layout_data=updates.get("layout_data", self._layout_data),
            behaviors=updates.get("behaviors", self._behaviors),
            combos=updates.get("combos", self._combos),
            macros=updates.get("macros", self._macros),
            tap_dances=updates.get("tap_dances", self._tap_dances),
            options=updates.get("options", self._options),
        )

    def with_profile(self, profile: "KeyboardProfile") -> Self:
        """Set keyboard profile - returns new instance.

        Args:
            profile: Keyboard profile containing hardware configuration

        Returns:
            New builder instance with profile set

        Examples:
            >>> builder = ZMKGeneratorBuilder(generator).with_profile(corne_profile)
        """
        return self._copy_with(profile=profile)

    def with_layout(self, layout_data: "LayoutData") -> Self:
        """Set layout data - returns new instance.

        Args:
            layout_data: Layout data containing layers and bindings

        Returns:
            New builder instance with layout data set

        Examples:
            >>> builder = ZMKGeneratorBuilder(generator).with_layout(my_layout)
        """
        return self._copy_with(layout_data=layout_data)

    def add_behavior(self, behavior: HoldTapBehavior) -> Self:
        """Add hold-tap behavior - returns new instance.

        Args:
            behavior: Hold-tap behavior to add

        Returns:
            New builder instance with behavior added

        Examples:
            >>> builder = builder.add_behavior(home_row_mod)
        """
        return self._copy_with(behaviors=self._behaviors + (behavior,))

    def add_combo(self, combo: ComboBehavior) -> Self:
        """Add combo behavior - returns new instance.

        Args:
            combo: Combo behavior to add

        Returns:
            New builder instance with combo added

        Examples:
            >>> builder = builder.add_combo(copy_combo)
        """
        return self._copy_with(combos=self._combos + (combo,))

    def add_macro(self, macro: MacroBehavior) -> Self:
        """Add macro behavior - returns new instance.

        Args:
            macro: Macro behavior to add

        Returns:
            New builder instance with macro added

        Examples:
            >>> builder = builder.add_macro(vim_save_macro)
        """
        return self._copy_with(macros=self._macros + (macro,))

    def add_tap_dance(self, tap_dance: TapDanceBehavior) -> Self:
        """Add tap-dance behavior - returns new instance.

        Args:
            tap_dance: Tap-dance behavior to add

        Returns:
            New builder instance with tap-dance added

        Examples:
            >>> builder = builder.add_tap_dance(td_caps)
        """
        return self._copy_with(tap_dances=self._tap_dances + (tap_dance,))

    def with_options(self, **options: Any) -> Self:
        """Set generation options - returns new instance.

        Args:
            **options: Generation options (e.g., format_style, include_comments)

        Returns:
            New builder instance with options updated

        Examples:
            >>> builder = builder.with_options(
            ...     format_style="grid",
            ...     include_comments=True,
            ...     max_columns=12
            ... )
        """
        new_options = {**self._options, **options}
        return self._copy_with(options=new_options)

    def generate_behaviors_dtsi(self) -> str:
        """Generate behaviors DTSI content.

        Returns:
            Generated DTSI content for behaviors

        Raises:
            ValueError: If profile is not set
        """
        if not self._profile:
            raise ValueError("Profile must be set before generating behaviors DTSI")

        return self._generator.generate_behaviors_dtsi(
            profile=self._profile,
            hold_taps_data=list(self._behaviors),
        )

    def generate_combos_dtsi(self, layer_names: list[str] | None = None) -> str:
        """Generate combos DTSI content.

        Args:
            layer_names: Optional list of layer names for validation

        Returns:
            Generated DTSI content for combos

        Raises:
            ValueError: If profile is not set
        """
        if not self._profile:
            raise ValueError("Profile must be set before generating combos DTSI")

        # Default layer names if not provided
        if layer_names is None:
            if self._layout_data and hasattr(self._layout_data, "layer_names"):
                layer_names = list(self._layout_data.layer_names)
            else:
                # Generate default layer names based on number of layers
                if self._layout_data and hasattr(self._layout_data, "layers"):
                    layer_names = [f"layer_{i}" for i in range(len(self._layout_data.layers))]
                else:
                    layer_names = []

        return self._generator.generate_combos_dtsi(
            profile=self._profile,
            combos_data=list(self._combos),
            layer_names=layer_names,
        )

    def generate_macros_dtsi(self) -> str:
        """Generate macros DTSI content.

        Returns:
            Generated DTSI content for macros

        Raises:
            ValueError: If profile is not set
        """
        if not self._profile:
            raise ValueError("Profile must be set before generating macros DTSI")

        return self._generator.generate_macros_dtsi(
            profile=self._profile,
            macros_data=list(self._macros),
        )

    def generate_keymap_node(self) -> str:
        """Generate keymap node content.

        Returns:
            Generated keymap node content

        Raises:
            ValueError: If required data is not set
        """
        if not self._profile:
            raise ValueError("Profile must be set before generating keymap")
        if not self._layout_data:
            raise ValueError("Layout data must be set before generating keymap")

        # Extract layer names and bindings from layout data
        layer_names = []
        layers_data = []

        if hasattr(self._layout_data, "layer_names"):
            layer_names = list(self._layout_data.layer_names)
        elif hasattr(self._layout_data, "layers"):
            # Generate default layer names
            layer_names = [f"layer_{i}" for i in range(len(self._layout_data.layers))]

        if hasattr(self._layout_data, "layers"):
            layers_data = list(self._layout_data.layers)

        return self._generator.generate_keymap_node(
            profile=self._profile,
            layer_names=layer_names,
            layers_data=layers_data,
        )

    def generate_all(self) -> dict[str, str]:
        """Generate all ZMK files.

        Returns:
            Dictionary mapping file types to generated content

        Raises:
            ValueError: If required data is not set
        """
        if not self._profile:
            raise ValueError("Profile must be set before generating files")
        if not self._layout_data:
            raise ValueError("Layout data must be set before generating files")

        # Get layer names for combo generation
        layer_names = []
        if hasattr(self._layout_data, "layer_names"):
            layer_names = list(self._layout_data.layer_names)
        elif hasattr(self._layout_data, "layers"):
            layer_names = [f"layer_{i}" for i in range(len(self._layout_data.layers))]

        return {
            "keymap_node": self.generate_keymap_node(),
            "behaviors": self.generate_behaviors_dtsi() if self._behaviors else "",
            "combos": self.generate_combos_dtsi(layer_names) if self._combos else "",
            "macros": self.generate_macros_dtsi() if self._macros else "",
        }

    def __repr__(self) -> str:
        """Useful representation for debugging.

        Returns:
            String representation of builder state
        """
        return (
            f"ZMKGeneratorBuilder("
            f"profile={'set' if self._profile else 'none'}, "
            f"layout={'set' if self._layout_data else 'none'}, "
            f"behaviors={len(self._behaviors)}, "
            f"combos={len(self._combos)}, "
            f"macros={len(self._macros)}, "
            f"tap_dances={len(self._tap_dances)})"
        )
