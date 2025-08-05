"""Tests for provider protocols and default implementations."""

from zmk_layout.providers import (
    ConfigurationProvider,
    FileProvider,
    LayoutLogger,
    LayoutProviders,
    TemplateProvider,
)
from zmk_layout.providers.factory import (
    DefaultConfigurationProvider,
    DefaultFileProvider,
    DefaultLogger,
    DefaultTemplateProvider,
    create_default_providers,
)


class TestProviderProtocols:
    """Test that provider protocols define the expected interface."""

    def test_configuration_provider_protocol(self):
        """Test ConfigurationProvider protocol methods."""
        # Protocol methods should exist
        assert hasattr(ConfigurationProvider, 'get_behavior_definitions')
        assert hasattr(ConfigurationProvider, 'get_include_files')
        assert hasattr(ConfigurationProvider, 'get_validation_rules')
        assert hasattr(ConfigurationProvider, 'get_template_context')
        assert hasattr(ConfigurationProvider, 'get_kconfig_options')
        assert hasattr(ConfigurationProvider, 'get_formatting_config')

    def test_template_provider_protocol(self):
        """Test TemplateProvider protocol methods."""
        assert hasattr(TemplateProvider, 'render_string')
        assert hasattr(TemplateProvider, 'has_template_syntax')
        assert hasattr(TemplateProvider, 'escape_content')

    def test_layout_logger_protocol(self):
        """Test LayoutLogger protocol methods."""
        assert hasattr(LayoutLogger, 'info')
        assert hasattr(LayoutLogger, 'error')
        assert hasattr(LayoutLogger, 'warning')
        assert hasattr(LayoutLogger, 'debug')
        assert hasattr(LayoutLogger, 'exception')

    def test_file_provider_protocol(self):
        """Test FileProvider protocol methods."""
        assert hasattr(FileProvider, 'read_text')
        assert hasattr(FileProvider, 'write_text')
        assert hasattr(FileProvider, 'exists')
        assert hasattr(FileProvider, 'mkdir')


class TestDefaultProviders:
    """Test default provider implementations."""

    def test_default_logger(self):
        """Test default logger implementation."""
        logger = DefaultLogger("test")
        
        # Should not raise exceptions
        logger.info("test message")
        logger.error("test error")
        logger.warning("test warning")
        logger.debug("test debug")
        logger.exception("test exception")

    def test_default_template_provider(self):
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

    def test_default_configuration_provider(self):
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

    def test_default_file_provider(self, tmp_path):
        """Test default file provider."""
        provider = DefaultFileProvider()
        
        test_file = tmp_path / "test.txt"
        test_content = "Hello, World!"
        
        # Test write
        provider.write_text(test_file, test_content)
        
        # Test exists
        assert provider.exists(test_file)
        assert not provider.exists(tmp_path / "nonexistent.txt")
        
        # Test read
        read_content = provider.read_text(test_file)
        assert read_content == test_content
        
        # Test mkdir
        new_dir = tmp_path / "new_directory"
        provider.mkdir(new_dir)
        assert provider.exists(new_dir)


class TestLayoutProviders:
    """Test LayoutProviders dataclass."""

    def test_layout_providers_creation(self):
        """Test creating LayoutProviders instance."""
        providers = create_default_providers()
        
        assert isinstance(providers, LayoutProviders)
        assert hasattr(providers, 'configuration')
        assert hasattr(providers, 'template')
        assert hasattr(providers, 'logger')
        assert hasattr(providers, 'file')
        
        # Test that all providers implement the expected interfaces
        assert hasattr(providers.configuration, 'get_behavior_definitions')
        assert hasattr(providers.template, 'render_string')
        assert hasattr(providers.logger, 'info')
        assert hasattr(providers.file, 'read_text')

    def test_providers_functionality(self, tmp_path):
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
        
        # Test file operations
        test_file = tmp_path / "test.txt"
        providers.file.write_text(test_file, "test content")
        assert providers.file.exists(test_file)
        content = providers.file.read_text(test_file)
        assert content == "test content"
        
        # Test logging (should not raise)
        providers.logger.info("Test message")
        providers.logger.error("Test error")