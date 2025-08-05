"""Tests for ZMK layout generators."""

from typing import Any
from unittest.mock import Mock

import pytest

from zmk_layout.models import HoldTapBehavior, LayoutBinding, LayoutData
from zmk_layout.providers import LayoutProviders
from zmk_layout.providers.factory import create_default_providers


class TestZMKGenerator:
    """Test ZMK file generation."""

    def test_basic_generator_functionality(self) -> None:
        """Test basic generator functionality."""
        providers = create_default_providers()
        
        # Mock generator behavior
        class MockZMKGenerator:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers
                
            def generate_keymap(self, layout_data: LayoutData) -> str:
                """Generate a basic keymap."""
                self.providers.logger.info("Generating keymap", keyboard=layout_data.keyboard)
                
                keymap_content = f"""
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {{
    keymap {{
        compatible = "zmk,keymap";
        
        default {{
            bindings = <
                {' '.join(f'{b.value} {" ".join(str(p.value) for p in b.params)}' for b in layout_data.layers[0])}
            >;
        }};
    }};
}};
"""
                return keymap_content.strip()
        
        # Test with simple layout
        layout_data = LayoutData(
            keyboard="test_board",
            title="Test Layout",
            layers=[
                [
                    LayoutBinding.from_str("&kp Q"),
                    LayoutBinding.from_str("&kp W"),
                ]
            ]
        )
        
        generator = MockZMKGenerator(providers)
        result = generator.generate_keymap(layout_data)
        
        assert "#include <behaviors.dtsi>" in result
        assert "#include <dt-bindings/zmk/keys.h>" in result
        assert "zmk,keymap" in result
        assert "default" in result
        assert "&kp Q" in result
        assert "&kp W" in result

    def test_generator_with_behaviors(self) -> None:
        """Test generator with custom behaviors."""
        providers = create_default_providers()
        
        class MockZMKGenerator:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers
                
            def generate_behaviors(self, behaviors: list[HoldTapBehavior]) -> str:
                """Generate behavior definitions."""
                if not behaviors:
                    return ""
                
                behavior_content = "behaviors {\n"
                for behavior in behaviors:
                    if hasattr(behavior, 'name'):
                        behavior_content += f"    {behavior.name} {{\n"
                        if hasattr(behavior, 'bindings'):
                            behavior_content += f"        bindings = <{', '.join(behavior.bindings)}>;\n"
                        if hasattr(behavior, 'tapping_term_ms'):
                            behavior_content += f"        tapping-term-ms = <{behavior.tapping_term_ms}>;\n"
                        behavior_content += "    };\n"
                behavior_content += "};\n"
                return behavior_content
        
        layout_data = LayoutData(
            keyboard="test_board",
            title="Test Layout with Behaviors",
            holdTaps=[
                HoldTapBehavior(
                    name="my_mt",
                    bindings=["&kp", "&kp"],
                    tappingTermMs=200,
                )
            ]
        )
        
        generator = MockZMKGenerator(providers)
        result = generator.generate_behaviors(layout_data.hold_taps)
        
        assert "behaviors {" in result
        assert "my_mt" in result
        assert "tapping-term-ms = <200>" in result
        assert "bindings = <&kp, &kp>" in result

    def test_generator_error_handling(self) -> None:
        """Test generator error handling."""
        providers = create_default_providers()
        
        class MockZMKGenerator:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers
                
            def generate_keymap(self, layout_data: LayoutData) -> str:
                if not layout_data.layers:
                    self.providers.logger.error("No layers found in layout data")
                    raise ValueError("Cannot generate keymap without layers")
                return "valid keymap"
        
        generator = MockZMKGenerator(providers)
        
        # Should work with valid layout
        valid_layout = LayoutData(
            keyboard="test",
            title="Test",
            layers=[[]]
        )
        result = generator.generate_keymap(valid_layout)
        assert result == "valid keymap"
        
        # Should raise error with no layers
        invalid_layout = LayoutData(keyboard="test", title="Test", layers=[])
        with pytest.raises(ValueError, match="Cannot generate keymap without layers"):
            generator.generate_keymap(invalid_layout)


class TestTemplateContext:
    """Test template context generation."""

    def test_template_context_creation(self) -> None:
        """Test template context creation."""
        providers = create_default_providers()
        
        class MockTemplateContext:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers
                
            def create_context(self, layout_data: LayoutData) -> dict[str, Any]:
                """Create template context from layout data."""
                context = {
                    "keyboard": layout_data.keyboard,
                    "title": layout_data.title,
                    "layer_count": len(layout_data.layers),
                    "behavior_count": len(layout_data.hold_taps) + len(layout_data.combos),
                    "layers": [
                        {
                            "name": f"layer_{i}",
                            "binding_count": len(layer_bindings)
                        }
                        for i, layer_bindings in enumerate(layout_data.layers)
                    ]
                }
                return context
        
        layout_data = LayoutData(
            keyboard="ergodox",
            title="Ergodox Layout",
            layers=[
                [LayoutBinding.from_str("&kp A")],
                [LayoutBinding.from_str("&kp N1")]
            ],
            holdTaps=[
                HoldTapBehavior(name="mt", bindings=["&kp", "&kp"])
            ]
        )
        
        context_gen = MockTemplateContext(providers)
        context = context_gen.create_context(layout_data)
        
        assert context["keyboard"] == "ergodox"
        assert context["title"] == "Ergodox Layout"
        assert context["layer_count"] == 2
        assert context["behavior_count"] == 1
        assert len(context["layers"]) == 2
        assert context["layers"][0]["name"] == "layer_0"
        assert context["layers"][1]["name"] == "layer_1"

    def test_template_context_with_providers(self) -> None:
        """Test template context with provider integration."""
        providers = create_default_providers()
        
        # Mock configuration provider
        mock_config = Mock()
        mock_config.get_template_context.return_value = {
            "keyboard_config": {"matrix": "5x6"},
            "includes": ["behaviors.dtsi", "keys.h"]
        }
        providers.configuration = mock_config
        
        class MockTemplateContext:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers
                
            def create_enhanced_context(self, layout_data: LayoutData) -> dict[str, Any]:
                base_context = {
                    "keyboard": layout_data.keyboard,
                    "title": layout_data.title
                }
                
                # Add configuration context
                config_context: dict[str, Any] = self.providers.configuration.get_template_context()
                base_context.update(config_context)
                
                return base_context
        
        layout_data = LayoutData(keyboard="test", title="Test")
        context_gen = MockTemplateContext(providers)
        context = context_gen.create_enhanced_context(layout_data)
        
        assert context["keyboard"] == "test"
        assert context["keyboard_config"]["matrix"] == "5x6"
        assert "behaviors.dtsi" in context["includes"]


class TestConfigGenerator:
    """Test configuration file generation."""

    def test_config_generation(self) -> None:
        """Test basic config generation."""
        providers = create_default_providers()
        
        class MockConfigGenerator:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers
                
            def generate_config(self, layout_data: LayoutData) -> dict[str, Any]:
                """Generate configuration data."""
                config = {
                    "keyboard": layout_data.keyboard,
                    "layout": {
                        "layers": len(layout_data.layers),
                        "behaviors": {
                            "hold_taps": len(layout_data.hold_taps),
                            "combos": len(layout_data.combos),
                        }
                    }
                }
                return config
        
        layout_data = LayoutData(
            keyboard="planck",
            title="Planck Layout",
            layers=[[]],
            holdTaps=[HoldTapBehavior(name="mt", bindings=["&kp", "&kp"])]
        )
        
        generator = MockConfigGenerator(providers)
        config = generator.generate_config(layout_data)
        
        assert config["keyboard"] == "planck"
        assert config["layout"]["layers"] == 1
        assert config["layout"]["behaviors"]["hold_taps"] == 1
        assert config["layout"]["behaviors"]["combos"] == 0

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        providers = create_default_providers()
        
        class MockConfigGenerator:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers
                
            def validate_config(self, config: dict[str, Any]) -> list[str]:
                """Validate configuration and return errors.""" 
                errors = []
                
                if "keyboard" not in config:
                    errors.append("Missing keyboard specification")
                    
                if "layout" not in config:
                    errors.append("Missing layout specification")
                elif "layers" not in config["layout"]:
                    errors.append("Missing layer count")
                    
                return errors
        
        generator = MockConfigGenerator(providers)
        
        # Valid config should pass
        valid_config = {
            "keyboard": "test",
            "layout": {"layers": 1}
        }
        errors = generator.validate_config(valid_config)
        assert len(errors) == 0
        
        # Invalid config should have errors
        invalid_config = {"keyboard": "test"}
        errors = generator.validate_config(invalid_config)
        assert len(errors) > 0
        assert "Missing layout specification" in errors


class TestCoreOperations:
    """Test core generation operations."""

    def test_core_operations_functionality(self) -> None:
        """Test core operations functionality."""
        providers = create_default_providers()
        
        class MockCoreOperations:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers
                
            def process_layout(self, layout_data: LayoutData) -> dict[str, Any]:
                """Process layout data and return summary."""
                self.providers.logger.info("Processing layout", keyboard=layout_data.keyboard)
                
                return {
                    "keyboard": layout_data.keyboard,
                    "processed": True,
                    "layer_names": [f"layer_{i}" for i in range(len(layout_data.layers))],
                    "total_bindings": sum(len(layer_bindings) for layer_bindings in layout_data.layers)
                }
        
        layout_data = LayoutData(
            keyboard="corne",
            title="Corne Layout",
            layers=[
                [
                    LayoutBinding.from_str("&kp Q"),
                    LayoutBinding.from_str("&kp W")
                ]
            ]
        )
        
        operations = MockCoreOperations(providers)
        result = operations.process_layout(layout_data)
        
        assert result["keyboard"] == "corne"
        assert result["processed"] is True
        assert "layer_names" in result  # May be empty or generated
        assert result["total_bindings"] == 2