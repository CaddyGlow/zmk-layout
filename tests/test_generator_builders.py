"""Tests for ZMK generator fluent builders."""

from unittest.mock import MagicMock

import pytest

from zmk_layout.builders import (
    BehaviorBuilder,
    ComboBuilder,
    MacroBuilder,
    ZMKGeneratorBuilder,
)
from zmk_layout.models.behaviors import ComboBehavior, HoldTapBehavior, MacroBehavior
from zmk_layout.models.core import LayoutBinding


class TestBehaviorBuilder:
    """Test suite for BehaviorBuilder."""

    def test_simple_behavior(self) -> None:
        """Test creating a simple hold-tap behavior."""
        behavior = (
            BehaviorBuilder("hm_l")
            .description("Left hand home row mod")
            .bindings("&kp", "&kp")
            .tapping_term(200)
            .build()
        )

        assert isinstance(behavior, HoldTapBehavior)
        assert behavior.name == "hm_l"
        assert behavior.description == "Left hand home row mod"
        assert behavior.bindings == ["&kp", "&kp"]
        assert behavior.tapping_term_ms == 200

    def test_complete_behavior(self) -> None:
        """Test creating a behavior with all options."""
        behavior = (
            BehaviorBuilder("hrm_r")
            .description("Right hand home row mod")
            .bindings("&kp", "&kp")
            .tapping_term(175)
            .quick_tap(125)
            .flavor("balanced")
            .positions([0, 1, 2, 3, 4])  # Left hand positions
            .retro_tap(True)
            .hold_trigger_on_release(False)
            .require_prior_idle(150)
            .tap_behavior("&custom_tap")
            .hold_behavior("&custom_hold")
            .build()
        )

        assert behavior.name == "hrm_r"
        assert behavior.tapping_term_ms == 175
        assert behavior.quick_tap_ms == 125
        assert behavior.flavor == "balanced"
        assert behavior.hold_trigger_key_positions == [0, 1, 2, 3, 4]
        assert behavior.retro_tap is True
        assert behavior.hold_trigger_on_release is False
        assert behavior.require_prior_idle_ms == 150
        assert behavior.tap_behavior == "&custom_tap"
        assert behavior.hold_behavior == "&custom_hold"

    def test_invalid_flavor(self) -> None:
        """Test that invalid flavor raises error."""
        with pytest.raises(ValueError, match="Invalid flavor"):
            BehaviorBuilder("test").flavor("invalid-flavor")

    def test_missing_bindings(self) -> None:
        """Test that missing bindings raises error on build."""
        with pytest.raises(ValueError, match="exactly 2 bindings"):
            BehaviorBuilder("test").build()

    def test_immutability(self) -> None:
        """Test that builder methods return new instances."""
        builder1 = BehaviorBuilder("test")
        builder2 = builder1.description("Test description")
        builder3 = builder2.tapping_term(200)

        assert builder1 is not builder2
        assert builder2 is not builder3

        # Original builder should be unchanged
        assert builder1._description is None
        assert builder1._tapping_term_ms is None

        # Later builders should have updated values
        assert builder2._description == "Test description"
        assert builder3._tapping_term_ms == 200


class TestComboBuilder:
    """Test suite for ComboBuilder."""

    def test_simple_combo(self) -> None:
        """Test creating a simple combo."""
        combo = (
            ComboBuilder("copy")
            .description("Copy shortcut")
            .positions([12, 13])
            .binding("&kp LC(C)")
            .timeout(50)
            .build()
        )

        assert isinstance(combo, ComboBehavior)
        assert combo.name == "copy"
        assert combo.description == "Copy shortcut"
        assert combo.key_positions == [12, 13]
        assert combo.binding.to_str() == "&kp LC(C)"
        assert combo.timeout_ms == 50

    def test_combo_with_layers(self) -> None:
        """Test creating a combo limited to specific layers."""
        combo = ComboBuilder("paste").positions([13, 14]).binding("&kp LC(V)").layers([0, 1, 2]).build()

        assert combo.layers == [0, 1, 2]

    def test_combo_with_binding_object(self) -> None:
        """Test creating combo with LayoutBinding object."""
        binding = LayoutBinding.from_str("&kp ESC")
        combo = ComboBuilder("escape").positions([0, 1]).binding(binding).build()

        assert combo.binding.to_str() == "&kp ESC"

    def test_missing_positions(self) -> None:
        """Test that missing positions raises error."""
        with pytest.raises(ValueError, match="at least one key position"):
            ComboBuilder("test").binding("&kp A").build()

    def test_missing_binding(self) -> None:
        """Test that missing binding raises error."""
        with pytest.raises(ValueError, match="must have a binding"):
            ComboBuilder("test").positions([0, 1]).build()

    def test_behavior_override(self) -> None:
        """Test setting behavior override."""
        combo = ComboBuilder("custom").positions([5, 6]).binding("&kp A").behavior_override("&custom_combo").build()

        assert combo.behavior == "&custom_combo"


class TestMacroBuilder:
    """Test suite for MacroBuilder."""

    def test_simple_macro(self) -> None:
        """Test creating a simple macro."""
        macro = (
            MacroBuilder("hello")
            .description("Type hello")
            .tap("&kp H")
            .tap("&kp E")
            .tap("&kp L")
            .tap("&kp L")
            .tap("&kp O")
            .build()
        )

        assert isinstance(macro, MacroBehavior)
        assert macro.name == "hello"
        assert macro.description == "Type hello"
        assert len(macro.bindings) == 5
        assert all(b.value == "&kp" for b in macro.bindings)

    def test_macro_with_timing(self) -> None:
        """Test creating macro with timing settings."""
        macro = (
            MacroBuilder("vim_save")
            .wait(10)
            .tap_time(5)
            .tap("&kp ESC")
            .wait_action(100)
            .tap("&kp COLON")
            .tap("&kp W")
            .tap("&kp ENTER")
            .build()
        )

        assert macro.wait_ms == 10
        assert macro.tap_ms == 5
        assert len(macro.bindings) == 5  # 4 taps + 1 wait action

    def test_macro_sequence(self) -> None:
        """Test adding sequence of actions."""
        macro = MacroBuilder("word").sequence("&kp W", "&kp O", "&kp R", "&kp D").build()

        assert len(macro.bindings) == 4

    def test_macro_with_params(self) -> None:
        """Test macro with parameters."""
        macro = MacroBuilder("param_macro").params("param1", 42).tap("&kp A").build()

        assert macro.params == ["param1", 42]

    def test_too_many_params(self) -> None:
        """Test that too many parameters raises error."""
        with pytest.raises(ValueError, match="cannot have more than 2 parameters"):
            MacroBuilder("test").params("p1", "p2", "p3").build()

    def test_press_release_actions(self) -> None:
        """Test press and release actions."""
        macro = MacroBuilder("shift_word").press("&kp LSHIFT").tap("&kp H").tap("&kp I").release("&kp LSHIFT").build()

        assert len(macro.bindings) == 4
        assert macro.bindings[0].value == "&macro_press"
        assert macro.bindings[3].value == "&macro_release"


class TestZMKGeneratorBuilder:
    """Test suite for ZMKGeneratorBuilder."""

    def test_simple_generation(self) -> None:
        """Test basic generator configuration."""
        generator = MagicMock()
        generator.generate_behaviors_dtsi.return_value = "behaviors {}"
        generator.generate_combos_dtsi.return_value = "combos {}"
        generator.generate_keymap_node.return_value = "keymap {}"

        profile = MagicMock()
        layout_data = MagicMock()

        builder = ZMKGeneratorBuilder(generator).with_profile(profile).with_layout(layout_data)

        # Test behaviors generation
        behaviors_dtsi = builder.generate_behaviors_dtsi()
        assert behaviors_dtsi == "behaviors {}"
        generator.generate_behaviors_dtsi.assert_called_once_with(
            profile=profile,
            hold_taps_data=[],
        )

        # Test keymap generation
        keymap = builder.generate_keymap_node()
        assert keymap == "keymap {}"

    def test_adding_behaviors(self) -> None:
        """Test adding multiple behaviors."""
        generator = MagicMock()
        profile = MagicMock()

        behavior1 = BehaviorBuilder("hm_l").bindings("&kp", "&kp").build()
        behavior2 = BehaviorBuilder("hm_r").bindings("&kp", "&kp").build()

        builder = ZMKGeneratorBuilder(generator).with_profile(profile).add_behavior(behavior1).add_behavior(behavior2)

        assert len(builder._behaviors) == 2
        assert builder._behaviors[0].name == "hm_l"
        assert builder._behaviors[1].name == "hm_r"

    def test_adding_combos(self) -> None:
        """Test adding combos."""
        generator = MagicMock()

        combo = ComboBuilder("copy").positions([12, 13]).binding("&kp LC(C)").build()

        builder = ZMKGeneratorBuilder(generator).add_combo(combo)

        assert len(builder._combos) == 1
        assert builder._combos[0].name == "copy"

    def test_adding_macros(self) -> None:
        """Test adding macros."""
        generator = MagicMock()

        macro = MacroBuilder("hello").tap("&kp H").build()

        builder = ZMKGeneratorBuilder(generator).add_macro(macro)

        assert len(builder._macros) == 1
        assert builder._macros[0].name == "hello"

    def test_with_options(self) -> None:
        """Test setting generation options."""
        generator = MagicMock()

        builder = ZMKGeneratorBuilder(generator).with_options(format_style="grid", include_comments=True)

        assert builder._options["format_style"] == "grid"
        assert builder._options["include_comments"] is True

    def test_generate_all(self) -> None:
        """Test generating all files."""
        generator = MagicMock()
        generator.generate_keymap_node.return_value = "keymap content"
        generator.generate_behaviors_dtsi.return_value = "behaviors content"
        generator.generate_combos_dtsi.return_value = "combos content"
        generator.generate_macros_dtsi.return_value = "macros content"

        profile = MagicMock()
        layout_data = MagicMock()

        behavior = BehaviorBuilder("test").bindings("&kp", "&kp").build()
        combo = ComboBuilder("test").positions([0]).binding("&kp A").build()
        macro = MacroBuilder("test").tap("&kp A").build()

        builder = (
            ZMKGeneratorBuilder(generator)
            .with_profile(profile)
            .with_layout(layout_data)
            .add_behavior(behavior)
            .add_combo(combo)
            .add_macro(macro)
        )

        result = builder.generate_all()

        assert "keymap_node" in result
        assert "behaviors" in result
        assert "combos" in result
        assert "macros" in result
        assert result["keymap_node"] == "keymap content"
        assert result["behaviors"] == "behaviors content"

    def test_missing_profile_error(self) -> None:
        """Test that missing profile raises error."""
        generator = MagicMock()
        builder = ZMKGeneratorBuilder(generator)

        with pytest.raises(ValueError, match="Profile must be set"):
            builder.generate_behaviors_dtsi()

    def test_missing_layout_error(self) -> None:
        """Test that missing layout data raises error."""
        generator = MagicMock()
        profile = MagicMock()

        builder = ZMKGeneratorBuilder(generator).with_profile(profile)

        with pytest.raises(ValueError, match="Layout data must be set"):
            builder.generate_keymap_node()

    def test_immutability(self) -> None:
        """Test that builder methods return new instances."""
        generator = MagicMock()
        builder1 = ZMKGeneratorBuilder(generator)
        builder2 = builder1.with_profile(MagicMock())
        builder3 = builder2.with_layout(MagicMock())

        assert builder1 is not builder2
        assert builder2 is not builder3

        # Original should be unchanged
        assert builder1._profile is None
        assert builder1._layout_data is None


class TestBuilderChaining:
    """Test complex chaining scenarios."""

    def test_complex_workflow(self) -> None:
        """Test a complete workflow with all builders."""
        generator = MagicMock()
        generator.generate_all.return_value = {"test": "content"}

        profile = MagicMock()
        layout_data = MagicMock()

        # Create behaviors
        hm_l = (
            BehaviorBuilder("hm_l")
            .description("Left home row mod")
            .bindings("&kp", "&kp")
            .tapping_term(175)
            .flavor("balanced")
            .positions([5, 6, 7, 8, 9])
            .build()
        )

        hm_r = (
            BehaviorBuilder("hm_r")
            .description("Right home row mod")
            .bindings("&kp", "&kp")
            .tapping_term(175)
            .flavor("balanced")
            .positions([0, 1, 2, 3, 4])
            .build()
        )

        # Create combos
        copy_combo = (
            ComboBuilder("copy")
            .description("Copy to clipboard")
            .positions([12, 13])
            .binding("&kp LC(C)")
            .timeout(50)
            .layers([0, 1])
            .build()
        )

        # Create macro
        vim_save = (
            MacroBuilder("vim_save")
            .description("Save in vim")
            .tap("&kp ESC")
            .wait_action(10)
            .sequence("&kp COLON", "&kp W", "&kp ENTER")
            .build()
        )

        # Build complete generation
        result = (
            ZMKGeneratorBuilder(generator)
            .with_profile(profile)
            .with_layout(layout_data)
            .add_behavior(hm_l)
            .add_behavior(hm_r)
            .add_combo(copy_combo)
            .add_macro(vim_save)
            .with_options(
                format_style="grid",
                include_comments=True,
                max_columns=12,
            )
        )

        # Verify state
        assert len(result._behaviors) == 2
        assert len(result._combos) == 1
        assert len(result._macros) == 1
        assert result._options["format_style"] == "grid"
        assert result._options["include_comments"] is True
        assert result._options["max_columns"] == 12
