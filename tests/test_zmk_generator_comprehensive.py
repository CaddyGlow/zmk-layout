"""Comprehensive tests for ZMK generator functionality."""
from typing import Any, cast
from unittest.mock import Mock

import pytest

from zmk_layout.generators.zmk_generator import (
    ZMKGenerator,
    create_zmk_generator,
)
from zmk_layout.models.behaviors import (
    ComboBehavior,
    HoldTapBehavior,
    InputListener,
    InputListenerNode,
    MacroBehavior,
    TapDanceBehavior,
)
from zmk_layout.models.core import LayoutBinding, LayoutParam
from zmk_layout.models.metadata import LayoutData


def create_layout_binding(binding_str: str) -> LayoutBinding:
    """Convert string binding to LayoutBinding object."""
    parts = binding_str.split()
    if len(parts) >= 2:
        return LayoutBinding(
            value=parts[0], 
            params=[LayoutParam(value=p) for p in parts[1:]]
        )
    return LayoutBinding(value=binding_str, params=[])


def create_layout_bindings(binding_strs: list[str]) -> list[LayoutBinding]:
    """Convert list of string bindings to LayoutBinding objects."""
    return [create_layout_binding(b) for b in binding_strs]


class MockLogger:
    def __init__(self) -> None:
        self.debug_calls: list[tuple[str, dict[str, Any]]] = []
        self.error_calls: list[tuple[str, dict[str, Any]]] = []
        self.warning_calls: list[tuple[str, dict[str, Any]]] = []
        self.info_calls: list[tuple[str, dict[str, Any]]] = []
        self.exception_calls: list[tuple[str, dict[str, Any]]] = []

    def debug(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        self.debug_calls.append((message, kwargs))

    def error(self, message: str, exc_info: bool = False, **kwargs: str | int | float | bool | None) -> None:
        self.error_calls.append((message, kwargs))

    def warning(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        self.warning_calls.append((message, kwargs))

    def info(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        self.info_calls.append((message, kwargs))

    def exception(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        self.exception_calls.append((message, kwargs))



class MockConfigurationProvider:
    def __init__(self, keyboard_config: Any | None = None) -> None:
        self.keyboard_config = keyboard_config or self._default_keyboard_config()

    def _default_keyboard_config(self) -> Any:
        patterns_mock = Mock()
        patterns_mock.layer_define = "#define {layer_name} {layer_index}"
        
        compatible_strings_mock = Mock()
        compatible_strings_mock.hold_tap = "zmk,behavior-hold-tap"
        compatible_strings_mock.keymap = "zmk,keymap"
        compatible_strings_mock.combos = "zmk,combos"
        compatible_strings_mock.macro = "zmk,behavior-macro"
        compatible_strings_mock.macro_one_param = "zmk,behavior-macro-one-param"
        compatible_strings_mock.macro_two_param = "zmk,behavior-macro-two-param"
        
        zmk_mock = Mock()
        zmk_mock.validation_limits = Mock(required_holdtap_bindings=2)
        zmk_mock.compatible_strings = compatible_strings_mock
        zmk_mock.hold_tap_flavors = ["balanced", "tap-preferred", "hold-preferred"]
        zmk_mock.patterns = patterns_mock
        
        return Mock(
            key_count=10,
            zmk=zmk_mock,
        )

    def get_behavior_definitions(self) -> list[Any]:
        return []

    def get_include_files(self) -> list[str]:
        return []

    def get_validation_rules(self) -> dict[str, int | list[int] | list[str]]:
        return {}

    def get_template_context(self) -> dict[str, str | int | float | bool | None]:
        return {}

    def get_kconfig_options(self) -> dict[str, str | int | float | bool | None]:
        return {}

    def get_formatting_config(self) -> dict[str, int | list[str]]:
        return {}

    def get_search_paths(self) -> list[Any]:
        return []


class MockTemplateProvider:
    def __init__(self, render_responses: dict[str, str] | None = None) -> None:
        self.render_responses = render_responses or {}
        self.render_calls: list[tuple[str, dict[str, Any]]] = []

    def render_template(self, template_name: str, context: dict[str, Any]) -> str:
        self.render_calls.append((template_name, context))
        return self.render_responses.get(template_name, f"rendered_{template_name}")

    def render_string(self, template: str, context: dict[str, str | int | float | bool | None]) -> str:
        return template

    def has_template_syntax(self, content: str) -> bool:
        return False

    def escape_content(self, content: str) -> str:
        return content


class MockBehaviorRegistry:
    def __init__(self) -> None:
        self.registered_behaviors: list[Any] = []

    def register_behavior(self, behavior: Any) -> None:
        self.registered_behaviors.append(behavior)


class MockBehaviorFormatter:
    def __init__(self) -> None:
        self.behavior_reference_context: bool = False
        self.format_calls: list[Any] = []

    def set_behavior_reference_context(self, context: bool) -> None:
        self.behavior_reference_context = context

    def format_binding(self, binding: Any) -> str:
        self.format_calls.append(binding)
        # Format similar to the real formatter
        if isinstance(binding, str):
            return binding
        elif hasattr(binding, 'value') and hasattr(binding, 'params'):
            if binding.params:
                param_strs = [p.value if hasattr(p, 'value') else str(p) for p in binding.params]
                return f"{binding.value} {' '.join(param_strs)}"
            else:
                return str(binding.value)
        else:
            return str(binding)


class MockLayoutFormatter:
    def __init__(self) -> None:
        self.format_calls: list[Any] = []
        self.generate_calls: list[Any] = []

    def format_layer_grid(self, bindings: Any, grid_config: Any) -> str:
        self.format_calls.append((bindings, grid_config))
        return f"formatted_grid_{len(bindings)}_bindings"
    
    def generate_layer_layout(self, layer_data: Any, profile: Any = None, base_indent: str = "            ", **kwargs: Any) -> str:
        """Generate layer layout for ZMK generator compatibility."""
        self.generate_calls.append((layer_data, profile, base_indent, kwargs))
        self.format_calls.append((layer_data, profile, base_indent))
        
        # Handle both formatted_bindings and layer_data formats
        bindings = layer_data if isinstance(layer_data, list) else [str(layer_data)]
        bindings_str = " ".join(str(b) for b in bindings)
        return f"{base_indent}{bindings_str}"


@pytest.fixture
def mock_logger() -> MockLogger:
    return MockLogger()


@pytest.fixture
def mock_configuration_provider() -> MockConfigurationProvider:
    return MockConfigurationProvider()


@pytest.fixture
def mock_template_provider() -> MockTemplateProvider:
    return MockTemplateProvider()


@pytest.fixture
def mock_behavior_registry() -> MockBehaviorRegistry:
    return MockBehaviorRegistry()


@pytest.fixture
def mock_behavior_formatter() -> MockBehaviorFormatter:
    return MockBehaviorFormatter()


@pytest.fixture
def mock_layout_formatter() -> MockLayoutFormatter:
    return MockLayoutFormatter()


@pytest.fixture
def sample_keyboard_profile(mock_configuration_provider: MockConfigurationProvider) -> Any:
    profile = Mock()
    profile.keyboard_config = mock_configuration_provider.keyboard_config
    profile.keyboard_name = "test_keyboard"
    return profile


@pytest.fixture
def zmk_generator(
    mock_configuration_provider: MockConfigurationProvider,
    mock_template_provider: MockTemplateProvider,
    mock_logger: MockLogger,
) -> ZMKGenerator:
    generator = ZMKGenerator(
        configuration_provider=mock_configuration_provider,
        template_provider=mock_template_provider,
        logger=mock_logger,
    )
    # Replace real components with mocks for testing  
    generator._behavior_registry = MockBehaviorRegistry()  # type: ignore
    generator._behavior_formatter = MockBehaviorFormatter()  # type: ignore
    generator._layout_formatter = MockLayoutFormatter()  # type: ignore
    return generator


class TestZMKGeneratorLayerDefines:
    """Tests for layer defines generation."""

    def test_generate_layer_defines_basic(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test basic layer defines generation."""
        layer_names = ["base", "nav", "symbols"]
        
        result = zmk_generator.generate_layer_defines(sample_keyboard_profile, layer_names)
        
        assert "#define base 0" in result
        assert "#define nav 1" in result
        assert "#define symbols 2" in result

    def test_generate_layer_defines_name_sanitization(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test layer name sanitization in defines."""
        layer_names = ["layer-with-dashes", "layer_with_underscores", "layer with spaces"]
        
        result = zmk_generator.generate_layer_defines(sample_keyboard_profile, layer_names)
        
        assert "#define layer_with_dashes 0" in result
        assert "#define layer_with_underscores 1" in result
        assert "#define layer_with_spaces 2" in result

    def test_generate_layer_defines_empty(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test layer defines generation with empty list."""
        result = zmk_generator.generate_layer_defines(sample_keyboard_profile, [])
        
        assert result == ""

    def test_generate_layer_defines_single_layer(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test layer defines generation with single layer."""
        result = zmk_generator.generate_layer_defines(sample_keyboard_profile, ["base"])
        
        assert "#define base 0" in result
        assert result.count("#define") == 1


class TestZMKGeneratorBehaviorsDTSI:
    """Tests for behaviors DTSI generation."""

    def test_generate_behaviors_dtsi_empty(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test behaviors generation with empty list."""
        result = zmk_generator.generate_behaviors_dtsi(sample_keyboard_profile, [])
        
        assert result == ""

    def test_generate_behaviors_dtsi_valid_hold_tap(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test generation with valid hold-tap behavior."""
        hold_tap = HoldTapBehavior(
            name="custom_ht",
            description="Custom hold-tap",
            bindings=["&kp", "&mo"],
            tappingTermMs=200,
            flavor="balanced",
            quickTapMs=150,
            requirePriorIdleMs=100,
            holdTriggerKeyPositions=[1, 2, 3],
            holdTriggerOnRelease=True,
            retroTap=True,
        )
        
        result = zmk_generator.generate_behaviors_dtsi(sample_keyboard_profile, [hold_tap])
        
        assert "custom_ht: custom_ht {" in result
        assert 'compatible = "zmk,behavior-hold-tap";' in result
        assert "tapping-term-ms = <200>;" in result
        assert 'flavor = "balanced";' in result
        assert "quick-tap-ms = <150>;" in result
        assert "require-prior-idle-ms = <100>;" in result
        assert "hold-trigger-key-positions = <1 2 3>;" in result
        assert "hold-trigger-on-release;" in result
        assert "retro-tap;" in result

    def test_generate_behaviors_dtsi_missing_name(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test handling of hold-tap with missing name."""
        hold_tap = HoldTapBehavior(
            name="",  # Empty name
            bindings=["&kp", "&mo"],
            tappingTermMs=200,
        )
        
        result = zmk_generator.generate_behaviors_dtsi(sample_keyboard_profile, [hold_tap])
        
        assert result == ""
        assert any("Skipping hold-tap behavior with missing 'name'" in call[0] for call in mock_logger.warning_calls)

    def test_generate_behaviors_dtsi_wrong_binding_count(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test handling of hold-tap with wrong binding count."""
        # Create a mock hold-tap that bypasses model validation
        hold_tap = Mock()
        hold_tap.name = "bad_ht"
        hold_tap.bindings = ["&kp"]  # Only one binding, needs 2
        hold_tap.tappingTermMs = 200
        hold_tap.description = None
        hold_tap.flavor = None
        hold_tap.quick_tap_ms = None
        hold_tap.require_prior_idle_ms = None
        hold_tap.hold_trigger_on_release = None
        hold_tap.hold_trigger_key_positions = None
        hold_tap.retro_tap = None
        
        result = zmk_generator.generate_behaviors_dtsi(sample_keyboard_profile, [hold_tap])
        
        assert result == ""
        assert any("requires exactly 2 bindings" in call[0] for call in mock_logger.warning_calls)

    def test_generate_behaviors_dtsi_invalid_flavor(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test handling of invalid flavor."""
        # Create a mock hold-tap with invalid flavor
        hold_tap = Mock()
        hold_tap.name = "ht_invalid_flavor"
        hold_tap.bindings = ["&kp", "&mo"]
        hold_tap.flavor = "invalid-flavor"
        hold_tap.description = None
        hold_tap.tappingTermMs = None
        hold_tap.quick_tap_ms = None
        hold_tap.require_prior_idle_ms = None
        hold_tap.hold_trigger_on_release = None
        hold_tap.hold_trigger_key_positions = None
        hold_tap.retro_tap = None
        
        result = zmk_generator.generate_behaviors_dtsi(sample_keyboard_profile, [hold_tap])
        
        # Should generate the behavior but omit the invalid flavor
        assert "ht_invalid_flavor: ht_invalid_flavor {" in result
        assert 'flavor = "invalid-flavor";' not in result
        assert any("Invalid flavor 'invalid-flavor'" in call[0] for call in mock_logger.warning_calls)

    def test_generate_behaviors_dtsi_behavior_registry_integration(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test integration with behavior registry."""
        hold_tap = HoldTapBehavior(
            name="&custom_ht",  # With & prefix
            bindings=["&kp", "&mo"],
            description="Test behavior",
        )
        
        zmk_generator.generate_behaviors_dtsi(sample_keyboard_profile, [hold_tap])
        
        # Should register the behavior (access the generator's mock registry)
        mock_registry = cast(MockBehaviorRegistry, zmk_generator._behavior_registry)
        assert len(mock_registry.registered_behaviors) == 1
        registered = mock_registry.registered_behaviors[0]
        assert registered.code == "&custom_ht"
        assert registered.name == "&custom_ht"
        assert registered.description == "Test behavior"

    def test_generate_behaviors_dtsi_behavior_formatter_integration(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test integration with behavior formatter."""
        hold_tap = HoldTapBehavior(
            name="formatted_ht",
            bindings=["&kp", "&mo"],
        )
        
        zmk_generator.generate_behaviors_dtsi(sample_keyboard_profile, [hold_tap])
        
        # Should use behavior formatter context (access the generator's mock formatter)
        mock_formatter = cast(MockBehaviorFormatter, zmk_generator._behavior_formatter)
        assert not mock_formatter.behavior_reference_context  # Should be reset after use

    def test_generate_behaviors_dtsi_fallback_bindings(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test fallback behavior when formatter is not available."""
        zmk_generator._behavior_formatter = None  # type: ignore
        
        hold_tap = HoldTapBehavior(
            name="fallback_ht",
            bindings=["&kp", "&mo"],
        )
        
        result = zmk_generator.generate_behaviors_dtsi(sample_keyboard_profile, [hold_tap])
        
        # Should still generate valid DTSI with fallback formatting
        assert "bindings = <&kp>, <&mo>;" in result


class TestZMKGeneratorTapDances:
    """Tests for tap dance generation."""

    def test_generate_tap_dances_dtsi_empty(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test tap dance generation with empty list."""
        result = zmk_generator.generate_tap_dances_dtsi(sample_keyboard_profile, [])
        
        assert result == ""

    def test_generate_tap_dances_dtsi_basic(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test basic tap dance generation."""
        tap_dance = TapDanceBehavior(
            name="test_td",
            bindings=create_layout_bindings(["&kp Q", "&kp W", "&kp E"]),
            tappingTermMs=200,
        )
        
        result = zmk_generator.generate_tap_dances_dtsi(sample_keyboard_profile, [tap_dance])
        
        assert "test_td: test_td {" in result
        assert 'compatible = "zmk,behavior-tap-dance";' in result
        assert "tapping-term-ms = <200>;" in result
        assert "bindings = <&kp Q>, <&kp W>, <&kp E>;" in result

    def test_generate_tap_dances_dtsi_missing_name(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test tap dance with missing name."""
        # Create a mock tap dance that bypasses model validation
        tap_dance = Mock()
        tap_dance.name = None  # Missing name
        tap_dance.description = None
        tap_dance.bindings = create_layout_bindings(["&kp Q", "&kp W"])
        tap_dance.tappingTermMs = None
        
        result = zmk_generator.generate_tap_dances_dtsi(sample_keyboard_profile, [tap_dance])
        
        assert result == ""
        assert any("Skipping tap-dance with missing name" in call[0] for call in mock_logger.warning_calls)

    def test_generate_tap_dances_dtsi_insufficient_bindings(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test tap dance with insufficient bindings."""
        # Create a mock tap dance with insufficient bindings
        tap_dance = Mock()
        tap_dance.name = "insufficient_td"
        tap_dance.description = None
        tap_dance.bindings = create_layout_bindings(["&kp Q"])  # Need at least 2
        tap_dance.tappingTermMs = None
        
        result = zmk_generator.generate_tap_dances_dtsi(sample_keyboard_profile, [tap_dance])
        
        assert result == ""
        assert any("requires at least 2 bindings" in call[0] for call in mock_logger.warning_calls)


class TestZMKGeneratorMacros:
    """Tests for macro generation."""

    def test_generate_macros_dtsi_empty(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test macro generation with empty list."""
        result = zmk_generator.generate_macros_dtsi(sample_keyboard_profile, [])
        
        assert result == ""

    def test_generate_macros_dtsi_basic(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test basic macro generation."""
        macro = MacroBehavior(
            name="test_macro",
            description="Test macro",
            bindings=create_layout_bindings(["&kp H", "&kp E", "&kp L", "&kp L", "&kp O"]),
            waitMs=10,
            tapMs=5,
        )
        
        result = zmk_generator.generate_macros_dtsi(sample_keyboard_profile, [macro])
        
        assert "test_macro: test_macro {" in result
        assert 'compatible = "zmk,behavior-macro";' in result
        assert "wait-ms = <10>;" in result
        assert "tap-ms = <5>;" in result
        # Check that all bindings are present in the output
        assert "<&kp H>" in result
        assert "<&kp E>" in result
        assert "<&kp L>" in result
        assert "<&kp O>" in result

    def test_generate_macros_dtsi_missing_name(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test macro with missing name."""
        macro = MacroBehavior(
            name="",
            bindings=create_layout_bindings(["&kp H", "&kp I"]),
        )
        
        result = zmk_generator.generate_macros_dtsi(sample_keyboard_profile, [macro])
        
        assert result == ""
        assert any("Skipping macro with missing name" in call[0] for call in mock_logger.warning_calls)

    def test_generate_macros_dtsi_empty_bindings(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test macro with empty bindings."""
        macro = MacroBehavior(
            name="empty_macro",
            bindings=[],
        )
        
        result = zmk_generator.generate_macros_dtsi(sample_keyboard_profile, [macro])
        
        assert result == ""
        assert any("has no bindings" in call[0] for call in mock_logger.warning_calls)


class TestZMKGeneratorCombos:
    """Tests for combo generation."""

    def test_generate_combos_dtsi_empty(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test combo generation with empty list."""
        result = zmk_generator.generate_combos_dtsi(sample_keyboard_profile, [], [])
        
        assert result == ""

    def test_generate_combos_dtsi_basic(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test basic combo generation."""
        combo = ComboBehavior(
            name="test_combo",
            description="Test combo",
            keyPositions=[0, 1],
            binding=LayoutBinding(value="&kp", params=[LayoutParam(value="ESC")]),
            timeoutMs=50,
            layers=[0],
        )
        
        result = zmk_generator.generate_combos_dtsi(sample_keyboard_profile, [combo], ["base", "nav"])
        
        assert "test_combo {" in result
        assert 'compatible = "zmk,combos";' in result
        assert "key-positions = <0 1>;" in result
        assert "bindings = <&kp ESC>;" in result
        assert "timeout-ms = <50>;" in result
        assert "layers = <0>;" in result

    def test_generate_combos_dtsi_missing_name(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test combo with missing name."""
        combo = ComboBehavior(
            name="",
            keyPositions=[0, 1],
            binding=LayoutBinding(value="&kp", params=[LayoutParam(value="ESC")]),
        )
        
        result = zmk_generator.generate_combos_dtsi(sample_keyboard_profile, [combo], ["base", "nav"])
        
        assert result == ""
        assert any("Skipping combo with missing name" in call[0] for call in mock_logger.warning_calls)

    def test_generate_combos_dtsi_insufficient_positions(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test combo with insufficient key positions."""
        combo = ComboBehavior(
            name="insufficient_combo",
            keyPositions=[0],  # Need at least 2
            binding=LayoutBinding(value="&kp", params=[LayoutParam(value="ESC")]),
        )
        
        result = zmk_generator.generate_combos_dtsi(sample_keyboard_profile, [combo], ["base", "nav"])
        
        assert result == ""
        assert any("requires at least 2 key positions" in call[0] for call in mock_logger.warning_calls)

    def test_generate_combos_dtsi_empty_bindings(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test combo with empty bindings."""
        combo = ComboBehavior(
            name="empty_combo",
            keyPositions=[0, 1],
            binding=LayoutBinding(value="&none", params=[]),
        )
        
        result = zmk_generator.generate_combos_dtsi(sample_keyboard_profile, [combo], ["base", "nav"])
        
        assert result == ""
        assert any("has no bindings" in call[0] for call in mock_logger.warning_calls)


class TestZMKGeneratorInputListeners:
    """Tests for input listener generation."""

    def test_generate_input_listeners_node_empty(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test input listener generation with empty data."""
        result = zmk_generator.generate_input_listeners_node(sample_keyboard_profile, [])
        
        assert result == ""

    def test_generate_input_listeners_node_basic(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test basic input listener generation."""
        input_listeners = [
            InputListener(
                code="encoder_1",
                nodes=[InputListenerNode(code="encoder_1_node", description="Encoder 1")]
            ),
            InputListener(
                code="rotary_switch", 
                nodes=[InputListenerNode(code="rotary_switch_node", description="Rotary Switch")]
            )
        ]
        
        result = zmk_generator.generate_input_listeners_node(sample_keyboard_profile, input_listeners)
        
        assert "encoder_1 {" in result
        assert "// Encoder 1" in result
        assert "encoder_1_node {" in result
        assert "rotary_switch {" in result
        assert "// Rotary Switch" in result

    def test_generate_input_listeners_node_optional_properties(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test input listener with optional properties."""
        input_listeners = [
            InputListener(
                code="encoder_1",
                nodes=[InputListenerNode(code="encoder_1_node", layers=[0, 1])]
            )
        ]
        
        result = zmk_generator.generate_input_listeners_node(sample_keyboard_profile, input_listeners)
        
        assert "encoder_1 {" in result
        assert "layers = <0 1>;" in result


class TestZMKGeneratorKeymapNode:
    """Tests for keymap node generation."""

    def test_generate_keymap_node_basic(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_layout_formatter: MockLayoutFormatter) -> None:
        """Test basic keymap node generation."""
        layout_data = LayoutData(
            title="Test Layout",
            keyboard="test_keyboard",
            layer_names=["base", "nav"],
            layers=[
                [LayoutBinding(value="&kp", params=[LayoutParam(value="Q")]), LayoutBinding(value="&kp", params=[LayoutParam(value="W")])],
                [LayoutBinding(value="&trans", params=[]), LayoutBinding(value="&kp", params=[LayoutParam(value="ESC")])],
            ],
        )
        
        result = zmk_generator.generate_keymap_node(sample_keyboard_profile, layout_data.layer_names, layout_data.layers)
        
        assert "keymap {" in result
        assert 'compatible = "zmk,keymap";' in result
        assert "base {" in result
        assert "nav {" in result
        assert "bindings = <" in result

    def test_generate_keymap_node_empty_layers(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test keymap generation with empty layers."""
        layout_data = LayoutData(
            title="Empty Layout",
            keyboard="test_keyboard",
            layer_names=[],
            layers=[],
        )
        
        result = zmk_generator.generate_keymap_node(sample_keyboard_profile, layout_data.layer_names, layout_data.layers)
        
        assert "keymap {" in result
        assert 'compatible = "zmk,keymap";' in result
        # Should still generate valid structure even with no layers

    def test_generate_keymap_node_grid_formatting(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_layout_formatter: MockLayoutFormatter) -> None:
        """Test keymap generation with grid formatting."""
        layout_data = LayoutData(
            title="Grid Test",
            keyboard="test_keyboard", 
            layer_names=["base"],
            layers=[[
                LayoutBinding(value="&kp", params=[LayoutParam(value="Q")]),
                LayoutBinding(value="&kp", params=[LayoutParam(value="W")]),
                LayoutBinding(value="&kp", params=[LayoutParam(value="E")]),
                LayoutBinding(value="&kp", params=[LayoutParam(value="R")]),
            ]],
        )
        
        zmk_generator.generate_keymap_node(sample_keyboard_profile, layout_data.layer_names, layout_data.layers)
        
        # Should call layout formatter - check generate_calls since that's what the formatter tracks
        mock_formatter = cast(MockLayoutFormatter, zmk_generator._layout_formatter)
        assert len(mock_formatter.format_calls) == 1


class TestZMKGeneratorKconfig:
    """Tests for Kconfig generation."""

    def test_generate_kconfig_conf_basic(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test basic Kconfig generation."""
        layout_data = LayoutData(
            title="Test Layout",
            keyboard="test_keyboard",
            layer_names=["base", "nav"],
            layers=[[], []],
        )
        
        result = zmk_generator.generate_kconfig_conf(layout_data, sample_keyboard_profile)
        
        # Should return tuple of (content, settings)
        assert isinstance(result, tuple)
        assert len(result) == 2
        content, settings = result
        assert isinstance(content, str)
        assert isinstance(settings, dict)

    def test_generate_kconfig_conf_empty_behaviors(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test Kconfig generation with no behaviors."""
        layout_data = LayoutData(
            title="Simple Layout",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[]],
        )
        
        result = zmk_generator.generate_kconfig_conf(layout_data, sample_keyboard_profile)
        
        # Should handle empty behaviors gracefully
        assert isinstance(result, tuple)
        content, settings = result
        assert isinstance(content, str)


class TestZMKGeneratorUtilities:
    """Tests for utility functions."""

    def test_indent_array_basic(self, zmk_generator: ZMKGenerator) -> None:
        """Test array indentation utility."""
        lines = ["line1", "line2", "line3"]
        
        result = zmk_generator._indent_array(lines, "  ")
        
        assert result == ["  line1", "  line2", "  line3"]

    def test_indent_array_empty(self, zmk_generator: ZMKGenerator) -> None:
        """Test array indentation with empty input."""
        result = zmk_generator._indent_array([], "  ")
        
        assert result == []

    def test_indent_array_different_indents(self, zmk_generator: ZMKGenerator) -> None:
        """Test array indentation with different indent strings."""
        lines = ["line1", "line2"]
        
        result_spaces = zmk_generator._indent_array(lines, "    ")
        assert result_spaces == ["    line1", "    line2"]
        
        result_tabs = zmk_generator._indent_array(lines, "\t")
        assert result_tabs == ["\tline1", "\tline2"]


class TestZMKGeneratorFactory:
    """Tests for generator factory function."""

    def test_create_zmk_generator(self) -> None:
        """Test ZMK generator factory."""
        mock_configuration = Mock()
        mock_template = Mock()
        mock_logger = Mock()
        
        generator = create_zmk_generator(
            configuration_provider=mock_configuration,
            template_provider=mock_template,
            logger=mock_logger
        )
        
        assert isinstance(generator, ZMKGenerator)
        assert generator.configuration_provider == mock_configuration
        assert generator.template_provider == mock_template
        assert generator.logger == mock_logger


class TestZMKGeneratorErrorHandling:
    """Tests for error handling and edge cases."""

    def test_generate_behaviors_dtsi_with_none_logger(self, sample_keyboard_profile: Any) -> None:
        """Test behavior generation with no logger."""
        generator = ZMKGenerator(
            configuration_provider=MockConfigurationProvider(),
            template_provider=MockTemplateProvider(),
            logger=None,  # No logger
        )
        
        hold_tap = HoldTapBehavior(
            name="test_ht",
            bindings=["&kp", "&mo"],
        )
        
        # Should not crash with None logger
        result = generator.generate_behaviors_dtsi(sample_keyboard_profile, [hold_tap])
        
        assert "test_ht: test_ht {" in result

    def test_generate_behaviors_dtsi_none_registry(self, sample_keyboard_profile: Any) -> None:
        """Test behavior generation with no registry."""
        generator = ZMKGenerator(
            configuration_provider=MockConfigurationProvider(),
            template_provider=MockTemplateProvider(),
            logger=MockLogger(),
        )
        # Replace registry with None
        generator._behavior_registry = None  # type: ignore
        
        hold_tap = HoldTapBehavior(
            name="test_ht",
            bindings=["&kp", "&mo"],
        )
        
        # Should not crash with None registry
        result = generator.generate_behaviors_dtsi(sample_keyboard_profile, [hold_tap])
        
        assert "test_ht: test_ht {" in result

    def test_generate_keymap_node_malformed_bindings(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any) -> None:
        """Test keymap generation with malformed bindings."""
        layout_data = LayoutData(
            title="Malformed",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[
                LayoutBinding(value="", params=[]),  # Empty binding
                LayoutBinding(value="&invalid", params=[LayoutParam(value="too"), LayoutParam(value="many"), LayoutParam(value="params")]),
            ]],
        )
        
        # Should handle malformed bindings gracefully
        result = zmk_generator.generate_keymap_node(sample_keyboard_profile, layout_data.layer_names, layout_data.layers)
        
        assert "keymap {" in result
        assert "base {" in result

    def test_edge_case_empty_names_with_ampersand_prefix(self, zmk_generator: ZMKGenerator, sample_keyboard_profile: Any, mock_logger: MockLogger) -> None:
        """Test edge case handling of names with ampersand prefix."""
        hold_tap = HoldTapBehavior(
            name="&test_ht",  # With ampersand prefix
            bindings=["&kp", "&mo"],
        )
        
        result = zmk_generator.generate_behaviors_dtsi(sample_keyboard_profile, [hold_tap])
        
        # Should strip ampersand for node name but keep for registration
        assert "test_ht: test_ht {" in result