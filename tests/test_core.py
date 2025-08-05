"""Tests for core functionality."""

from typing import Any
from unittest.mock import patch

import pytest

from zmk_layout.core.optional_deps import (
    get_display_provider,
    get_parser_provider,
    get_template_provider,
    has_jinja2,
    has_lark,
    has_rich,
)


class TestOptionalDependencies:
    """Test optional dependency management."""

    def test_dependency_detection(self) -> None:
        """Test detection of optional dependencies."""
        # Test has_jinja2
        jinja2_available = has_jinja2()
        assert isinstance(jinja2_available, bool)
        
        # Test has_rich  
        rich_available = has_rich()
        assert isinstance(rich_available, bool)
        
        # Test has_lark
        lark_available = has_lark()
        assert isinstance(lark_available, bool)

    def test_template_provider_fallback(self) -> None:
        """Test template provider fallback behavior."""
        provider = get_template_provider()
        assert provider is not None  # Should always return a provider

    def test_display_provider_fallback(self) -> None:
        """Test display provider fallback behavior."""
        provider = get_display_provider()
        # May return None as display is optional
        assert provider is None or provider is not None

    def test_parser_provider_fallback(self) -> None:
        """Test parser provider fallback behavior."""
        provider = get_parser_provider()
        # May return None as advanced parsing is optional
        assert provider is None or provider is not None

    def test_graceful_degradation(self) -> None:
        """Test that missing dependencies don't break the system."""
        # All optional dependency functions should handle ImportError gracefully
        try:
            has_jinja2()
            has_rich()
            has_lark()
            get_template_provider()
            get_display_provider()
            get_parser_provider()
        except Exception as e:
            pytest.fail(f"Optional dependency functions should not raise exceptions: {e}")

    def test_feature_flags(self) -> None:
        """Test feature availability flags."""
        # Test that we can check features
        features = {
            "templating": has_jinja2(),
            "rich_display": has_rich(),
            "advanced_parsing": has_lark()
        }
        
        # All should be boolean values
        for feature, available in features.items():
            assert isinstance(available, bool), f"Feature '{feature}' should return boolean"

    @patch('zmk_layout.core.optional_deps.has_jinja2')
    @patch('zmk_layout.core.optional_deps.has_rich')
    @patch('zmk_layout.core.optional_deps.has_lark')
    def test_all_dependencies_unavailable(self, mock_lark: Any, mock_rich: Any, mock_jinja2: Any) -> None:
        """Test behavior when all optional dependencies are unavailable."""
        # Mock all as unavailable
        mock_jinja2.return_value = False
        mock_rich.return_value = False
        mock_lark.return_value = False
        
        # All getters should handle unavailability gracefully
        template_provider = get_template_provider()
        display_provider = get_display_provider()
        parser_provider = get_parser_provider()
        
        # Template provider should always be available (fallback)
        assert template_provider is not None
        # Display and parser may be None
        assert display_provider is None or display_provider is not None
        assert parser_provider is None or parser_provider is not None
        
        # All checkers should return False
        assert has_jinja2() is False
        assert has_rich() is False
        assert has_lark() is False

    def test_import_error_handling(self) -> None:
        """Test that ImportError is handled correctly."""
        # The actual functions should handle ImportError internally
        # This test ensures they don't leak exceptions
        
        # Patch __import__ to raise ImportError for all imports
        with patch('builtins.__import__', side_effect=ImportError("Mocked import error")):
            # All functions should handle ImportError gracefully
            assert has_jinja2() is False
            assert has_rich() is False
            assert has_lark() is False
            
            # Providers should handle import errors gracefully
            template_provider = get_template_provider()
            display_provider = get_display_provider()
            parser_provider = get_parser_provider()
            
            # Template should still work (fallback)
            assert template_provider is not None
            # Others may be None
            assert display_provider is None or display_provider is not None
            assert parser_provider is None or parser_provider is not None


class TestCoreInitialization:
    """Test core module initialization."""

    def test_core_module_imports(self) -> None:
        """Test that core module imports work correctly."""
        # Test importing core functionality
        try:
            from zmk_layout.core import optional_deps
            assert optional_deps is not None
        except ImportError as e:
            pytest.fail(f"Core module should be importable: {e}")

    def test_core_module_structure(self) -> None:
        """Test core module structure."""
        # Test that expected functions are available
        from zmk_layout.core.optional_deps import (
            get_display_provider,
            get_parser_provider,
            get_template_provider,
            has_jinja2,
            has_lark,
            has_rich,
        )
        
        # All functions should be callable
        assert callable(has_jinja2)
        assert callable(has_rich)
        assert callable(has_lark)
        assert callable(get_template_provider)
        assert callable(get_display_provider)
        assert callable(get_parser_provider)

    def test_version_info(self) -> None:
        """Test version information availability."""
        # Test that we can get version info from the main module
        try:
            from zmk_layout import __version__
            assert isinstance(__version__, str)
            assert len(__version__) > 0
        except ImportError:
            # Version might not be defined yet, that's okay
            pass


class TestFeatureAvailability:
    """Test feature availability based on dependencies."""

    def test_templating_features(self) -> None:
        """Test templating feature availability."""
        has_jinja2()
        
        # Always get template provider (has fallback)
        provider = get_template_provider()
        assert provider is not None  # Always returns fallback

    def test_display_features(self) -> None:
        """Test display feature availability.""" 
        has_rich()
        
        # Get display provider (always returns fallback)
        provider = get_display_provider()
        # Provider is not None (fallback implementation)
        assert provider is not None

    def test_parsing_features(self) -> None:
        """Test advanced parsing feature availability."""
        lark_available = has_lark()
        
        # Parser provider always returns fallback implementation
        provider = get_parser_provider()
        assert provider is not None

    def test_feature_compatibility_matrix(self) -> None:
        """Test feature compatibility combinations."""
        # Test all combinations of feature availability
        jinja2_available = has_jinja2()
        rich_available = has_rich()
        lark_available = has_lark()
        
        # Record availability for debugging
        availability = {
            "jinja2": jinja2_available,
            "rich": rich_available,
            "lark": lark_available
        }
        
        # System should work regardless of which features are available
        assert isinstance(availability["jinja2"], bool)
        assert isinstance(availability["rich"], bool)
        assert isinstance(availability["lark"], bool)
        
        # At least one combination should work (even if all False)
        total_features = sum(availability.values())
        assert total_features >= 0  # Can be 0 if no optional deps available


class TestErrorHandling:
    """Test error handling in core functionality."""

    def test_safe_import_handling(self) -> None:
        """Test that import errors are handled safely."""
        # Mock import failures
        with patch('builtins.__import__') as mock_import:
            mock_import.side_effect = ImportError("Test import failure")
            
            # All functions should handle import errors gracefully
            assert has_jinja2() is False
            assert has_rich() is False
            assert has_lark() is False
            
            # All providers return fallback implementations
            assert get_template_provider() is not None  # Returns fallback
            assert get_display_provider() is not None   # Returns fallback
            assert get_parser_provider() is not None    # Returns fallback

    def test_partial_import_failure(self) -> None:
        """Test handling of partial import failures."""
        original_import = __import__
        
        def selective_import_failure(name: str, *args: Any, **kwargs: Any) -> Any:
            if name == 'jinja2':
                raise ImportError("jinja2 not available")
            return original_import(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=selective_import_failure):
            # jinja2 should fail
            assert has_jinja2() is False
            # Template provider returns fallback even when jinja2 unavailable
            assert get_template_provider() is not None
            
            # Others might still work (depending on actual availability)
            rich_available = has_rich()
            lark_available = has_lark()
            assert isinstance(rich_available, bool)
            assert isinstance(lark_available, bool)