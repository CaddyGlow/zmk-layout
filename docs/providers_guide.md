# Provider Implementation Guide

## Overview

The zmk-layout library uses a provider pattern to abstract all external dependencies, enabling maximum flexibility and portability. This guide provides comprehensive documentation for implementing each provider interface, with examples and best practices.

## Table of Contents

1. [Provider Architecture](#provider-architecture)
2. [ConfigurationProvider](#configurationprovider)
3. [TemplateProvider](#templateprovider)
4. [LoggerProvider](#loggerprovider)
5. **Note**: FileProvider removed - file I/O delegated to consuming application
6. [Provider Factory](#provider-factory)
7. [Validation & Testing](#validation--testing)
8. [Best Practices](#best-practices)
9. [Reference Implementations](#reference-implementations)

## Provider Architecture

### Design Principles

The provider pattern in zmk-layout follows these principles:

1. **Protocol-Based**: Uses Python protocols (PEP 544) for type safety without inheritance
2. **Dependency Injection**: All dependencies injected at construction time
3. **Immutable**: Providers should be immutable after creation
4. **Lazy Loading**: Resources loaded only when needed
5. **Graceful Degradation**: Missing optional providers handled gracefully

### Provider Structure

```python
from typing import Protocol, Any
from pathlib import Path

# All providers are protocols (interfaces)
class SomeProvider(Protocol):
    """Protocol defining required methods."""
    
    def required_method(self) -> Any:
        """This method must be implemented."""
        ...
    
    def another_method(self, param: str) -> bool:
        """Another required method."""
        ...
```

### Provider Aggregation

All providers are aggregated in the `LayoutProviders` dataclass:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class LayoutProviders:
    """Container for all layout providers."""
    
    configuration: ConfigurationProvider
    template: TemplateProvider
    logger: LayoutLogger
    
    def validate(self) -> list[str]:
        """Validate all providers implement required methods."""
        errors = []
        # Validation logic
        return errors
```

## ConfigurationProvider

The `ConfigurationProvider` supplies keyboard-specific configuration, behaviors, and validation rules.

### Protocol Definition

```python
from typing import Protocol, Any

class ConfigurationProvider(Protocol):
    """Provider for keyboard configuration and behavior definitions."""
    
    def get_behavior_definitions(self) -> list[dict[str, Any]]:
        """
        Get all available ZMK behaviors for validation.
        
        Returns:
            List of behavior definitions with structure:
            [
                {
                    "name": "mt",
                    "type": "hold-tap",
                    "params": ["hold", "tap"],
                    "description": "Mod-tap behavior"
                },
                ...
            ]
        """
        ...
    
    def get_include_files(self) -> list[str]:
        """
        Get required include files for ZMK compilation.
        
        Returns:
            List of include paths:
            ["behaviors.dtsi", "keys.h", "custom.dtsi"]
        """
        ...
    
    def get_validation_rules(self) -> dict[str, Any]:
        """
        Get keyboard-specific validation rules.
        
        Returns:
            Dictionary with validation parameters:
            {
                "key_count": 42,
                "layer_limit": 10,
                "combo_limit": 32,
                "macro_limit": 16,
                "hold_tap_limit": 8
            }
        """
        ...
    
    def get_template_context(self) -> dict[str, Any]:
        """
        Get context data for template processing.
        
        Returns:
            Template context dictionary:
            {
                "keyboard": "crkbd",
                "manufacturer": "foostan",
                "layout": {...},
                "features": ["oled", "rgb"]
            }
        """
        ...
    
    def get_kconfig_options(self) -> dict[str, Any]:
        """
        Get Kconfig options for the keyboard.
        
        Returns:
            Kconfig settings:
            {
                "CONFIG_ZMK_SLEEP": True,
                "CONFIG_BT_MAX_CONN": 5
            }
        """
        ...
    
    def get_formatting_options(self) -> dict[str, Any]:
        """
        Get code formatting preferences.
        
        Returns:
            Formatting options:
            {
                "indent_size": 4,
                "use_tabs": False,
                "max_line_length": 120
            }
        """
        ...
```

### Implementation Example

```python
class SimpleConfigurationProvider:
    """Simple configuration provider implementation."""
    
    def __init__(self, keyboard: str = "crkbd"):
        self.keyboard = keyboard
        self._load_config()
    
    def _load_config(self):
        """Load configuration from files or defaults."""
        self.behaviors = self._default_behaviors()
        self.rules = self._default_rules()
    
    def get_behavior_definitions(self) -> list[dict[str, Any]]:
        return self.behaviors
    
    def get_include_files(self) -> list[str]:
        return [
            "behaviors.dtsi",
            "keys.h",
            f"{self.keyboard}.dtsi"
        ]
    
    def get_validation_rules(self) -> dict[str, Any]:
        return self.rules
    
    def get_template_context(self) -> dict[str, Any]:
        return {
            "keyboard": self.keyboard,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    def get_kconfig_options(self) -> dict[str, Any]:
        return {
            "CONFIG_ZMK_SLEEP": True,
            "CONFIG_ZMK_IDLE_SLEEP_TIMEOUT": 900000
        }
    
    def get_formatting_options(self) -> dict[str, Any]:
        return {
            "indent_size": 4,
            "use_tabs": False,
            "max_line_length": 100
        }
    
    def _default_behaviors(self) -> list[dict[str, Any]]:
        """Get default ZMK behaviors."""
        return [
            {"name": "kp", "type": "key-press", "params": ["keycode"]},
            {"name": "mt", "type": "mod-tap", "params": ["hold", "tap"]},
            {"name": "lt", "type": "layer-tap", "params": ["layer", "tap"]},
            # ... more behaviors
        ]
    
    def _default_rules(self) -> dict[str, Any]:
        """Get default validation rules."""
        keyboards = {
            "crkbd": {"key_count": 42, "layers": 10},
            "sofle": {"key_count": 58, "layers": 10},
            "glove80": {"key_count": 80, "layers": 10},
        }
        return keyboards.get(self.keyboard, {"key_count": 60, "layers": 10})
```

### Database-Backed Implementation

```python
class DatabaseConfigurationProvider:
    """Configuration provider backed by database."""
    
    def __init__(self, db_connection, keyboard_id: str):
        self.db = db_connection
        self.keyboard_id = keyboard_id
        self._cache = {}
    
    def get_behavior_definitions(self) -> list[dict[str, Any]]:
        if "behaviors" not in self._cache:
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT * FROM behaviors WHERE keyboard_id = ?",
                (self.keyboard_id,)
            )
            self._cache["behaviors"] = [
                dict(row) for row in cursor.fetchall()
            ]
        return self._cache["behaviors"]
    
    # ... implement other methods
```

## TemplateProvider

The `TemplateProvider` handles template rendering for generating ZMK configuration files.

### Protocol Definition

```python
class TemplateProvider(Protocol):
    """Provider for template rendering operations."""
    
    def render_string(self, template: str, context: dict[str, Any]) -> str:
        """
        Render a template string with given context.
        
        Args:
            template: Template string with placeholders
            context: Variables for template substitution
            
        Returns:
            Rendered string
            
        Example:
            render_string("Hello {{name}}", {"name": "World"})
            # Returns: "Hello World"
        """
        ...
    
    def render_file(self, template_path: str, context: dict[str, Any]) -> str:
        """
        Render a template file.
        
        Args:
            template_path: Path to template file
            context: Template variables
            
        Returns:
            Rendered content
        """
        ...
    
    def has_template_syntax(self, content: str) -> bool:
        """
        Check if content contains template syntax.
        
        Args:
            content: String to check
            
        Returns:
            True if template syntax detected
            
        Example:
            has_template_syntax("Hello {{name}}")  # True
            has_template_syntax("Hello World")     # False
        """
        ...
    
    def validate_template(self, template: str) -> list[str]:
        """
        Validate template syntax.
        
        Args:
            template: Template string to validate
            
        Returns:
            List of error messages (empty if valid)
        """
        ...
    
    def escape_content(self, content: str) -> str:
        """
        Escape special characters in content.
        
        Args:
            content: Content to escape
            
        Returns:
            Escaped content safe for templates
        """
        ...
```

### Jinja2 Implementation

```python
from jinja2 import Environment, Template, TemplateSyntaxError

class Jinja2TemplateProvider:
    """Template provider using Jinja2."""
    
    def __init__(self, **jinja_options):
        self.env = Environment(**jinja_options)
        self._template_cache = {}
    
    def render_string(self, template: str, context: dict[str, Any]) -> str:
        try:
            if template not in self._template_cache:
                self._template_cache[template] = self.env.from_string(template)
            return self._template_cache[template].render(**context)
        except Exception as e:
            raise TemplateError(f"Template rendering failed: {e}")
    
    def render_file(self, template_path: str, context: dict[str, Any]) -> str:
        with open(template_path) as f:
            template = f.read()
        return self.render_string(template, context)
    
    def has_template_syntax(self, content: str) -> bool:
        # Check for Jinja2 syntax markers
        markers = ["{{", "}}", "{%", "%}", "{#", "#}"]
        return any(marker in content for marker in markers)
    
    def validate_template(self, template: str) -> list[str]:
        errors = []
        try:
            self.env.from_string(template)
        except TemplateSyntaxError as e:
            errors.append(f"Line {e.lineno}: {e.message}")
        return errors
    
    def escape_content(self, content: str) -> str:
        # Escape Jinja2 special characters
        replacements = {
            "{{": "{{ '{{' }}",
            "}}": "{{ '}}' }}",
            "{%": "{{ '{%' }}",
            "%}": "{{ '%}' }}",
        }
        for old, new in replacements.items():
            content = content.replace(old, new)
        return content
```

### Simple String Template Implementation

```python
import string

class SimpleTemplateProvider:
    """Simple template provider using Python string.Template."""
    
    def render_string(self, template: str, context: dict[str, Any]) -> str:
        # Convert {{var}} to $var for string.Template
        converted = template.replace("{{", "${").replace("}}", "}")
        tmpl = string.Template(converted)
        return tmpl.safe_substitute(**context)
    
    def render_file(self, template_path: str, context: dict[str, Any]) -> str:
        with open(template_path) as f:
            return self.render_string(f.read(), context)
    
    def has_template_syntax(self, content: str) -> bool:
        return "{{" in content or "${" in content
    
    def validate_template(self, template: str) -> list[str]:
        # Basic validation
        errors = []
        if template.count("{{") != template.count("}}"):
            errors.append("Unbalanced template brackets")
        return errors
    
    def escape_content(self, content: str) -> str:
        return content.replace("$", "$$")
```

## LoggerProvider

The `LayoutLogger` provides logging capabilities for the library.

### Protocol Definition

```python
class LayoutLogger(Protocol):
    """Provider for logging operations."""
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with optional context."""
        ...
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with optional context."""
        ...
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with optional context."""
        ...
    
    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """Log error message with optional exception info."""
        ...
    
    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        ...
```

### Python Logging Implementation

```python
import logging
import sys

class PythonLogger:
    """Logger using Python's standard logging."""
    
    def __init__(self, name: str = "zmk_layout", level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level))
        
        # Add console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def exception(self, message: str, **kwargs: Any) -> None:
        self.logger.exception(message, extra=kwargs)
```

### Structured Logging Implementation

```python
import structlog

class StructuredLogger:
    """Logger using structlog for structured logging."""
    
    def __init__(self, name: str = "zmk_layout"):
        self.logger = structlog.get_logger(name)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        if exc_info:
            kwargs["exc_info"] = True
        self.logger.error(message, **kwargs)
    
    def exception(self, message: str, **kwargs: Any) -> None:
        self.logger.exception(message, **kwargs)
```

### Null Logger (for testing)

```python
class NullLogger:
    """Logger that discards all messages (useful for testing)."""
    
    def debug(self, message: str, **kwargs: Any) -> None:
        pass
    
    def info(self, message: str, **kwargs: Any) -> None:
        pass
    
    def warning(self, message: str, **kwargs: Any) -> None:
        pass
    
    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        pass
    
    def exception(self, message: str, **kwargs: Any) -> None:
        pass
```

## FileProvider

The `FileProvider` abstracts file system operations.

### Protocol Definition

```python
from pathlib import Path

class FileProvider(Protocol):
    """Provider for file operations."""
    
    def read_text(self, path: Path) -> str:
        """
        Read text content from file.
        
        Args:
            path: File path
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be read
        """
        ...
    
    def write_text(self, path: Path, content: str) -> None:
        """
        Write text content to file.
        
        Args:
            path: File path
            content: Content to write
            
        Raises:
            PermissionError: If file can't be written
        """
        ...
    
    def exists(self, path: Path) -> bool:
        """
        Check if file exists.
        
        Args:
            path: File path
            
        Returns:
            True if file exists
        """
        ...
    
    def create_directory(self, path: Path, parents: bool = True) -> None:
        """
        Create directory.
        
        Args:
            path: Directory path
            parents: Create parent directories if needed
        """
        ...
    
    def delete(self, path: Path) -> None:
        """
        Delete file or directory.
        
        Args:
            path: Path to delete
        """
        ...
    
    def list_files(self, path: Path, pattern: str = "*") -> list[Path]:
        """
        List files in directory.
        
        Args:
            path: Directory path
            pattern: Glob pattern for filtering
            
        Returns:
            List of file paths
        """
        ...
```

### Standard File System Implementation

```python
from pathlib import Path
import shutil

class FileSystemProvider:
    """File provider using standard file system."""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
    
    def _resolve_path(self, path: Path) -> Path:
        """Resolve path relative to base."""
        if path.is_absolute():
            return path
        return self.base_path / path
    
    def read_text(self, path: Path) -> str:
        resolved = self._resolve_path(path)
        return resolved.read_text(encoding="utf-8")
    
    def write_text(self, path: Path, content: str) -> None:
        resolved = self._resolve_path(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
    
    def exists(self, path: Path) -> bool:
        return self._resolve_path(path).exists()
    
    def create_directory(self, path: Path, parents: bool = True) -> None:
        self._resolve_path(path).mkdir(parents=parents, exist_ok=True)
    
    def delete(self, path: Path) -> None:
        resolved = self._resolve_path(path)
        if resolved.is_dir():
            shutil.rmtree(resolved)
        else:
            resolved.unlink(missing_ok=True)
    
    def list_files(self, path: Path, pattern: str = "*") -> list[Path]:
        resolved = self._resolve_path(path)
        return list(resolved.glob(pattern))
```

### In-Memory Implementation (for testing)

```python
class InMemoryFileProvider:
    """File provider using in-memory storage (for testing)."""
    
    def __init__(self):
        self.files = {}
        self.directories = set([Path("/")])
    
    def read_text(self, path: Path) -> str:
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        return self.files[path]
    
    def write_text(self, path: Path, content: str) -> None:
        # Create parent directories
        for parent in path.parents:
            self.directories.add(parent)
        self.files[path] = content
    
    def exists(self, path: Path) -> bool:
        return path in self.files or path in self.directories
    
    def create_directory(self, path: Path, parents: bool = True) -> None:
        if parents:
            for parent in path.parents:
                self.directories.add(parent)
        self.directories.add(path)
    
    def delete(self, path: Path) -> None:
        if path in self.files:
            del self.files[path]
        # Remove directory and all contents
        self.directories.discard(path)
        # Remove files in directory
        for file_path in list(self.files.keys()):
            if path in file_path.parents:
                del self.files[file_path]
    
    def list_files(self, path: Path, pattern: str = "*") -> list[Path]:
        import fnmatch
        results = []
        for file_path in self.files:
            if path in file_path.parents:
                if fnmatch.fnmatch(file_path.name, pattern):
                    results.append(file_path)
        return results
```

## Provider Factory

Creating and configuring providers efficiently.

### Basic Factory

```python
from typing import Optional

class ProviderFactory:
    """Factory for creating provider instances."""
    
    @staticmethod
    def create_default_providers(
        keyboard: str = "crkbd",
        log_level: str = "INFO"
    ) -> LayoutProviders:
        """Create providers with default implementations."""
        return LayoutProviders(
            configuration=SimpleConfigurationProvider(keyboard),
            template=Jinja2TemplateProvider(),
            logger=PythonLogger(level=log_level),
            file=FileSystemProvider()
        )
    
    @staticmethod
    def create_test_providers() -> LayoutProviders:
        """Create providers for testing."""
        return LayoutProviders(
            configuration=SimpleConfigurationProvider(),
            template=SimpleTemplateProvider(),
            logger=NullLogger(),
            file=InMemoryFileProvider()
        )
    
    @staticmethod
    def create_from_config(config: dict[str, Any]) -> LayoutProviders:
        """Create providers from configuration dictionary."""
        # Parse configuration
        keyboard = config.get("keyboard", "crkbd")
        template_engine = config.get("template_engine", "jinja2")
        log_level = config.get("log_level", "INFO")
        file_base = config.get("file_base_path")
        
        # Create appropriate providers
        configuration = SimpleConfigurationProvider(keyboard)
        
        if template_engine == "jinja2":
            template = Jinja2TemplateProvider()
        else:
            template = SimpleTemplateProvider()
        
        logger = PythonLogger(level=log_level)
        
        if file_base:
            file = FileSystemProvider(Path(file_base))
        else:
            file = FileSystemProvider()
        
        return LayoutProviders(
            configuration=configuration,
            template=template,
            logger=logger,
            file=file
        )
```

### Environment-Based Factory

```python
import os

class EnvironmentProviderFactory:
    """Factory that configures providers from environment variables."""
    
    @staticmethod
    def create_from_environment() -> LayoutProviders:
        """Create providers based on environment variables."""
        
        # Read environment
        keyboard = os.getenv("ZMK_LAYOUT_KEYBOARD", "crkbd")
        template_engine = os.getenv("ZMK_LAYOUT_TEMPLATE", "jinja2")
        log_level = os.getenv("ZMK_LAYOUT_LOG_LEVEL", "INFO")
        file_base = os.getenv("ZMK_LAYOUT_BASE_PATH")
        
        # Database configuration
        db_url = os.getenv("ZMK_LAYOUT_DB_URL")
        
        # Create providers
        if db_url:
            configuration = DatabaseConfigurationProvider(db_url, keyboard)
        else:
            configuration = SimpleConfigurationProvider(keyboard)
        
        template = (Jinja2TemplateProvider() 
                   if template_engine == "jinja2" 
                   else SimpleTemplateProvider())
        
        logger = PythonLogger(level=log_level)
        
        file = (FileSystemProvider(Path(file_base)) 
                if file_base 
                else FileSystemProvider())
        
        return LayoutProviders(
            configuration=configuration,
            template=template,
            logger=logger,
            file=file
        )
```

## Validation & Testing

### Provider Validation

```python
def validate_providers(providers: LayoutProviders) -> list[str]:
    """
    Validate that all providers implement required methods.
    
    Args:
        providers: Provider instances to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check ConfigurationProvider
    required_config_methods = [
        "get_behavior_definitions",
        "get_include_files",
        "get_validation_rules",
        "get_template_context"
    ]
    for method in required_config_methods:
        if not hasattr(providers.configuration, method):
            errors.append(f"ConfigurationProvider missing method: {method}")
    
    # Check TemplateProvider
    required_template_methods = [
        "render_string",
        "has_template_syntax",
        "validate_template"
    ]
    for method in required_template_methods:
        if not hasattr(providers.template, method):
            errors.append(f"TemplateProvider missing method: {method}")
    
    # Check LayoutLogger
    required_logger_methods = [
        "debug", "info", "warning", "error"
    ]
    for method in required_logger_methods:
        if not hasattr(providers.logger, method):
            errors.append(f"LayoutLogger missing method: {method}")
    
    # Check FileProvider
    required_file_methods = [
        "read_text", "write_text", "exists"
    ]
    for method in required_file_methods:
        if not hasattr(providers.file, method):
            errors.append(f"FileProvider missing method: {method}")
    
    return errors
```

### Testing Providers

```python
import pytest
from unittest.mock import Mock, MagicMock

class TestProviderImplementation:
    """Test suite for provider implementations."""
    
    def test_configuration_provider(self):
        """Test ConfigurationProvider implementation."""
        provider = SimpleConfigurationProvider("crkbd")
        
        # Test behavior definitions
        behaviors = provider.get_behavior_definitions()
        assert isinstance(behaviors, list)
        assert len(behaviors) > 0
        assert all("name" in b for b in behaviors)
        
        # Test validation rules
        rules = provider.get_validation_rules()
        assert "key_count" in rules
        assert rules["key_count"] == 42  # crkbd has 42 keys
    
    def test_template_provider(self):
        """Test TemplateProvider implementation."""
        provider = SimpleTemplateProvider()
        
        # Test rendering
        result = provider.render_string(
            "Hello {{name}}", 
            {"name": "World"}
        )
        assert result == "Hello World"
        
        # Test syntax detection
        assert provider.has_template_syntax("{{var}}")
        assert not provider.has_template_syntax("plain text")
    
    def test_logger_provider(self):
        """Test LayoutLogger implementation."""
        provider = NullLogger()
        
        # Should not raise
        provider.info("test message", extra="data")
        provider.error("error message", exc_info=True)
    
    def test_file_provider(self):
        """Test FileProvider implementation."""
        provider = InMemoryFileProvider()
        
        # Test write and read
        path = Path("test.txt")
        provider.write_text(path, "content")
        assert provider.read_text(path) == "content"
        
        # Test exists
        assert provider.exists(path)
        assert not provider.exists(Path("nonexistent.txt"))
    
    def test_provider_validation(self):
        """Test provider validation."""
        # Create mock providers
        providers = LayoutProviders(
            configuration=Mock(spec=ConfigurationProvider),
            template=Mock(spec=TemplateProvider),
            logger=Mock(spec=LayoutLogger),
            file=Mock(spec=FileProvider)
        )
        
        # Should validate successfully
        errors = validate_providers(providers)
        assert len(errors) == 0
        
        # Test with missing method
        incomplete = LayoutProviders(
            configuration=Mock(),  # Missing methods
            template=Mock(spec=TemplateProvider),
            logger=Mock(spec=LayoutLogger),
            file=Mock(spec=FileProvider)
        )
        
        errors = validate_providers(incomplete)
        assert len(errors) > 0
```

## Best Practices

### 1. Immutability

Make providers immutable after creation:

```python
@dataclass(frozen=True)
class ImmutableProvider:
    """Immutable provider example."""
    
    config: dict[str, Any]
    
    def get_value(self, key: str) -> Any:
        return self.config.get(key)
    
    # No setter methods - configuration is fixed
```

### 2. Lazy Loading

Load resources only when needed:

```python
class LazyProvider:
    """Provider with lazy loading."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._config = None
    
    @property
    def config(self) -> dict[str, Any]:
        """Load configuration lazily."""
        if self._config is None:
            with open(self.config_path) as f:
                self._config = json.load(f)
        return self._config
    
    def get_value(self, key: str) -> Any:
        return self.config.get(key)
```

### 3. Caching

Cache expensive operations:

```python
from functools import lru_cache

class CachedProvider:
    """Provider with caching."""
    
    @lru_cache(maxsize=128)
    def get_behavior_definitions(self) -> list[dict[str, Any]]:
        """Cache behavior definitions."""
        # Expensive operation
        return self._load_behaviors_from_database()
```

### 4. Error Handling

Provide clear error messages:

```python
class RobustProvider:
    """Provider with robust error handling."""
    
    def read_text(self, path: Path) -> str:
        try:
            return path.read_text()
        except FileNotFoundError:
            raise ProviderError(
                f"File not found: {path}\n"
                f"Working directory: {Path.cwd()}\n"
                f"Available files: {list(path.parent.glob('*'))[:5]}"
            )
        except PermissionError:
            raise ProviderError(
                f"Permission denied reading: {path}\n"
                f"File permissions: {oct(path.stat().st_mode)}"
            )
```

### 5. Testing Support

Make providers easy to mock:

```python
def create_mock_providers() -> LayoutProviders:
    """Create mock providers for testing."""
    return LayoutProviders(
        configuration=Mock(
            spec=ConfigurationProvider,
            get_behavior_definitions=Mock(return_value=[]),
            get_validation_rules=Mock(return_value={"key_count": 42})
        ),
        template=Mock(
            spec=TemplateProvider,
            render_string=Mock(side_effect=lambda t, c: t.format(**c))
        ),
        logger=Mock(spec=LayoutLogger),
        file=Mock(
            spec=FileProvider,
            read_text=Mock(return_value="content"),
            exists=Mock(return_value=True)
        )
    )
```

## Reference Implementations

### Minimal Implementation

```python
"""Minimal provider implementation for zmk-layout."""

from pathlib import Path
from typing import Any

class MinimalProviders:
    """Minimal provider implementation."""
    
    class Config:
        def get_behavior_definitions(self) -> list[dict[str, Any]]:
            return []
        
        def get_include_files(self) -> list[str]:
            return ["behaviors.dtsi"]
        
        def get_validation_rules(self) -> dict[str, Any]:
            return {"key_count": 60}
        
        def get_template_context(self) -> dict[str, Any]:
            return {}
        
        def get_kconfig_options(self) -> dict[str, Any]:
            return {}
        
        def get_formatting_options(self) -> dict[str, Any]:
            return {"indent_size": 4}
    
    class Template:
        def render_string(self, template: str, context: dict[str, Any]) -> str:
            for key, value in context.items():
                template = template.replace(f"{{{{{key}}}}}", str(value))
            return template
        
        def has_template_syntax(self, content: str) -> bool:
            return "{{" in content
        
        def validate_template(self, template: str) -> list[str]:
            return []
        
        def escape_content(self, content: str) -> str:
            return content
    
    class Logger:
        def debug(self, message: str, **kwargs: Any) -> None:
            print(f"DEBUG: {message}")
        
        def info(self, message: str, **kwargs: Any) -> None:
            print(f"INFO: {message}")
        
        def warning(self, message: str, **kwargs: Any) -> None:
            print(f"WARNING: {message}")
        
        def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
            print(f"ERROR: {message}")
        
        def exception(self, message: str, **kwargs: Any) -> None:
            print(f"EXCEPTION: {message}")
    
    class File:
        def read_text(self, path: Path) -> str:
            return path.read_text()
        
        def write_text(self, path: Path, content: str) -> None:
            path.write_text(content)
        
        def exists(self, path: Path) -> bool:
            return path.exists()
        
        def create_directory(self, path: Path, parents: bool = True) -> None:
            path.mkdir(parents=parents, exist_ok=True)
        
        def delete(self, path: Path) -> None:
            if path.is_dir():
                import shutil
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=True)
        
        def list_files(self, path: Path, pattern: str = "*") -> list[Path]:
            return list(path.glob(pattern))
    
    @classmethod
    def create(cls) -> LayoutProviders:
        """Create minimal provider instances."""
        return LayoutProviders(
            configuration=cls.Config(),
            template=cls.Template(),
            logger=cls.Logger(),
            file=cls.File()
        )
```

### Usage Example

```python
from zmk_layout import Layout
from zmk_layout.providers import LayoutProviders

# Create custom providers
providers = MinimalProviders.create()

# Use with Layout
layout = Layout.create_empty("crkbd", "My Layout", providers=providers)

# Or use factory
providers = ProviderFactory.create_default_providers(
    keyboard="sofle",
    log_level="DEBUG"
)

layout = Layout.from_keymap("keymap.dtsi", providers=providers)
```

## Conclusion

The provider pattern in zmk-layout enables:

1. **Flexibility**: Swap implementations without changing core logic
2. **Testability**: Easy to mock and test
3. **Portability**: Works in different environments
4. **Extensibility**: Add new providers without breaking existing code

Follow this guide to implement providers that integrate seamlessly with the zmk-layout library while maintaining clean separation of concerns.