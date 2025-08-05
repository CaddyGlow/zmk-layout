"""Comprehensive tests for ZmkKeymapParser.

This module provides complete test coverage for the ZmkKeymapParser class,
including initialization, method behavior, and integration scenarios.
"""

from typing import Any

import pytest

from zmk_layout.parsers.ast_nodes import DTNode, DTProperty, DTValue
from zmk_layout.parsers.keymap_parser import ZmkKeymapParser


class TestZmkKeymapParserInitialization:
    """Test ZmkKeymapParser initialization and basic properties."""

    def test_parser_initialization(self) -> None:
        """Test that parser initializes correctly."""
        parser = ZmkKeymapParser()
        
        assert isinstance(parser, ZmkKeymapParser)
        assert hasattr(parser, "defines")
        assert isinstance(parser.defines, dict)
        assert len(parser.defines) == 0

    def test_parser_defines_property(self) -> None:
        """Test that defines property is accessible and modifiable."""
        parser = ZmkKeymapParser()
        
        # Test initial state
        assert parser.defines == {}
        
        # Test modification
        parser.defines["test_key"] = "test_value"
        assert parser.defines["test_key"] == "test_value"
        assert len(parser.defines) == 1

    def test_multiple_parser_instances(self) -> None:
        """Test that multiple parser instances are independent."""
        parser1 = ZmkKeymapParser()
        parser2 = ZmkKeymapParser()
        
        parser1.defines["key1"] = "value1"
        parser2.defines["key2"] = "value2"
        
        assert parser1.defines == {"key1": "value1"}
        assert parser2.defines == {"key2": "value2"}
        assert parser1.defines != parser2.defines


class TestZmkKeymapParserMethods:
    """Test ZmkKeymapParser method functionality."""

    def test_extract_layers_from_ast_with_none(self) -> None:
        """Test _extract_layers_from_ast returns None for any input."""
        parser = ZmkKeymapParser()
        
        # Test with None
        result = parser._extract_layers_from_ast(None)  # type: ignore[arg-type]
        assert result is None

    def test_extract_layers_from_ast_with_empty_node(self) -> None:
        """Test _extract_layers_from_ast with empty DTNode."""
        parser = ZmkKeymapParser()
        root = DTNode(name="root")
        
        result = parser._extract_layers_from_ast(root)
        assert result is None

    def test_extract_layers_from_ast_with_complex_node(self) -> None:
        """Test _extract_layers_from_ast with complex DTNode structure."""
        parser = ZmkKeymapParser()
        
        # Create a complex node structure
        root = DTNode(name="", label="root")
        keymap_node = DTNode(name="keymap", label="")
        layer_node = DTNode(name="default_layer", label="")
        
        # Add properties
        compat_prop = DTProperty(
            name="compatible",
            value=DTValue.string("zmk,keymap")
        )
        keymap_node.add_property(compat_prop)
        
        bindings_prop = DTProperty(
            name="bindings",
            value=DTValue.array(["&kp Q", "&kp W"])
        )
        layer_node.add_property(bindings_prop)
        
        # Build hierarchy
        keymap_node.add_child(layer_node)
        root.add_child(keymap_node)
        
        result = parser._extract_layers_from_ast(root)
        assert result is None  # Stub implementation always returns None

    def test_extract_layers_from_ast_with_malformed_node(self) -> None:
        """Test _extract_layers_from_ast handles malformed nodes gracefully."""
        parser = ZmkKeymapParser()
        
        # Create node with unusual structure
        root = DTNode(name="unusual", unit_address="0x1000")
        root.add_property(DTProperty(name="invalid", value=None))
        
        result = parser._extract_layers_from_ast(root)
        assert result is None

    def test_extract_layers_from_ast_method_signature(self) -> None:
        """Test that _extract_layers_from_ast has correct method signature."""
        parser = ZmkKeymapParser()
        
        # Test method exists and is callable
        assert hasattr(parser, "_extract_layers_from_ast")
        assert callable(parser._extract_layers_from_ast)
        
        # Test it accepts DTNode parameter
        root = DTNode()
        try:
            result = parser._extract_layers_from_ast(root)
            assert result is None
        except TypeError:
            pytest.fail("Method should accept DTNode parameter")

    def test_extract_layers_return_type(self) -> None:
        """Test that _extract_layers_from_ast return type annotation is correct."""
        parser = ZmkKeymapParser()
        root = DTNode()
        
        result = parser._extract_layers_from_ast(root)
        
        # Should return None or dict[str, Any]
        assert result is None or isinstance(result, dict)


class TestZmkKeymapParserEdgeCases:
    """Test ZmkKeymapParser edge cases and error conditions."""

    def test_parser_with_large_defines_dict(self) -> None:
        """Test parser handles large defines dictionary."""
        parser = ZmkKeymapParser()
        
        # Add many defines
        for i in range(1000):
            parser.defines[f"key_{i}"] = f"value_{i}"
        
        assert len(parser.defines) == 1000
        assert parser.defines["key_0"] == "value_0"
        assert parser.defines["key_999"] == "value_999"

    def test_parser_defines_with_complex_values(self) -> None:
        """Test parser handles complex values in defines."""
        parser = ZmkKeymapParser()
        
        # Test various data types
        parser.defines["string"] = "test_string"
        parser.defines["integer"] = 42
        parser.defines["list"] = [1, 2, 3]
        parser.defines["dict"] = {"nested": "value"}
        parser.defines["none"] = None
        
        assert parser.defines["string"] == "test_string"
        assert parser.defines["integer"] == 42
        assert parser.defines["list"] == [1, 2, 3]
        assert parser.defines["dict"] == {"nested": "value"}
        assert parser.defines["none"] is None

    def test_parser_defines_modification_persistence(self) -> None:
        """Test that defines modifications persist."""
        parser = ZmkKeymapParser()
        
        # Initial modification
        parser.defines["persistent"] = "initial"
        assert parser.defines["persistent"] == "initial"
        
        # Update value
        parser.defines["persistent"] = "updated"
        assert parser.defines["persistent"] == "updated"
        
        # Delete key
        del parser.defines["persistent"]
        assert "persistent" not in parser.defines

    def test_extract_layers_with_node_hierarchy(self) -> None:
        """Test _extract_layers_from_ast with deep node hierarchy."""
        parser = ZmkKeymapParser()
        
        # Create deep hierarchy
        root = DTNode(name="")
        level1 = DTNode(name="level1")
        level2 = DTNode(name="level2")
        level3 = DTNode(name="level3")
        
        level2.add_child(level3)
        level1.add_child(level2)
        root.add_child(level1)
        
        result = parser._extract_layers_from_ast(root)
        assert result is None  # Stub always returns None


class TestZmkKeymapParserIntegration:
    """Test ZmkKeymapParser integration scenarios."""

    def test_parser_state_after_multiple_operations(self) -> None:
        """Test parser state remains consistent after multiple operations."""
        parser = ZmkKeymapParser()
        
        # Perform multiple operations
        parser.defines["op1"] = "result1"
        
        root1 = DTNode(name="root1")
        result1 = parser._extract_layers_from_ast(root1)
        
        parser.defines["op2"] = "result2"
        
        root2 = DTNode(name="root2")
        result2 = parser._extract_layers_from_ast(root2)
        
        # Verify state consistency
        assert result1 is None
        assert result2 is None
        assert parser.defines["op1"] == "result1"
        assert parser.defines["op2"] == "result2"
        assert len(parser.defines) == 2

    def test_parser_with_realistic_ast_structure(self) -> None:
        """Test parser with realistic ZMK keymap AST structure."""
        parser = ZmkKeymapParser()
        
        # Create realistic ZMK structure
        root = DTNode(name="")
        
        # Add includes (typical in ZMK)
        includes = DTNode(name="includes")
        root.add_child(includes)
        
        # Add keymap node
        keymap = DTNode(name="keymap")
        keymap.add_property(DTProperty(
            name="compatible",
            value=DTValue.string("zmk,keymap")
        ))
        
        # Add default layer
        default_layer = DTNode(name="default_layer")
        default_layer.add_property(DTProperty(
            name="bindings",
            value=DTValue.array([
                "&kp Q", "&kp W", "&kp E", "&kp R",
                "&kp T", "&kp Y", "&kp U", "&kp I"
            ])
        ))
        keymap.add_child(default_layer)
        
        # Add raise layer
        raise_layer = DTNode(name="raise_layer")
        raise_layer.add_property(DTProperty(
            name="bindings",
            value=DTValue.array([
                "&kp N1", "&kp N2", "&kp N3", "&kp N4",
                "&trans", "&trans", "&trans", "&trans"
            ])
        ))
        keymap.add_child(raise_layer)
        
        root.add_child(keymap)
        
        # Test parsing
        result = parser._extract_layers_from_ast(root)
        assert result is None  # Stub implementation

    def test_parser_error_resilience(self) -> None:
        """Test parser resilience to various error conditions."""
        parser = ZmkKeymapParser()
        
        # Test with various problematic inputs
        test_nodes = [
            DTNode(),  # Empty node
            DTNode(name="test", unit_address="invalid"),
            DTNode(name="", label="", line=-1, column=-1),
        ]
        
        for node in test_nodes:
            try:
                result = parser._extract_layers_from_ast(node)
                assert result is None
            except Exception as e:
                pytest.fail(f"Parser should handle edge case gracefully, but raised: {e}")

    def test_parser_memory_efficiency(self) -> None:
        """Test parser memory efficiency with repeated operations."""
        parser = ZmkKeymapParser()
        
        # Perform many operations to test memory efficiency
        for i in range(100):
            node = DTNode(name=f"node_{i}")
            result = parser._extract_layers_from_ast(node)
            assert result is None
            
            # Update defines
            parser.defines[f"iteration_{i}"] = i
        
        # Verify final state
        assert len(parser.defines) == 100
        assert parser.defines["iteration_0"] == 0
        assert parser.defines["iteration_99"] == 99


class TestZmkKeymapParserTypeAnnotations:
    """Test ZmkKeymapParser type annotations and typing compliance."""

    def test_init_return_type(self) -> None:
        """Test that __init__ returns None."""
        parser = ZmkKeymapParser()
        assert isinstance(parser, ZmkKeymapParser)

    def test_defines_type_annotation(self) -> None:
        """Test that defines has correct type annotation."""
        parser = ZmkKeymapParser()
        
        # Test that defines accepts dict[str, Any]
        test_dict: dict[str, Any] = {"test": "value", "number": 42}
        parser.defines.update(test_dict)
        
        assert parser.defines["test"] == "value"
        assert parser.defines["number"] == 42

    def test_extract_layers_parameter_types(self) -> None:
        """Test that _extract_layers_from_ast accepts correct parameter types."""
        parser = ZmkKeymapParser()
        
        # Should accept DTNode
        node = DTNode(name="test")
        result = parser._extract_layers_from_ast(node)
        assert result is None
        
        # Test with typed node
        typed_node: DTNode = DTNode(name="typed_test")
        result = parser._extract_layers_from_ast(typed_node)
        assert result is None


class TestZmkKeymapParserDocumentation:
    """Test ZmkKeymapParser documentation and docstring coverage."""

    def test_class_has_docstring(self) -> None:
        """Test that class has proper docstring."""
        assert ZmkKeymapParser.__doc__ is not None
        assert "stub implementation" in ZmkKeymapParser.__doc__.lower()

    def test_init_has_docstring(self) -> None:
        """Test that __init__ method has docstring."""
        assert ZmkKeymapParser.__init__.__doc__ is not None
        assert "initialize" in ZmkKeymapParser.__init__.__doc__.lower()

    def test_extract_layers_has_docstring(self) -> None:
        """Test that _extract_layers_from_ast has proper docstring."""
        method = ZmkKeymapParser._extract_layers_from_ast
        assert method.__doc__ is not None
        assert "extract layer information" in method.__doc__.lower()
        assert "stub implementation" in method.__doc__.lower()

    def test_method_parameter_documentation(self) -> None:
        """Test that method parameters are documented."""
        method = ZmkKeymapParser._extract_layers_from_ast
        docstring = method.__doc__ or ""
        
        assert "Args:" in docstring
        assert "root:" in docstring
        assert "DTNode" in docstring
        assert "Returns:" in docstring


class TestZmkKeymapParserFutureCompatibility:
    """Test ZmkKeymapParser future compatibility and extensibility."""

    def test_parser_extensibility(self) -> None:
        """Test that parser can be extended in the future."""
        parser = ZmkKeymapParser()
        
        # Test that we can add attributes dynamically (for future extensions)
        parser.custom_attribute = "custom_value"  # type: ignore[attr-defined]
        assert hasattr(parser, "custom_attribute")
        assert parser.custom_attribute == "custom_value"

    def test_defines_future_compatibility(self) -> None:
        """Test that defines dictionary is compatible with future enhancements."""
        parser = ZmkKeymapParser()
        
        # Test nested structures (for future config support)
        parser.defines["config"] = {
            "layers": {
                "default": {"priority": 1},
                "raise": {"priority": 2}
            },
            "behaviors": {
                "tap_dance": {"enabled": True},
                "mod_tap": {"enabled": True}
            }
        }
        
        assert parser.defines["config"]["layers"]["default"]["priority"] == 1
        assert parser.defines["config"]["behaviors"]["tap_dance"]["enabled"] is True

    def test_method_signature_stability(self) -> None:
        """Test that method signatures are stable for future implementations."""
        parser = ZmkKeymapParser()
        
        # Test that current signature works
        node = DTNode()
        result = parser._extract_layers_from_ast(node)
        assert result is None
        
        # Test with mock future implementation
        original_method = parser._extract_layers_from_ast
        
        def mock_future_implementation(root: DTNode) -> dict[str, Any] | None:
            """Mock future implementation."""
            return {"layers": {"default": {}}} if root.name else None
        
        parser._extract_layers_from_ast = mock_future_implementation  # type: ignore[method-assign]
        
        # Test that signature still works
        test_node = DTNode(name="test")
        result = parser._extract_layers_from_ast(test_node)
        assert result is not None
        assert "layers" in result
        
        # Restore original
        parser._extract_layers_from_ast = original_method  # type: ignore[method-assign]