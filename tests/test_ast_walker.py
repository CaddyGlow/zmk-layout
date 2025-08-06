"""Comprehensive tests for AST walker infrastructure."""

from unittest.mock import Mock, patch

from zmk_layout.parsers.ast_nodes import (
    DTNode,
    DTProperty,
    DTValue,
    DTValueType,
)
from zmk_layout.parsers.ast_walker import (
    BehaviorExtractor,
    ComboExtractor,
    DTMultiWalker,
    DTWalker,
    HoldTapExtractor,
    MacroExtractor,
    UniversalBehaviorExtractor,
    create_behavior_extractor,
    create_universal_behavior_extractor,
    create_universal_behavior_extractor_with_converter,
)


class TestDTWalker:
    """Test DTWalker class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Create a simple AST structure for testing
        self.root = DTNode(name="root")

        # Add properties to root
        compatible_prop = DTProperty(name="compatible", value=DTValue.string("test,device"))
        self.root.add_property(compatible_prop)

        # Create child nodes
        self.child1 = DTNode(name="child1", label="label1")
        self.child1.add_property(DTProperty(name="prop1", value=DTValue.integer(42)))

        self.child2 = DTNode(name="child2", unit_address="deadbeef")
        self.child2.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-macro")))

        # Create grandchild
        self.grandchild = DTNode(name="grandchild")
        self.grandchild.add_property(DTProperty(name="test-prop", value=DTValue.array([1, 2, 3])))

        # Build tree structure
        self.child1.add_child(self.grandchild)
        self.root.add_child(self.child1)
        self.root.add_child(self.child2)

        # Create mock logger
        self.mock_logger = Mock()

    def test_init(self) -> None:
        """Test DTWalker initialization."""
        walker = DTWalker(self.root)
        assert walker.root == self.root
        assert walker.logger is None

        walker_with_logger = DTWalker(self.root, self.mock_logger)
        assert walker_with_logger.logger == self.mock_logger

    def test_find_nodes_with_predicate(self) -> None:
        """Test finding nodes with custom predicate."""
        walker = DTWalker(self.root)

        # Find nodes with specific name
        result = walker.find_nodes(lambda node: node.name == "child1")
        assert len(result) == 1
        assert result[0] == self.child1

        # Find nodes with unit address
        result = walker.find_nodes(lambda node: bool(node.unit_address))
        assert len(result) == 1
        assert result[0] == self.child2

        # Find all nodes (should return all 4 nodes in tree)
        result = walker.find_nodes(lambda node: True)
        assert len(result) == 4  # root, child1, child2, grandchild

    def test_find_nodes_by_compatible(self) -> None:
        """Test finding nodes by compatible property."""
        walker = DTWalker(self.root)

        # Test delegation to root.find_nodes_by_compatible
        with patch.object(self.root, "find_nodes_by_compatible", return_value=[self.child2]) as mock_find:
            result = walker.find_nodes_by_compatible("zmk,behavior-macro")
            mock_find.assert_called_once_with("zmk,behavior-macro")
            assert result == [self.child2]

    def test_find_nodes_by_name(self) -> None:
        """Test finding nodes by name."""
        walker = DTWalker(self.root)

        result = walker.find_nodes_by_name("child1")
        assert len(result) == 1
        assert result[0] == self.child1

        result = walker.find_nodes_by_name("nonexistent")
        assert len(result) == 0

    def test_find_nodes_by_label(self) -> None:
        """Test finding nodes by label."""
        walker = DTWalker(self.root)

        result = walker.find_nodes_by_label("label1")
        assert len(result) == 1
        assert result[0] == self.child1

        result = walker.find_nodes_by_label("nonexistent")
        assert len(result) == 0

    def test_find_nodes_by_path_pattern(self) -> None:
        """Test finding nodes by path pattern."""
        walker = DTWalker(self.root)

        # Find nodes with "child1" in path
        result = walker.find_nodes_by_path_pattern("child1")
        assert len(result) == 2  # child1 and grandchild
        assert self.child1 in result
        assert self.grandchild in result

        # Find nodes with specific pattern
        result = walker.find_nodes_by_path_pattern("deadbeef")
        assert len(result) == 1
        assert result[0] == self.child2

    def test_find_properties(self) -> None:
        """Test finding properties with predicate."""
        walker = DTWalker(self.root)

        # Find compatible properties
        result = walker.find_properties(lambda prop: prop.name == "compatible")
        assert len(result) == 2
        node_names = [node.name for node, prop in result]
        assert "root" in node_names
        assert "child2" in node_names

        # Find properties with integer values
        result = walker.find_properties(lambda prop: prop.value is not None and prop.value.type == DTValueType.INTEGER)
        assert len(result) == 1
        assert result[0][0] == self.child1

    def test_find_properties_by_name(self) -> None:
        """Test finding properties by name."""
        walker = DTWalker(self.root)

        result = walker.find_properties_by_name("compatible")
        assert len(result) == 2

        result = walker.find_properties_by_name("nonexistent")
        assert len(result) == 0


class TestDTMultiWalker:
    """Test DTMultiWalker class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Create multiple root nodes
        self.root1 = DTNode(name="root1")
        self.root1.add_property(DTProperty(name="compatible", value=DTValue.string("test,device1")))

        self.root2 = DTNode(name="root2")
        self.root2.add_property(DTProperty(name="compatible", value=DTValue.string("test,device2")))

        # Add children
        self.child1 = DTNode(name="shared_child", label="label1")
        self.child2 = DTNode(name="unique_child")

        self.root1.add_child(self.child1)
        self.root2.add_child(self.child2)

        self.roots = [self.root1, self.root2]

    def test_init(self) -> None:
        """Test DTMultiWalker initialization."""
        walker = DTMultiWalker(self.roots)
        assert walker.roots == self.roots

    def test_find_nodes_multi_root(self) -> None:
        """Test finding nodes across multiple roots."""
        walker = DTMultiWalker(self.roots)

        # Find all root nodes
        result = walker.find_nodes(lambda node: node.name.startswith("root"))
        assert len(result) == 2
        assert self.root1 in result
        assert self.root2 in result

        # Find shared child name
        result = walker.find_nodes(lambda node: node.name == "shared_child")
        assert len(result) == 1
        assert result[0] == self.child1

    def test_find_nodes_by_compatible_multi_root(self) -> None:
        """Test finding nodes by compatible across multiple roots."""
        walker = DTMultiWalker(self.roots)

        # Mock find_nodes_by_compatible for each root
        with (
            patch.object(self.root1, "find_nodes_by_compatible", return_value=[self.root1]) as mock1,
            patch.object(self.root2, "find_nodes_by_compatible", return_value=[self.root2]) as mock2,
        ):
            result = walker.find_nodes_by_compatible("test,device")

            mock1.assert_called_once_with("test,device")
            mock2.assert_called_once_with("test,device")
            assert result == [self.root1, self.root2]

    def test_find_nodes_by_name_multi_root(self) -> None:
        """Test finding nodes by name across multiple roots."""
        walker = DTMultiWalker(self.roots)

        result = walker.find_nodes_by_name("shared_child")
        assert len(result) == 1
        assert result[0] == self.child1

    def test_find_nodes_by_label_multi_root(self) -> None:
        """Test finding nodes by label across multiple roots."""
        walker = DTMultiWalker(self.roots)

        result = walker.find_nodes_by_label("label1")
        assert len(result) == 1
        assert result[0] == self.child1

    def test_find_nodes_by_path_pattern_multi_root(self) -> None:
        """Test finding nodes by path pattern across multiple roots."""
        walker = DTMultiWalker(self.roots)

        result = walker.find_nodes_by_path_pattern("root1")
        assert len(result) == 2  # root1 and its child
        assert self.root1 in result
        assert self.child1 in result

    def test_find_properties_multi_root(self) -> None:
        """Test finding properties across multiple roots."""
        walker = DTMultiWalker(self.roots)

        result = walker.find_properties(lambda prop: prop.name == "compatible")
        assert len(result) == 2
        node_names = [node.name for node, prop in result]
        assert "root1" in node_names
        assert "root2" in node_names

    def test_find_properties_by_name_multi_root(self) -> None:
        """Test finding properties by name across multiple roots."""
        walker = DTMultiWalker(self.roots)

        result = walker.find_properties_by_name("compatible")
        assert len(result) == 2


class TestBehaviorExtractor:
    """Test BehaviorExtractor class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.extractor = BehaviorExtractor()

        # Create test nodes with different behavior types
        self.hold_tap_node = DTNode(name="my_mt")
        self.hold_tap_node.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-hold-tap")))

        self.macro_node = DTNode(name="my_macro")
        self.macro_node.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-macro")))

        self.tap_dance_node = DTNode(name="my_td")
        self.tap_dance_node.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-tap-dance")))

        self.generic_behavior_node = DTNode(name="my_behavior")
        self.generic_behavior_node.add_property(
            DTProperty(name="compatible", value=DTValue.string("zmk,behavior-custom"))
        )

        self.non_behavior_node = DTNode(name="other")
        self.non_behavior_node.add_property(DTProperty(name="compatible", value=DTValue.string("other,device")))

    def test_init(self) -> None:
        """Test BehaviorExtractor initialization."""
        extractor = BehaviorExtractor()
        assert extractor.behaviors == []
        assert extractor.macros == []
        assert extractor.combos == []
        assert extractor.tap_dances == []
        assert extractor.hold_taps == []

    def test_visit_node_hold_tap(self) -> None:
        """Test visiting hold-tap behavior node."""
        self.extractor.visit_node(self.hold_tap_node)

        assert len(self.extractor.hold_taps) == 1
        assert self.hold_tap_node in self.extractor.hold_taps
        assert len(self.extractor.behaviors) == 1
        assert self.hold_tap_node in self.extractor.behaviors

    def test_visit_node_macro(self) -> None:
        """Test visiting macro behavior node."""
        self.extractor.visit_node(self.macro_node)

        assert len(self.extractor.macros) == 1
        assert self.macro_node in self.extractor.macros
        assert len(self.extractor.behaviors) == 1
        assert self.macro_node in self.extractor.behaviors

    def test_visit_node_tap_dance(self) -> None:
        """Test visiting tap-dance behavior node."""
        self.extractor.visit_node(self.tap_dance_node)

        assert len(self.extractor.tap_dances) == 1
        assert self.tap_dance_node in self.extractor.tap_dances
        assert len(self.extractor.behaviors) == 1
        assert self.tap_dance_node in self.extractor.behaviors

    def test_visit_node_generic_behavior(self) -> None:
        """Test visiting generic behavior node."""
        self.extractor.visit_node(self.generic_behavior_node)

        assert len(self.extractor.behaviors) == 1
        assert self.generic_behavior_node in self.extractor.behaviors
        assert len(self.extractor.hold_taps) == 0
        assert len(self.extractor.macros) == 0
        assert len(self.extractor.tap_dances) == 0

    def test_visit_node_no_compatible(self) -> None:
        """Test visiting node without compatible property."""
        node = DTNode(name="no_compat")
        self.extractor.visit_node(node)

        assert len(self.extractor.behaviors) == 0

    def test_visit_node_non_string_compatible(self) -> None:
        """Test visiting node with non-string compatible value."""
        node = DTNode(name="bad_compat")
        node.add_property(DTProperty(name="compatible", value=DTValue.integer(123)))
        self.extractor.visit_node(node)

        assert len(self.extractor.behaviors) == 0

    def test_visit_node_non_behavior(self) -> None:
        """Test visiting non-behavior node."""
        self.extractor.visit_node(self.non_behavior_node)
        assert len(self.extractor.behaviors) == 0

    def test_visit_property(self) -> None:
        """Test visiting property (should do nothing)."""
        prop = DTProperty(name="test", value=DTValue.string("value"))
        result = self.extractor.visit_property(prop)
        assert result is None

    def test_extract_combos(self) -> None:
        """Test extracting combo definitions."""
        root = DTNode(name="root")
        combos_section = DTNode(name="combos")

        # Create combo nodes
        combo1 = DTNode(name="combo1")
        combo2 = DTNode(name="combo2")

        combos_section.add_child(combo1)
        combos_section.add_child(combo2)
        root.add_child(combos_section)

        result = self.extractor.extract_combos(root)

        assert len(result) == 2
        assert combo1 in result
        assert combo2 in result
        assert self.extractor.combos == result


class TestMacroExtractor:
    """Test MacroExtractor class."""

    def test_init(self) -> None:
        """Test MacroExtractor initialization."""
        MacroExtractor()  # Should inherit from StructlogMixin (placeholder)

    def test_extract_macros(self) -> None:
        """Test extracting macro definitions."""
        extractor = MacroExtractor()
        root = DTNode(name="root")
        macros_section = DTNode(name="macros")

        # Create macro node with correct compatible
        macro1 = DTNode(name="macro1")
        macro1.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-macro")))

        # Create non-macro node in macros section
        non_macro = DTNode(name="not_macro")
        non_macro.add_property(DTProperty(name="compatible", value=DTValue.string("other,device")))

        # Create macro without compatible
        macro_no_compat = DTNode(name="macro_no_compat")

        macros_section.add_child(macro1)
        macros_section.add_child(non_macro)
        macros_section.add_child(macro_no_compat)
        root.add_child(macros_section)

        result = extractor.extract_macros(root)

        assert len(result) == 1
        assert macro1 in result
        assert non_macro not in result
        assert macro_no_compat not in result


class TestHoldTapExtractor:
    """Test HoldTapExtractor class."""

    def test_init(self) -> None:
        """Test HoldTapExtractor initialization."""
        HoldTapExtractor()  # Should inherit from StructlogMixin (placeholder)

    def test_extract_hold_taps(self) -> None:
        """Test extracting hold-tap definitions."""
        extractor = HoldTapExtractor()
        root = DTNode(name="root")
        behaviors_section = DTNode(name="behaviors")

        # Create hold-tap node
        hold_tap1 = DTNode(name="my_mt")
        hold_tap1.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-hold-tap")))

        # Create non-hold-tap behavior
        other_behavior = DTNode(name="other")
        other_behavior.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-macro")))

        behaviors_section.add_child(hold_tap1)
        behaviors_section.add_child(other_behavior)
        root.add_child(behaviors_section)

        result = extractor.extract_hold_taps(root)

        assert len(result) == 1
        assert hold_tap1 in result
        assert other_behavior not in result


class TestComboExtractor:
    """Test ComboExtractor class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.extractor = ComboExtractor(self.mock_logger)

    def test_init(self) -> None:
        """Test ComboExtractor initialization."""
        extractor = ComboExtractor()
        assert extractor.logger is None

        extractor_with_logger = ComboExtractor(self.mock_logger)
        assert extractor_with_logger.logger == self.mock_logger

    def test_extract_combos_valid(self) -> None:
        """Test extracting valid combo definitions."""
        root = DTNode(name="root")
        combos_section = DTNode(name="combos")

        # Create valid combo
        valid_combo = DTNode(name="combo1")
        valid_combo.add_property(DTProperty(name="key-positions", value=DTValue.array([0, 1])))
        valid_combo.add_property(DTProperty(name="bindings", value=DTValue.string("&kp A")))

        # Create invalid combo (missing key-positions)
        invalid_combo1 = DTNode(name="combo2")
        invalid_combo1.add_property(DTProperty(name="bindings", value=DTValue.string("&kp B")))

        # Create invalid combo (missing bindings)
        invalid_combo2 = DTNode(name="combo3")
        invalid_combo2.add_property(DTProperty(name="key-positions", value=DTValue.array([2, 3])))

        combos_section.add_child(valid_combo)
        combos_section.add_child(invalid_combo1)
        combos_section.add_child(invalid_combo2)
        root.add_child(combos_section)

        result = self.extractor.extract_combos(root)

        assert len(result) == 1
        assert valid_combo in result

        # Check warning calls for invalid combos
        assert self.mock_logger.warning.call_count == 2

    def test_extract_combos_no_logger(self) -> None:
        """Test extracting combos without logger."""
        extractor = ComboExtractor()
        root = DTNode(name="root")
        combos_section = DTNode(name="combos")

        # Create invalid combo
        invalid_combo = DTNode(name="combo1")
        invalid_combo.add_property(DTProperty(name="bindings", value=DTValue.string("&kp A")))

        combos_section.add_child(invalid_combo)
        root.add_child(combos_section)

        # Should not raise exception even with invalid combo and no logger
        result = extractor.extract_combos(root)
        assert len(result) == 0


class TestUniversalBehaviorExtractor:
    """Test UniversalBehaviorExtractor class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.extractor = UniversalBehaviorExtractor(self.mock_logger)

        # Create test nodes
        self.root = DTNode(name="root")

        # Create various behavior nodes
        self.hold_tap = DTNode(name="my_mt")
        self.hold_tap.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-hold-tap")))

        self.macro = DTNode(name="my_macro")
        self.macro.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-macro")))

        self.combo = DTNode(name="my_combo")
        self.combo.add_property(DTProperty(name="key-positions", value=DTValue.array([0, 1])))
        self.combo.add_property(DTProperty(name="bindings", value=DTValue.string("&kp A")))

        # Create combos section
        combos_section = DTNode(name="combos")
        combos_section.add_child(self.combo)
        self.root.add_child(combos_section)

        self.root.add_child(self.hold_tap)
        self.root.add_child(self.macro)

    def test_init(self) -> None:
        """Test UniversalBehaviorExtractor initialization."""
        extractor = UniversalBehaviorExtractor()
        assert extractor.logger is None
        assert len(extractor.behavior_patterns) > 0
        assert "hold_taps" in extractor.behavior_patterns
        assert extractor._behavior_cache == {}
        assert extractor.ast_converter is None

        extractor_with_logger = UniversalBehaviorExtractor(self.mock_logger)
        assert extractor_with_logger.logger == self.mock_logger

    def test_behavior_patterns(self) -> None:
        """Test behavior pattern definitions."""
        patterns = self.extractor.behavior_patterns

        assert "hold_taps" in patterns
        assert "zmk,behavior-hold-tap" in patterns["hold_taps"]
        assert "zmk,behavior-tap-hold" in patterns["hold_taps"]

        assert "macros" in patterns
        assert "zmk,behavior-macro" in patterns["macros"]

        assert "tap_dances" in patterns
        assert "zmk,behavior-tap-dance" in patterns["tap_dances"]

    def test_extract_all_behaviors(self) -> None:
        """Test extracting all behaviors from single root."""
        result = self.extractor.extract_all_behaviors(self.root)

        assert isinstance(result, dict)
        assert "hold_taps" in result
        assert "macros" in result
        assert "combos" in result

        assert len(result["hold_taps"]) == 1
        assert self.hold_tap in result["hold_taps"]

        assert len(result["macros"]) == 1
        assert self.macro in result["macros"]

        assert len(result["combos"]) == 1
        assert self.combo in result["combos"]

    def test_extract_all_behaviors_multiple(self) -> None:
        """Test extracting behaviors from multiple roots."""
        root2 = DTNode(name="root2")
        tap_dance = DTNode(name="my_td")
        tap_dance.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-tap-dance")))
        root2.add_child(tap_dance)

        result = self.extractor.extract_all_behaviors_multiple([self.root, root2])

        assert "tap_dances" in result
        assert len(result["tap_dances"]) == 1
        assert tap_dance in result["tap_dances"]

    def test_extract_behaviors_as_models(self) -> None:
        """Test extracting behaviors as model objects."""
        # Mock the AST converter
        mock_converter = Mock()
        mock_converter.defines = {}
        mock_converter.convert_hold_tap_node.return_value = Mock()
        mock_converter.convert_macro_node.return_value = Mock()
        mock_converter.convert_combo_node.return_value = Mock()
        mock_converter.convert_tap_dance_node.return_value = None
        mock_converter.convert_sticky_key_node.return_value = None
        mock_converter.convert_caps_word_node.return_value = None
        mock_converter.convert_mod_morph_node.return_value = None
        mock_converter.convert_input_listener_node.return_value = None

        with patch(
            "zmk_layout.parsers.ast_behavior_converter.create_ast_behavior_converter", return_value=mock_converter
        ):
            result = self.extractor.extract_behaviors_as_models([self.root])

        assert isinstance(result, dict)
        assert "hold_taps" in result
        assert "macros" in result
        assert "combos" in result

        assert len(result["hold_taps"]) == 1
        assert len(result["macros"]) == 1
        assert len(result["combos"]) == 1

        # Verify converter was called
        mock_converter.convert_hold_tap_node.assert_called_once()
        mock_converter.convert_macro_node.assert_called_once()
        mock_converter.convert_combo_node.assert_called_once()

    def test_extract_behaviors_as_models_with_defines(self) -> None:
        """Test extracting behaviors with defines update."""
        defines = {"TEST": "value"}
        mock_converter = Mock()
        mock_converter.defines = {"OLD": "value"}

        # Mock all conversion methods to return None for simplicity
        for method_name in [
            "convert_hold_tap_node",
            "convert_macro_node",
            "convert_combo_node",
            "convert_tap_dance_node",
            "convert_sticky_key_node",
            "convert_caps_word_node",
            "convert_mod_morph_node",
            "convert_input_listener_node",
        ]:
            setattr(mock_converter, method_name, Mock(return_value=None))

        # Set up existing converter to test the update path
        self.extractor.ast_converter = mock_converter

        self.extractor.extract_behaviors_as_models([self.root], defines=defines)

        # Verify defines were updated
        assert mock_converter.defines == defines

    def test_extract_behaviors_as_models_reuse_converter(self) -> None:
        """Test reusing existing converter."""
        mock_converter = Mock()
        mock_converter.defines = {"OLD": "value"}
        self.extractor.ast_converter = mock_converter

        # Mock all conversion methods
        for method_name in [
            "convert_hold_tap_node",
            "convert_macro_node",
            "convert_combo_node",
            "convert_tap_dance_node",
            "convert_sticky_key_node",
            "convert_caps_word_node",
            "convert_mod_morph_node",
            "convert_input_listener_node",
        ]:
            setattr(mock_converter, method_name, Mock(return_value=None))

        new_defines = {"NEW": "value"}
        self.extractor.extract_behaviors_as_models([self.root], defines=new_defines)

        # Verify defines were updated
        assert mock_converter.defines == new_defines

    def test_is_behavior_compatible(self) -> None:
        """Test behavior compatible string detection."""
        assert self.extractor._is_behavior_compatible("zmk,behavior-hold-tap")
        assert self.extractor._is_behavior_compatible("zmk,behavior-macro")
        assert self.extractor._is_behavior_compatible("zmk,combo-test")
        assert not self.extractor._is_behavior_compatible("other,device")

    def test_categorize_behavior(self) -> None:
        """Test behavior categorization."""
        assert self.extractor._categorize_behavior("zmk,behavior-hold-tap") == "hold_taps"
        assert self.extractor._categorize_behavior("zmk,behavior-macro") == "macros"
        assert self.extractor._categorize_behavior("zmk,behavior-tap-dance") == "tap_dances"
        assert self.extractor._categorize_behavior("zmk,behavior-unknown") == "other_behaviors"

    def test_is_valid_combo(self) -> None:
        """Test combo validation."""
        valid_combo = DTNode(name="combo")
        valid_combo.add_property(DTProperty(name="key-positions", value=DTValue.array([0, 1])))
        valid_combo.add_property(DTProperty(name="bindings", value=DTValue.string("&kp A")))

        invalid_combo = DTNode(name="combo")
        invalid_combo.add_property(DTProperty(name="key-positions", value=DTValue.array([0, 1])))

        assert self.extractor._is_valid_combo(valid_combo)
        assert not self.extractor._is_valid_combo(invalid_combo)

    def test_extract_combos_enhanced(self) -> None:
        """Test enhanced combo extraction."""
        # This tests the multi-method combo detection
        result = self.extractor._extract_combos_enhanced([self.root])
        assert len(result) == 1
        assert self.combo in result

    def test_detect_advanced_patterns(self) -> None:
        """Test advanced pattern detection."""
        # Create nodes with advanced patterns
        input_listener = DTNode(name="mouse_input_listener")
        sensor_node = DTNode(name="sensor")
        sensor_node.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-sensor-rotate")))

        rgb_node = DTNode(name="rgb_ug")
        mouse_node = DTNode(name="mmv")

        root = DTNode(name="root")
        root.add_child(input_listener)
        root.add_child(sensor_node)
        root.add_child(rgb_node)
        root.add_child(mouse_node)

        result = self.extractor.detect_advanced_patterns([root])

        assert "input_listeners" in result
        assert "sensor_configs" in result
        assert "underglow_configs" in result
        assert "mouse_configs" in result

        assert input_listener in result["input_listeners"]
        assert sensor_node in result["sensor_configs"]
        assert rgb_node in result["underglow_configs"]
        assert mouse_node in result["mouse_configs"]


class TestFactoryFunctions:
    """Test factory functions."""

    def test_create_behavior_extractor(self) -> None:
        """Test create_behavior_extractor factory."""
        extractor = create_behavior_extractor()
        assert isinstance(extractor, BehaviorExtractor)
        assert extractor.behaviors == []

    def test_create_universal_behavior_extractor(self) -> None:
        """Test create_universal_behavior_extractor factory."""
        mock_logger = Mock()

        extractor = create_universal_behavior_extractor()
        assert isinstance(extractor, UniversalBehaviorExtractor)
        assert extractor.logger is None

        extractor_with_logger = create_universal_behavior_extractor(mock_logger)
        assert extractor_with_logger.logger == mock_logger

    def test_create_universal_behavior_extractor_with_converter(self) -> None:
        """Test create_universal_behavior_extractor_with_converter factory."""
        mock_logger = Mock()
        mock_converter = Mock()

        with patch(
            "zmk_layout.parsers.ast_behavior_converter.create_ast_behavior_converter", return_value=mock_converter
        ):
            extractor = create_universal_behavior_extractor_with_converter()
            assert isinstance(extractor, UniversalBehaviorExtractor)
            assert extractor.ast_converter == mock_converter

            extractor_with_logger = create_universal_behavior_extractor_with_converter(mock_logger)
            assert extractor_with_logger.logger == mock_logger
            assert extractor_with_logger.ast_converter == mock_converter


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_walker_with_empty_root(self) -> None:
        """Test walker with empty root node."""
        root = DTNode(name="empty")
        walker = DTWalker(root)

        assert walker.find_nodes(lambda x: True) == [root]
        assert walker.find_nodes_by_name("nonexistent") == []
        assert walker.find_properties(lambda x: True) == []

    def test_multi_walker_with_empty_roots(self) -> None:
        """Test multi-walker with empty roots list."""
        walker = DTMultiWalker([])

        assert walker.find_nodes(lambda x: True) == []
        assert walker.find_properties(lambda x: True) == []

    def test_behavior_extractor_with_null_compatible_value(self) -> None:
        """Test behavior extractor with null compatible value."""
        extractor = BehaviorExtractor()
        node = DTNode(name="test")
        node.add_property(DTProperty(name="compatible", value=None))

        extractor.visit_node(node)
        assert len(extractor.behaviors) == 0

    def test_universal_extractor_logging(self) -> None:
        """Test logging in universal extractor."""
        mock_logger = Mock()
        extractor = UniversalBehaviorExtractor(mock_logger)

        root = DTNode(name="root")
        hold_tap = DTNode(name="mt")
        hold_tap.add_property(DTProperty(name="compatible", value=DTValue.string("zmk,behavior-hold-tap")))
        root.add_child(hold_tap)

        extractor.extract_all_behaviors(root)

        # Should log extraction summary
        mock_logger.debug.assert_called()

    def test_behavior_categorization_edge_cases(self) -> None:
        """Test edge cases in behavior categorization."""
        extractor = UniversalBehaviorExtractor()

        # Test empty string
        assert extractor._categorize_behavior("") == "other_behaviors"

        # Test partial matches
        assert extractor._categorize_behavior("zmk,behavior") == "other_behaviors"
        assert extractor._categorize_behavior("zmk,behavior-hold-tap-custom") == "hold_taps"

    def test_combo_extraction_with_no_combos_section(self) -> None:
        """Test combo extraction when no combos section exists."""
        extractor = UniversalBehaviorExtractor()
        root = DTNode(name="root")

        result = extractor._extract_combos_enhanced([root])
        assert result == []
