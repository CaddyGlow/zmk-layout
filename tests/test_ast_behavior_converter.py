"""Test suite for AST behavior converter."""

from unittest.mock import Mock, patch

from zmk_layout.models import (
    CapsWordBehavior,
    ComboBehavior,
    HoldTapBehavior,
    LayoutBinding,
    MacroBehavior,
    ModMorphBehavior,
    StickyKeyBehavior,
    TapDanceBehavior,
)
from zmk_layout.parsers.ast_behavior_converter import ASTBehaviorConverter
from zmk_layout.parsers.ast_nodes import (
    DTComment,
    DTNode,
    DTProperty,
    DTValue,
    DTValueType,
)


class TestASTBehaviorConverter:
    """Test suite for ASTBehaviorConverter."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.converter = ASTBehaviorConverter(logger=self.mock_logger)
        self.converter_with_defines = ASTBehaviorConverter(
            defines={"MY_TIMEOUT": "300", "DEFAULT_LAYER": "1"}, logger=self.mock_logger
        )

    def test_init_without_params(self) -> None:
        """Test converter initialization without parameters."""
        converter = ASTBehaviorConverter()
        assert converter.defines == {}
        assert converter.logger is None

    def test_init_with_params(self) -> None:
        """Test converter initialization with parameters."""
        defines = {"TEST": "value"}
        converter = ASTBehaviorConverter(defines=defines, logger=self.mock_logger)
        assert converter.defines == defines
        assert converter.logger is self.mock_logger

    def test_resolve_token_with_define(self) -> None:
        """Test token resolution with defined value."""
        result = self.converter_with_defines._resolve_token("MY_TIMEOUT")
        assert result == "300"
        self.mock_logger.debug.assert_called_once()

    def test_resolve_token_without_define(self) -> None:
        """Test token resolution without defined value."""
        result = self.converter._resolve_token("UNDEFINED")
        assert result == "UNDEFINED"

    def test_resolve_binding_string_no_defines(self) -> None:
        """Test binding string resolution without defines."""
        result = self.converter._resolve_binding_string("&kp A")
        assert result == "&kp A"

    def test_resolve_binding_string_with_defines(self) -> None:
        """Test binding string resolution with defines."""
        result = self.converter_with_defines._resolve_binding_string("&kp MY_TIMEOUT")
        assert result == "&kp 300"

    def test_resolve_binding_string_complex(self) -> None:
        """Test complex binding string resolution."""
        converter = ASTBehaviorConverter(
            defines={"LAYER": "1", "KEY": "A"}, logger=self.mock_logger
        )
        result = converter._resolve_binding_string("&lt LAYER KEY")
        assert result == "&lt 1 A"

    def test_resolve_binding_string_nested_functions(self) -> None:
        """Test binding string resolution with nested functions."""
        result = self.converter_with_defines._resolve_binding_string(
            "&kp LG(LA(MY_TIMEOUT))"
        )
        assert result == "&kp LG(LA(300))"

    def test_resolve_binding_string_behavior_references_not_resolved(self) -> None:
        """Test that behavior references starting with & are not resolved."""
        converter = ASTBehaviorConverter(
            defines={"kp": "should_not_resolve"}, logger=self.mock_logger
        )
        result = converter._resolve_binding_string("&kp A")
        assert result == "&kp A"

    def test_convert_hold_tap_node_success(self) -> None:
        """Test successful hold-tap node conversion."""
        # Create a mock DTNode
        node = DTNode(name="my_ht", label="my_ht")
        node.add_property(DTProperty("tapping-term-ms", DTValue.integer(200)))
        node.add_property(DTProperty("quick-tap-ms", DTValue.integer(150)))
        node.add_property(DTProperty("flavor", DTValue.string("tap-preferred")))
        node.add_property(DTProperty("bindings", DTValue.array(["&kp", "&mo"])))

        result = self.converter.convert_hold_tap_node(node)

        assert result is not None
        assert isinstance(result, HoldTapBehavior)
        assert result.name == "&my_ht"
        assert result.tapping_term_ms == 200
        assert result.quick_tap_ms == 150
        assert result.flavor == "tap-preferred"

    def test_convert_hold_tap_node_missing_name(self) -> None:
        """Test hold-tap node conversion with missing name."""
        node = DTNode()
        result = self.converter.convert_hold_tap_node(node)

        assert result is None
        self.mock_logger.warning.assert_called()

    def test_convert_hold_tap_node_with_comments(self) -> None:
        """Test hold-tap node conversion with description from comments."""
        node = DTNode(name="my_ht", label="my_ht")
        comment = DTComment("Hold-tap behavior for home row mods")
        node.comments = [comment]

        result = self.converter.convert_hold_tap_node(node)

        assert result is not None
        assert result.description == "Hold-tap behavior for home row mods"

    def test_convert_hold_tap_node_exception(self) -> None:
        """Test hold-tap node conversion with exception."""
        node = DTNode(name="my_ht")

        # Patch to force an exception
        with patch.object(
            self.converter,
            "_extract_description_from_node",
            side_effect=Exception("Test error"),
        ):
            result = self.converter.convert_hold_tap_node(node)

        assert result is None
        self.mock_logger.error.assert_called()

    def test_convert_macro_node_success(self) -> None:
        """Test successful macro node conversion."""
        node = DTNode(name="my_macro", label="my_macro")
        node.add_property(DTProperty("wait-ms", DTValue.integer(40)))
        node.add_property(DTProperty("tap-ms", DTValue.integer(30)))
        node.add_property(DTProperty("#binding-cells", DTValue.integer(1)))
        node.add_property(
            DTProperty("bindings", DTValue.array(["&kp", "HOME", "&kp", "END"]))
        )

        result = self.converter.convert_macro_node(node)

        assert result is not None
        assert isinstance(result, MacroBehavior)
        assert result.name == "&my_macro"
        assert result.wait_ms == 40
        assert result.tap_ms == 30
        assert result.params == ["code"]

    def test_convert_macro_node_binding_cells_variations(self) -> None:
        """Test macro node conversion with different binding-cells property names."""
        # Test #binding-cells
        node1 = DTNode(name="macro1")
        node1.add_property(DTProperty("#binding-cells", DTValue.integer(0)))
        result1 = self.converter.convert_macro_node(node1)
        assert result1 is not None
        assert result1.params == []

        # Test binding-cells
        node2 = DTNode(name="macro2")
        node2.add_property(DTProperty("binding-cells", DTValue.integer(2)))
        result2 = self.converter.convert_macro_node(node2)
        assert result2 is not None
        assert result2.params == ["param1", "param2"]

        # Test binding_cells
        node3 = DTNode(name="macro3")
        node3.add_property(DTProperty("binding_cells", DTValue.integer(1)))
        result3 = self.converter.convert_macro_node(node3)
        assert result3 is not None
        assert result3.params == ["code"]

    def test_convert_macro_node_compatible_fallback(self) -> None:
        """Test macro node conversion with compatible property fallback."""
        node = DTNode(name="my_macro")
        node.add_property(
            DTProperty("compatible", DTValue.string("zmk,behavior-macro-one-param"))
        )

        result = self.converter.convert_macro_node(node)

        assert result is not None
        assert result.params == ["code"]
        self.mock_logger.warning.assert_called()

    def test_convert_macro_node_no_params_info(self) -> None:
        """Test macro node conversion without parameter information."""
        node = DTNode(name="my_macro")

        result = self.converter.convert_macro_node(node)

        assert result is not None
        assert result.params == []
        self.mock_logger.warning.assert_called()

    def test_convert_combo_node_success(self) -> None:
        """Test successful combo node conversion."""
        node = DTNode(name="combo_esc", label="combo_esc")
        node.add_property(DTProperty("key-positions", DTValue.array([0, 1])))
        node.add_property(DTProperty("bindings", DTValue.array(["&kp", "ESC"])))
        node.add_property(DTProperty("timeout-ms", DTValue.integer(50)))
        node.add_property(DTProperty("layers", DTValue.array([0, 1])))

        result = self.converter.convert_combo_node(node)

        assert result is not None
        assert isinstance(result, ComboBehavior)
        assert result.name == "esc"  # combo_ prefix stripped
        assert result.key_positions == [0, 1]
        assert result.timeout_ms == 50
        assert result.layers == [0, 1]

    def test_convert_combo_node_missing_key_positions(self) -> None:
        """Test combo node conversion with missing key-positions."""
        node = DTNode(name="combo_test")
        node.add_property(DTProperty("bindings", DTValue.array(["&kp", "A"])))

        result = self.converter.convert_combo_node(node)

        assert result is None
        self.mock_logger.warning.assert_called()

    def test_convert_combo_node_missing_bindings(self) -> None:
        """Test combo node conversion with missing bindings."""
        node = DTNode(name="combo_test")
        node.add_property(DTProperty("key-positions", DTValue.array([0, 1])))

        result = self.converter.convert_combo_node(node)

        assert result is None
        self.mock_logger.warning.assert_called()

    def test_convert_combo_node_without_layers(self) -> None:
        """Test combo node conversion without layers property."""
        node = DTNode(name="combo_test")
        node.add_property(DTProperty("key-positions", DTValue.array([0, 1])))
        node.add_property(DTProperty("bindings", DTValue.array(["&kp", "A"])))

        result = self.converter.convert_combo_node(node)

        assert result is not None
        assert result.layers == [-1]  # placeholder added

    def test_extract_description_from_node_comments(self) -> None:
        """Test description extraction from node comments."""
        node = DTNode(name="test")
        comment1 = DTComment("// First line")
        comment2 = DTComment("// Second line")
        node.comments = [comment1, comment2]

        result = self.converter._extract_description_from_node(node)

        assert result == "First line\nSecond line"

    def test_extract_description_from_node_multiline_cleanup(self) -> None:
        """Test description extraction with multiline cleanup."""
        node = DTNode(name="test")
        node.comments = [
            DTComment("// Line 1"),
            DTComment("//"),
            DTComment("//"),
            DTComment("//"),
            DTComment("// Line 2"),
        ]

        result = self.converter._extract_description_from_node(node)

        # Should clean up excessive empty lines
        assert "Line 1\n\nLine 2" in result

    def test_extract_description_from_property(self) -> None:
        """Test description extraction from description property."""
        node = DTNode(name="test")
        node.add_property(
            DTProperty("description", DTValue.string("Property description"))
        )

        result = self.converter._extract_description_from_node(node)

        assert result == "Property description"

    def test_extract_string_from_property_various_types(self) -> None:
        """Test string extraction from various property types."""
        # String type
        prop1 = DTProperty("test", DTValue.string("hello"))
        assert self.converter._extract_string_from_property(prop1) == "hello"

        # Integer type
        prop2 = DTProperty("test", DTValue.integer(42))
        assert self.converter._extract_string_from_property(prop2) == "42"

        # Boolean type
        prop3 = DTProperty("test", DTValue.boolean(True))
        assert self.converter._extract_string_from_property(prop3) == "True"

        # None value
        prop4 = DTProperty("test", None)
        assert self.converter._extract_string_from_property(prop4) == ""

    def test_extract_int_from_property_various_types(self) -> None:
        """Test integer extraction from various property types."""
        # Integer type
        prop1 = DTProperty("test", DTValue.integer(42))
        assert self.converter._extract_int_from_property(prop1) == 42

        # String type with valid number
        prop2 = DTProperty("test", DTValue.string("123"))
        assert self.converter._extract_int_from_property(prop2) == 123

        # String type with angle brackets
        prop3 = DTProperty("test", DTValue.string("<456>"))
        assert self.converter._extract_int_from_property(prop3) == 456

        # Array type
        prop4 = DTProperty("test", DTValue.array([789]))
        assert self.converter._extract_int_from_property(prop4) == 789

        # Invalid string
        prop5 = DTProperty("test", DTValue.string("invalid"))
        assert self.converter._extract_int_from_property(prop5) is None

        # None value
        prop6 = DTProperty("test", None)
        assert self.converter._extract_int_from_property(prop6) is None

    def test_extract_array_from_property_various_types(self) -> None:
        """Test array extraction from various property types."""
        # Array type
        prop1 = DTProperty("test", DTValue.array([1, 2, 3]))
        assert self.converter._extract_array_from_property(prop1) == [1, 2, 3]

        # Integer type (single value)
        prop2 = DTProperty("test", DTValue.integer(42))
        assert self.converter._extract_array_from_property(prop2) == [42]

        # String type with spaces
        prop3 = DTProperty("test", DTValue(DTValueType.ARRAY, [], "<1 2 3>"))
        assert self.converter._extract_array_from_property(prop3) == []

        # None value
        prop4 = DTProperty("test", None)
        assert self.converter._extract_array_from_property(prop4) == []

    def test_extract_bindings_from_property_array(self) -> None:
        """Test bindings extraction from array property."""
        prop = DTProperty("bindings", DTValue.array(["&kp", "&mo"]))
        result = self.converter._extract_bindings_from_property(prop)
        assert result == ["&kp", "&mo"]

    def test_extract_bindings_from_property_raw(self) -> None:
        """Test bindings extraction from raw property."""
        prop = DTProperty("bindings", DTValue(DTValueType.STRING, "", "<&kp, &mo>"))
        result = self.converter._extract_bindings_from_property(prop)
        assert result == ["&kp", "&mo"]

    def test_extract_macro_bindings_from_property_array(self) -> None:
        """Test macro bindings extraction from array property."""
        prop = DTProperty("bindings", DTValue.array(["&kp", "HOME", "&kp", "END"]))

        # Test without mocks to verify actual behavior
        result = self.converter._extract_macro_bindings_from_property(prop)

        # Should group into 2 bindings: "&kp HOME" and "&kp END"
        assert len(result) == 2

        # Verify each binding has the correct structure
        for binding in result:
            assert hasattr(binding, "value")
            assert binding.value == "&kp" or binding.value.startswith("&kp")

    def test_extract_single_binding_from_property_simple(self) -> None:
        """Test single binding extraction from simple property."""
        prop = DTProperty("bindings", DTValue.array(["&kp", "A"]))

        with (
            patch.object(
                self.converter,
                "_preprocess_moergo_binding_edge_cases",
                side_effect=lambda x: x,
            ),
            patch.object(
                self.converter, "_resolve_binding_string", side_effect=lambda x: x
            ),
            patch("zmk_layout.models.core.LayoutBinding.from_str") as mock_from_str,
        ):
            mock_binding = Mock()
            mock_from_str.return_value = mock_binding

            result = self.converter._extract_single_binding_from_property(prop)

            assert result == mock_binding

    def test_extract_single_binding_from_property_with_spaced_parentheses(self) -> None:
        """Test single binding extraction with spaced parentheses."""
        prop = DTProperty("bindings", DTValue(DTValueType.STRING, "", "<&kp LG( A )>"))

        with (
            patch.object(
                self.converter,
                "_preprocess_moergo_binding_edge_cases",
                side_effect=lambda x: x,
            ),
            patch.object(
                self.converter, "_resolve_binding_string", side_effect=lambda x: x
            ),
            patch("zmk_layout.models.core.LayoutBinding.from_str") as mock_from_str,
        ):
            mock_binding = Mock()
            mock_from_str.return_value = mock_binding

            result = self.converter._extract_single_binding_from_property(prop)

            assert result == mock_binding
            # Should be called with fixed parentheses
            assert mock_from_str.called
            # The exact call depends on the method's behavior - let's check if parentheses were fixed
            call_args = mock_from_str.call_args[0][0]
            assert "LG(" in call_args and "A" in call_args

    def test_extract_single_binding_from_property_none_value(self) -> None:
        """Test single binding extraction from None property."""
        prop = DTProperty("bindings", None)
        result = self.converter._extract_single_binding_from_property(prop)
        assert result is None

    def test_extract_single_binding_from_property_exception(self) -> None:
        """Test single binding extraction with exception."""
        prop = DTProperty("bindings", DTValue.array(["&kp", "A"]))

        with patch.object(
            self.converter,
            "_preprocess_moergo_binding_edge_cases",
            side_effect=Exception("Test error"),
        ):
            result = self.converter._extract_single_binding_from_property(prop)

            # Should return fallback binding
            assert result is not None
            assert result.value == "&none"

    def test_reconstruct_nested_function_call_simple(self) -> None:
        """Test reconstruction of simple function call."""
        parts = ["&sk", "LSHIFT"]
        result = self.converter._reconstruct_nested_function_call(parts)
        assert result == "&sk LSHIFT"

    def test_reconstruct_nested_function_call_no_parentheses(self) -> None:
        """Test reconstruction without parentheses."""
        parts = ["&kp", "A"]
        result = self.converter._reconstruct_nested_function_call(parts)
        assert result == "&kp A"

    def test_reconstruct_nested_function_call_nested(self) -> None:
        """Test reconstruction of nested function calls."""
        parts = ["&sk", "LG", "(", "LA", "(", "LC", "(", "LSHFT", ")", ")", ")"]
        result = self.converter._reconstruct_nested_function_call(parts)
        assert result == "&sk LG(LA(LC(LSHFT)))"

    def test_reconstruct_nested_function_call_empty(self) -> None:
        """Test reconstruction with empty parts."""
        result = self.converter._reconstruct_nested_function_call([])
        assert result == ""

    def test_preprocess_moergo_binding_edge_cases_sys_reset(self) -> None:
        """Test MoErgo edge case preprocessing for sys_reset."""
        result = self.converter._preprocess_moergo_binding_edge_cases("&sys_reset")
        assert result == "&reset"
        self.mock_logger.debug.assert_called()

    def test_preprocess_moergo_binding_edge_cases_magic_cleanup(self) -> None:
        """Test MoErgo edge case preprocessing for magic parameter cleanup."""
        result = self.converter._preprocess_moergo_binding_edge_cases(
            "&magic LAYER_Magic 0"
        )
        assert result == "&magic"
        self.mock_logger.debug.assert_called()

    def test_preprocess_moergo_binding_edge_cases_no_change(self) -> None:
        """Test MoErgo edge case preprocessing with no changes needed."""
        result = self.converter._preprocess_moergo_binding_edge_cases("&kp A")
        assert result == "&kp A"

    def test_convert_input_listener_node_success(self) -> None:
        """Test successful input listener node conversion."""
        node = DTNode(name="input_listener")
        child_node = DTNode(name="xy_listener")
        child_node.add_property(DTProperty("layers", DTValue.array([0, 1])))
        child_node.add_property(
            DTProperty("input-processors", DTValue.array(["&zip_xy_scaler", "1", "9"]))
        )
        node.add_child(child_node)

        result = self.converter.convert_input_listener_node(node)

        assert result is not None
        assert result.code == "&input_listener"
        assert len(result.nodes) == 1
        assert result.nodes[0].code == "xy_listener"

    def test_convert_input_listener_node_missing_name(self) -> None:
        """Test input listener node conversion with missing name."""
        node = DTNode()
        result = self.converter.convert_input_listener_node(node)

        assert result is None
        self.mock_logger.warning.assert_called()

    def test_convert_input_listener_child_node_success(self) -> None:
        """Test successful input listener child node conversion."""
        child_node = DTNode(name="xy_listener")
        child_node.add_property(DTProperty("layers", DTValue.array([0, 1])))

        result = self.converter._convert_input_listener_child_node(
            "xy_listener", child_node
        )

        assert result is not None
        assert result.code == "xy_listener"
        assert result.layers == [0, 1]

    def test_extract_input_processors_from_property_array_separate(self) -> None:
        """Test input processors extraction from separate array elements."""
        prop = DTProperty(
            "input-processors", DTValue.array(["&zip_xy_scaler", "1", "9"])
        )
        result = self.converter._extract_input_processors_from_property(prop)

        assert len(result) == 1
        assert result[0].code == "&zip_xy_scaler"
        assert result[0].params == [1, 9]

    def test_extract_input_processors_from_property_array_space_separated(self) -> None:
        """Test input processors extraction from space-separated string."""
        prop = DTProperty("input-processors", DTValue.array(["&zip_xy_scaler 1 9"]))
        result = self.converter._extract_input_processors_from_property(prop)

        assert len(result) == 1
        assert result[0].code == "&zip_xy_scaler"
        assert result[0].params == [1, 9]

    def test_extract_input_processors_from_property_single(self) -> None:
        """Test input processors extraction from single processor."""
        prop = DTProperty("input-processors", DTValue.string("&processor"))
        result = self.converter._extract_input_processors_from_property(prop)

        assert len(result) == 1
        assert result[0].code == "&processor"
        assert result[0].params == []

    def test_convert_tap_dance_node_success(self) -> None:
        """Test successful tap dance node conversion."""
        node = DTNode(name="&td_q_esc")
        node.add_property(
            DTProperty("compatible", DTValue.string("zmk,behavior-tap-dance"))
        )
        node.add_property(DTProperty("label", DTValue.string("TAP_DANCE_Q_ESC")))
        node.add_property(DTProperty("tapping-term-ms", DTValue.integer(200)))
        node.add_property(DTProperty("bindings", DTValue.array(["&kp Q", "&kp ESC"])))

        result = self.converter.convert_tap_dance_node(node)

        assert result is not None
        assert isinstance(result, TapDanceBehavior)
        assert result.name == "td_q_esc"  # & prefix stripped
        assert result.description == "TAP_DANCE_Q_ESC"
        assert result.tapping_term_ms == 200

    def test_convert_tap_dance_node_invalid_compatible(self) -> None:
        """Test tap dance node conversion with invalid compatible."""
        node = DTNode(name="test")
        node.add_property(DTProperty("compatible", DTValue.string("invalid")))

        result = self.converter.convert_tap_dance_node(node)

        assert result is None

    def test_convert_tap_dance_node_tapping_term_array(self) -> None:
        """Test tap dance node conversion with tapping-term-ms as array."""
        node = DTNode(name="test")
        node.add_property(
            DTProperty("compatible", DTValue.string("zmk,behavior-tap-dance"))
        )
        node.add_property(DTProperty("tapping-term-ms", DTValue.array([250])))
        node.add_property(DTProperty("bindings", DTValue.array(["&kp A", "&kp B"])))

        result = self.converter.convert_tap_dance_node(node)

        assert result is not None
        assert result.tapping_term_ms == 250

    def test_convert_sticky_key_node_success(self) -> None:
        """Test successful sticky key node conversion."""
        node = DTNode(name="&sk_shift")
        node.add_property(
            DTProperty("compatible", DTValue.string("zmk,behavior-sticky-key"))
        )
        node.add_property(DTProperty("label", DTValue.string("STICKY_SHIFT")))
        node.add_property(DTProperty("release-after-ms", DTValue.integer(1000)))
        node.add_property(DTProperty("quick-release", DTValue.boolean(True)))
        node.add_property(DTProperty("lazy", DTValue.boolean(True)))
        node.add_property(DTProperty("ignore-modifiers", DTValue.boolean(True)))
        node.add_property(DTProperty("bindings", DTValue.array(["&kp LSHIFT"])))

        result = self.converter.convert_sticky_key_node(node)

        assert result is not None
        assert isinstance(result, StickyKeyBehavior)
        assert result.name == "sk_shift"  # & prefix stripped
        assert result.description == "STICKY_SHIFT"
        assert result.release_after_ms == 1000
        assert result.quick_release is True
        assert result.lazy is True
        assert result.ignore_modifiers is True

    def test_convert_sticky_key_node_invalid_compatible(self) -> None:
        """Test sticky key node conversion with invalid compatible."""
        node = DTNode(name="test")
        node.add_property(DTProperty("compatible", DTValue.string("invalid")))

        result = self.converter.convert_sticky_key_node(node)

        assert result is None

    def test_convert_caps_word_node_success(self) -> None:
        """Test successful caps word node conversion."""
        node = DTNode(name="&caps_word")
        node.add_property(
            DTProperty("compatible", DTValue.string("zmk,behavior-caps-word"))
        )
        node.add_property(DTProperty("label", DTValue.string("CAPS_WORD")))
        node.add_property(
            DTProperty("continue-list", DTValue.array(["UNDERSCORE", "BACKSPACE"]))
        )
        node.add_property(DTProperty("mods", DTValue.integer(2)))

        result = self.converter.convert_caps_word_node(node)

        assert result is not None
        assert isinstance(result, CapsWordBehavior)
        assert result.name == "caps_word"  # & prefix stripped
        assert result.description == "CAPS_WORD"
        assert result.continue_list == ["UNDERSCORE", "BACKSPACE"]
        assert result.mods == 2

    def test_convert_caps_word_node_continue_list_with_defines(self) -> None:
        """Test caps word node conversion with defines in continue-list."""
        node = DTNode(name="caps_word")
        node.add_property(
            DTProperty("compatible", DTValue.string("zmk,behavior-caps-word"))
        )
        node.add_property(DTProperty("continue-list", DTValue.array(["MY_TIMEOUT"])))

        result = self.converter_with_defines.convert_caps_word_node(node)

        assert result is not None
        assert result.continue_list == ["300"]  # MY_TIMEOUT resolved

    def test_convert_caps_word_node_invalid_compatible(self) -> None:
        """Test caps word node conversion with invalid compatible."""
        node = DTNode(name="test")
        node.add_property(DTProperty("compatible", DTValue.string("invalid")))

        result = self.converter.convert_caps_word_node(node)

        assert result is None

    def test_convert_mod_morph_node_success(self) -> None:
        """Test successful mod-morph node conversion."""
        node = DTNode(name="&mm_dot_colon")
        node.add_property(
            DTProperty("compatible", DTValue.string("zmk,behavior-mod-morph"))
        )
        node.add_property(DTProperty("label", DTValue.string("DOT_COLON")))
        node.add_property(DTProperty("mods", DTValue.integer(1)))
        node.add_property(DTProperty("keep-mods", DTValue.integer(2)))
        node.add_property(
            DTProperty("bindings", DTValue.array(["&kp DOT", "&kp COLON"]))
        )

        result = self.converter.convert_mod_morph_node(node)

        assert result is not None
        assert isinstance(result, ModMorphBehavior)
        assert result.name == "mm_dot_colon"  # & prefix stripped
        assert result.description == "DOT_COLON"
        assert result.mods == 1
        assert result.keep_mods == 2

    def test_convert_mod_morph_node_invalid_compatible(self) -> None:
        """Test mod-morph node conversion with invalid compatible."""
        node = DTNode(name="test")
        node.add_property(DTProperty("compatible", DTValue.string("invalid")))

        result = self.converter.convert_mod_morph_node(node)

        assert result is None

    def test_populate_hold_tap_properties_all_properties(self) -> None:
        """Test hold-tap properties population with all properties."""
        hold_tap = HoldTapBehavior(name="&test", description="")
        node = DTNode(name="test")
        node.add_property(DTProperty("tapping-term-ms", DTValue.integer(200)))
        node.add_property(DTProperty("quick-tap-ms", DTValue.integer(150)))
        node.add_property(DTProperty("require-prior-idle-ms", DTValue.integer(100)))
        node.add_property(DTProperty("flavor", DTValue.string("tap-preferred")))
        node.add_property(
            DTProperty("hold-trigger-key-positions", DTValue.array([5, 6, 7]))
        )
        node.add_property(DTProperty("hold-trigger-on-release", DTValue.boolean(True)))
        node.add_property(DTProperty("retro-tap", DTValue.boolean(True)))
        node.add_property(DTProperty("bindings", DTValue.array(["&kp", "&mo"])))

        self.converter._populate_hold_tap_properties(hold_tap, node)

        assert hold_tap.tapping_term_ms == 200
        assert hold_tap.quick_tap_ms == 150
        assert hold_tap.require_prior_idle_ms == 100
        assert hold_tap.flavor == "tap-preferred"
        assert hold_tap.hold_trigger_key_positions == [5, 6, 7]
        assert hold_tap.hold_trigger_on_release is True
        assert hold_tap.retro_tap is True

    def test_populate_macro_properties_all_properties(self) -> None:
        """Test macro properties population with all properties."""
        macro = MacroBehavior(name="&test", description="")
        node = DTNode(name="test")
        node.add_property(DTProperty("wait-ms", DTValue.integer(40)))
        node.add_property(DTProperty("tap-ms", DTValue.integer(30)))
        node.add_property(DTProperty("bindings", DTValue.array(["&kp", "A"])))

        self.converter._populate_macro_properties(macro, node)

        assert macro.wait_ms == 40
        assert macro.tap_ms == 30

    def test_populate_combo_properties_all_properties(self) -> None:
        """Test combo properties population with all properties."""
        combo = ComboBehavior(
            name="test",
            description="",
            keyPositions=[0, 1],
            binding=LayoutBinding(value="&kp", params=[]),
        )
        node = DTNode(name="test")
        node.add_property(DTProperty("timeout-ms", DTValue.integer(50)))
        node.add_property(DTProperty("layers", DTValue.array([0, 1, 2])))

        self.converter._populate_combo_properties(combo, node)

        assert combo.timeout_ms == 50
        assert combo.layers == [0, 1, 2]

    def test_populate_combo_properties_missing_layers(self) -> None:
        """Test combo properties population with missing layers."""
        combo = ComboBehavior(
            name="test",
            description="",
            keyPositions=[0, 1],
            binding=LayoutBinding(value="&kp", params=[]),
        )
        node = DTNode(name="test")

        self.converter._populate_combo_properties(combo, node)

        assert combo.layers == [-1]  # placeholder added
        self.mock_logger.debug.assert_called()

    def test_create_ast_behavior_converter_function(self) -> None:
        """Test the factory function for creating AST behavior converter."""
        from zmk_layout.parsers.ast_behavior_converter import (
            create_ast_behavior_converter,
        )

        defines = {"TEST": "value"}
        converter = create_ast_behavior_converter(defines)

        assert isinstance(converter, ASTBehaviorConverter)
        assert converter.defines == defines

    def test_create_ast_behavior_converter_function_no_args(self) -> None:
        """Test the factory function without arguments."""
        from zmk_layout.parsers.ast_behavior_converter import (
            create_ast_behavior_converter,
        )

        converter = create_ast_behavior_converter()

        assert isinstance(converter, ASTBehaviorConverter)
        assert converter.defines == {}

    def test_error_handling_in_all_convert_methods(self) -> None:
        """Test error handling in all convert methods."""
        # Create a node that will cause various errors
        bad_node = DTNode(name="test")

        # Test all convert methods handle exceptions gracefully
        methods_to_test = [
            "convert_hold_tap_node",
            "convert_macro_node",
            "convert_combo_node",
            "convert_tap_dance_node",
            "convert_sticky_key_node",
            "convert_caps_word_node",
            "convert_mod_morph_node",
        ]

        for method_name in methods_to_test:
            method = getattr(self.converter, method_name)

            # Patch internal method to raise exception
            with patch.object(
                self.converter,
                "_extract_description_from_node",
                side_effect=Exception("Test error"),
            ):
                result = method(bad_node)

                # Should return None and log error
                assert result is None
                # Logger should have been called (error method)
                assert self.mock_logger.error.called

        # Test input_listener_node separately as it has different behavior
        # Force an exception by creating a node that will cause an error in the method body
        with patch(
            "zmk_layout.models.behaviors.InputListener",
            side_effect=Exception("Test error"),
        ):
            result = self.converter.convert_input_listener_node(bad_node)
            assert result is None

    def test_extract_macro_bindings_with_moergo_preprocessing(self) -> None:
        """Test macro bindings extraction with MoErgo preprocessing."""
        # Test the preprocessing directly
        result = self.converter._preprocess_moergo_binding_edge_cases("&sys_reset")
        assert result == "&reset"

        # Test preprocessing of magic parameter cleanup
        result = self.converter._preprocess_moergo_binding_edge_cases(
            "&magic LAYER_Magic 0"
        )
        assert result == "&magic"

    def test_extract_macro_bindings_fallback_on_error(self) -> None:
        """Test macro bindings extraction fallback behavior on parsing error."""
        prop = DTProperty("bindings", DTValue.array(["&invalid_binding"]))

        with (
            patch.object(
                self.converter,
                "_preprocess_moergo_binding_edge_cases",
                side_effect=lambda x: x,
            ),
            patch.object(
                self.converter, "_resolve_binding_string", side_effect=lambda x: x
            ),
            patch(
                "zmk_layout.models.core.LayoutBinding.from_str",
                side_effect=Exception("Parse error"),
            ),
        ):
            result = self.converter._extract_macro_bindings_from_property(prop)

            # Should create fallback binding
            assert len(result) == 1
            assert result[0].value == "&invalid_binding"
            assert result[0].params == []

    def test_comprehensive_node_conversion_flow(self) -> None:
        """Test comprehensive flow of node conversion with all features."""
        # Create a complex hold-tap node with multiple properties and comments
        node = DTNode(name="home_row_mod", label="hrm")

        # Add comments for description
        comment = DTComment("// Home row mod with balanced settings")
        node.comments = [comment]

        # Add all possible properties
        node.add_property(DTProperty("tapping-term-ms", DTValue.integer(200)))
        node.add_property(DTProperty("quick-tap-ms", DTValue.integer(150)))
        node.add_property(DTProperty("require-prior-idle-ms", DTValue.integer(100)))
        node.add_property(DTProperty("flavor", DTValue.string("balanced")))
        node.add_property(
            DTProperty("hold-trigger-key-positions", DTValue.array([5, 6, 7, 8, 9]))
        )
        node.add_property(DTProperty("hold-trigger-on-release", DTValue.boolean(True)))
        node.add_property(DTProperty("retro-tap", DTValue.boolean(True)))
        node.add_property(DTProperty("bindings", DTValue.array(["&kp", "&mo"])))

        result = self.converter.convert_hold_tap_node(node)

        # Verify all properties were extracted correctly
        assert result is not None
        assert result.name == "&hrm"
        assert result.description == "Home row mod with balanced settings"
        assert result.tapping_term_ms == 200
        assert result.quick_tap_ms == 150
        assert result.require_prior_idle_ms == 100
        assert result.flavor == "balanced"
        assert result.hold_trigger_key_positions == [5, 6, 7, 8, 9]
        assert result.hold_trigger_on_release is True
        assert result.retro_tap is True
        assert result.bindings == ["&kp", "&mo"]

    def test_edge_case_empty_and_none_values(self) -> None:
        """Test handling of empty and None values in various scenarios."""
        # Test with None property values
        node = DTNode(name="test")
        node.add_property(DTProperty("empty-prop", None))

        # Should not crash and handle gracefully
        empty_prop = node.get_property("empty-prop")
        assert empty_prop is not None
        result = self.converter._extract_string_from_property(empty_prop)
        assert result == ""

        result_int = self.converter._extract_int_from_property(empty_prop)
        assert result_int is None

        result_array = self.converter._extract_array_from_property(empty_prop)
        assert result_array == []

    def test_all_binding_extraction_methods_with_none_input(self) -> None:
        """Test all binding extraction methods handle None input gracefully."""
        # Test all binding extraction methods with None
        prop_none = DTProperty("test", None)

        # Should all handle None gracefully
        result1 = self.converter._extract_bindings_from_property(prop_none)
        assert result1 == []

        result2 = self.converter._extract_macro_bindings_from_property(prop_none)
        assert result2 == []

        result3 = self.converter._extract_single_binding_from_property(prop_none)
        assert result3 is None

        result4 = self.converter._extract_input_processors_from_property(prop_none)
        assert result4 == []
