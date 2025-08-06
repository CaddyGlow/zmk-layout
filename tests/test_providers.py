"""Tests for provider protocols and default implementations."""

from pathlib import Path

from zmk_layout.providers import (
    ConfigurationProvider,
    LayoutLogger,
    LayoutProviders,
    TemplateProvider,
)
from zmk_layout.providers.factory import (
    DefaultConfigurationProvider,
    DefaultLogger,
    DefaultTemplateProvider,
    create_default_providers,
)


class TestProviderProtocols:
    """Test that provider protocols define the expected interface."""

    def test_configuration_provider_protocol(self) -> None:
        """Test ConfigurationProvider protocol methods."""
        # Protocol methods should exist
        assert hasattr(ConfigurationProvider, "get_behavior_definitions")
        assert hasattr(ConfigurationProvider, "get_include_files")
        assert hasattr(ConfigurationProvider, "get_validation_rules")
        assert hasattr(ConfigurationProvider, "get_template_context")
        assert hasattr(ConfigurationProvider, "get_kconfig_options")
        assert hasattr(ConfigurationProvider, "get_formatting_config")

    def test_template_provider_protocol(self) -> None:
        """Test TemplateProvider protocol methods."""
        assert hasattr(TemplateProvider, "render_string")
        assert hasattr(TemplateProvider, "has_template_syntax")
        assert hasattr(TemplateProvider, "escape_content")

    def test_layout_logger_protocol(self) -> None:
        """Test LayoutLogger protocol methods."""
        assert hasattr(LayoutLogger, "info")
        assert hasattr(LayoutLogger, "error")
        assert hasattr(LayoutLogger, "warning")
        assert hasattr(LayoutLogger, "debug")
        assert hasattr(LayoutLogger, "exception")


class TestDefaultProviders:
    """Test default provider implementations."""

    def test_default_logger(self) -> None:
        """Test default logger implementation."""
        logger = DefaultLogger("test")

        # Should not raise exceptions
        logger.info("test message")
        logger.error("test error")
        logger.warning("test warning")
        logger.debug("test debug")
        logger.exception("test exception")

    def test_default_template_provider(self) -> None:
        """Test default template provider."""
        provider = DefaultTemplateProvider()

        # Test basic rendering
        result = provider.render_string("Hello {name}!", {"name": "World"})
        assert result == "Hello World!"

        # Test template syntax detection
        assert provider.has_template_syntax("Hello {name}")
        assert provider.has_template_syntax("Hello {{name}}")
        assert provider.has_template_syntax("Hello ${name}")
        assert not provider.has_template_syntax("Hello World")

        # Test escaping
        escaped = provider.escape_content("Hello {name}")
        assert "{" in escaped and "}" in escaped

    def test_default_configuration_provider(self) -> None:
        """Test default configuration provider."""
        provider = DefaultConfigurationProvider()

        # Test behavior definitions
        behaviors = provider.get_behavior_definitions()
        assert len(behaviors) > 0
        assert any(b.name == "kp" for b in behaviors)

        # Test include files
        includes = provider.get_include_files()
        assert len(includes) > 0
        assert any("keys.h" in inc for inc in includes)

        # Test validation rules
        rules = provider.get_validation_rules()
        assert "max_layers" in rules
        assert "key_positions" in rules
        assert "supported_behaviors" in rules

        # Test template context
        context = provider.get_template_context()
        assert "keyboard_name" in context
        assert "firmware_version" in context

        # Test kconfig options
        kconfig = provider.get_kconfig_options()
        assert isinstance(kconfig, dict)

        # Test formatting config
        formatting = provider.get_formatting_config()
        assert "key_gap" in formatting
        assert "base_indent" in formatting


class TestLayoutProviders:
    """Test LayoutProviders dataclass."""

    def test_layout_providers_creation(self) -> None:
        """Test creating LayoutProviders instance."""
        providers = create_default_providers()

        assert isinstance(providers, LayoutProviders)
        assert hasattr(providers, "configuration")
        assert hasattr(providers, "template")
        assert hasattr(providers, "logger")

        # Test that all providers implement the expected interfaces
        assert hasattr(providers.configuration, "get_behavior_definitions")
        assert hasattr(providers.template, "render_string")
        assert hasattr(providers.logger, "info")

    def test_providers_functionality(self, tmp_path: Path) -> None:
        """Test that providers work together."""
        providers = create_default_providers()

        # Test configuration
        behaviors = providers.configuration.get_behavior_definitions()
        assert len(behaviors) > 0

        # Test templating
        template_result = providers.template.render_string(
            "Keyboard: {name}", {"name": "Test"}
        )
        assert template_result == "Keyboard: Test"

        # Test file operations using pathlib directly
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        content = test_file.read_text()
        assert content == "test content"

        # Test logging (should not raise)
        providers.logger.info("Test message")
        providers.logger.error("Test error")
