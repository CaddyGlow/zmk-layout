# Provider Pattern API Reference

## Overview

The zmk-layout library uses a provider pattern to abstract all external dependencies. This enables maximum flexibility, allowing the library to work standalone or integrate with any keyboard framework by implementing the provider protocols.

## Provider Architecture

```
LayoutProviders (aggregates all providers)
├── ConfigurationProvider   # Keyboard configs, behaviors, validation rules
├── TemplateProvider        # Template processing (Jinja2 optional)
└── LayoutLogger           # Logging abstraction
```

**Note:** FileProvider has been removed from the system. File operations are now handled directly by core components when needed.

## LayoutProviders

The main aggregator class that holds all provider instances.

### Import

```python
from zmk_layout.providers import LayoutProviders
```

### Dataclass: `LayoutProviders`

```python
@dataclass
class LayoutProviders:
    configuration: ConfigurationProvider
    template: TemplateProvider
    logger: LayoutLogger
```

**Fields:**
- `configuration`: Configuration provider instance (required)
- `template`: Template provider instance (required)
- `logger`: Logger provider instance (required)

**Example:**
```python
from zmk_layout.providers import LayoutProviders
from zmk_layout.providers.factory import (
    DefaultConfigurationProvider,
    DefaultTemplateProvider,
    DefaultLogger
)

providers = LayoutProviders(
    configuration=DefaultConfigurationProvider(),
    template=DefaultTemplateProvider(),
    logger=DefaultLogger()
)

layout = Layout("my_layout.keymap", providers=providers)
```

### Factory Functions

#### `create_default_providers`

```python
def create_default_providers() -> LayoutProviders
```

Create a set of default providers for basic functionality. These providers offer minimal functionality to get started.

**Returns:** `LayoutProviders` with default implementations

#### `create_data_only_providers`

```python
def create_data_only_providers() -> LayoutProviders
```

Create providers optimized for data-only operations (same as default providers).

---

## ConfigurationProvider Protocol

Provides keyboard configurations, behavior definitions, and validation rules.

### Protocol Definition

```python
from typing import Protocol
from pathlib import Path

class ConfigurationProvider(Protocol):
    def get_behavior_definitions(self) -> list[SystemBehavior]:
        """Get all available ZMK behaviors for validation and registration."""
        ...
    
    def get_include_files(self) -> list[str]:
        """Get required include files for ZMK compilation."""
        ...
    
    def get_validation_rules(self) -> dict[str, int | list[int] | list[str]]:
        """Get keyboard-specific validation rules and constraints."""
        ...
    
    def get_template_context(self) -> dict[str, str | int | float | bool | None]:
        """Get context data for template processing during generation."""
        ...
    
    def get_kconfig_options(self) -> dict[str, str | int | float | bool | None]:
        """Get available kconfig options for configuration generation."""
        ...
    
    def get_formatting_config(self) -> dict[str, int | list[str]]:
        """Get formatting preferences for generated files."""
        ...
    
    def get_search_paths(self) -> list[Path]:
        """Get search paths for resolving template and configuration files."""
        ...
```

### Built-in Implementations

#### `DefaultConfigurationProvider`

Default implementation with minimal ZMK behavior support.

```python
from zmk_layout.providers.factory import DefaultConfigurationProvider

provider = DefaultConfigurationProvider()

# Get basic ZMK behaviors
behaviors = provider.get_behavior_definitions()
# Returns: [SystemBehavior("kp", "Key press"), SystemBehavior("trans", "Transparent"), ...]

# Get include files
includes = provider.get_include_files()
# Returns: ["zmk/include/dt-bindings/zmk/keys.h", "zmk/include/dt-bindings/zmk/bt.h"]

# Get validation rules
rules = provider.get_validation_rules()
# Returns: {"max_layers": 10, "key_positions": [0, 1, 2, ...], "supported_behaviors": [...]}
```

### Custom Implementation Example

```python
from pathlib import Path
from zmk_layout.providers.configuration import SystemBehavior

class MyConfigProvider:
    def get_behavior_definitions(self) -> list[SystemBehavior]:
        return [
            SystemBehavior("kp", "Key press"),
            SystemBehavior("mt", "Mod-tap", tapping_term_ms=200),
            SystemBehavior("lt", "Layer-tap"),
            SystemBehavior("trans", "Transparent"),
            SystemBehavior("none", "No operation"),
        ]
    
    def get_include_files(self) -> list[str]:
        return [
            "zmk/include/dt-bindings/zmk/keys.h",
            "zmk/include/dt-bindings/zmk/bt.h",
            "zmk/include/dt-bindings/zmk/outputs.h"
        ]
    
    def get_validation_rules(self) -> dict[str, int | list[int] | list[str]]:
        return {
            "max_layers": 8,
            "key_positions": list(range(42)),  # For CRKBD
            "supported_behaviors": ["kp", "mt", "lt", "trans", "none"]
        }
    
    def get_template_context(self) -> dict[str, str | int | float | bool | None]:
        return {
            "keyboard_name": "crkbd",
            "firmware_version": "3.2.0",
            "split_keyboard": True
        }
    
    def get_kconfig_options(self) -> dict[str, str | int | float | bool | None]:
        return {
            "CONFIG_ZMK_SLEEP": True,
            "CONFIG_ZMK_IDLE_TIMEOUT": 30000
        }
    
    def get_formatting_config(self) -> dict[str, int | list[str]]:
        return {
            "key_gap": 1,
            "base_indent": 4,
            "rows": ["0  1  2  3  4  5", "6  7  8  9 10 11"]
        }
    
    def get_search_paths(self) -> list[Path]:
        return [Path.cwd(), Path.cwd() / "config", Path.home() / ".zmk"]
```

---

## TemplateProvider Protocol

Handles template processing for keymap generation.

### Protocol Definition

```python
class TemplateProvider(Protocol):
    def render_string(
        self,
        template: str,
        context: dict[str, str | int | float | bool | None]
    ) -> str:
        """Render a template string with given context."""
        ...
    
    def render_template(
        self,
        template_path: str,
        context: dict[str, str | int | float | bool | None]
    ) -> str:
        """Render a template file with given context."""
        ...
    
    def has_template_syntax(self, content: str) -> bool:
        """Check if content contains template syntax requiring processing."""
        ...
    
    def escape_content(self, content: str) -> str:
        """Escape content to prevent template processing."""
        ...
```

### Built-in Implementations

#### `DefaultTemplateProvider`

Default implementation with Jinja2 and basic format string support.

```python
from zmk_layout.providers.factory import DefaultTemplateProvider

provider = DefaultTemplateProvider()

# Basic format string (uses str.format())
result = provider.render_string("Hello {name}!", {"name": "World"})
# Returns: "Hello World!"

# Jinja2 template (uses Jinja2 engine)
result = provider.render_string("Hello {{name}}!", {"name": "World"})
# Returns: "Hello World!"

# Check for template syntax
has_syntax = provider.has_template_syntax("Hello {name}")
# Returns: True

# Escape template content
escaped = provider.escape_content("Hello {{name}}")
# Returns: "Hello {{ '{{' }}name{{ '}}' }}"
```

### Custom Implementation Example

```python
class MyTemplateProvider:
    def render_string(
        self, template: str, context: dict[str, str | int | float | bool | None]
    ) -> str:
        # Custom template rendering using simple replacement
        result = template
        for key, value in context.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    def render_template(
        self, template_path: str, context: dict[str, str | int | float | bool | None]
    ) -> str:
        from pathlib import Path
        template_content = Path(template_path).read_text()
        return self.render_string(template_content, context)
    
    def has_template_syntax(self, content: str) -> bool:
        return "{" in content and "}" in content
    
    def escape_content(self, content: str) -> str:
        return content.replace("{", "{{").replace("}", "}}")
```

---

## LayoutLogger Protocol

Provides logging abstraction for the library.

### Protocol Definition

```python
class LayoutLogger(Protocol):
    def info(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        """Log an informational message."""
        ...
    
    def error(
        self,
        message: str,
        exc_info: bool = False,
        **kwargs: str | int | float | bool | None
    ) -> None:
        """Log an error message."""
        ...
    
    def warning(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        """Log a warning message."""
        ...
    
    def debug(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        """Log a debug message."""
        ...
    
    def exception(
        self, message: str, **kwargs: str | int | float | bool | None
    ) -> None:
        """Log an exception with traceback."""
        ...
```

### Built-in Implementations

#### `DefaultLogger`

Default logger using Python's standard logging module.

```python
from zmk_layout.providers.factory import DefaultLogger

logger = DefaultLogger("zmk_layout")

# Log messages with structured data
logger.info("Layout loaded", file_path="my_layout.keymap", layer_count=3)
logger.error("Parsing failed", exc_info=True, line_number=42)
logger.warning("Deprecated behavior", behavior_name="&mt")
logger.debug("Processing layer", layer_name="gaming")
logger.exception("Unexpected error during save")
```

### Custom Implementation Example

```python
class MyLogger:
    def __init__(self):
        self.messages = []
    
    def info(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        self.messages.append(("INFO", message, kwargs))
        print(f"INFO: {message}")
    
    def error(
        self,
        message: str,
        exc_info: bool = False,
        **kwargs: str | int | float | bool | None
    ) -> None:
        self.messages.append(("ERROR", message, kwargs))
        print(f"ERROR: {message}")
        if exc_info:
            import traceback
            traceback.print_exc()
    
    def warning(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        self.messages.append(("WARNING", message, kwargs))
        print(f"WARNING: {message}")
    
    def debug(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        self.messages.append(("DEBUG", message, kwargs))
        # Debug messages often suppressed in production
    
    def exception(
        self, message: str, **kwargs: str | int | float | bool | None
    ) -> None:
        self.messages.append(("EXCEPTION", message, kwargs))
        print(f"EXCEPTION: {message}")
        import traceback
        traceback.print_exc()
```


---

## Creating Custom Providers

### Step 1: Implement the Protocol

```python
class MyCustomProvider:
    def get_keyboard_config(self, keyboard: str) -> Optional[dict[str, Any]]:
        # Your implementation
        pass
    
    # Implement other required methods...
```

### Step 2: Test Your Implementation

```python
# Test that your provider works as expected
provider = MyCustomProvider()

# Test the interface methods
behaviors = provider.get_behavior_definitions()
assert len(behaviors) > 0

rules = provider.get_validation_rules()
assert "max_layers" in rules
```

### Step 3: Use with Layout

```python
from zmk_layout.providers.factory import DefaultTemplateProvider, DefaultLogger

providers = LayoutProviders(
    configuration=MyCustomProvider(),
    template=DefaultTemplateProvider(),
    logger=DefaultLogger()
)

layout = Layout("my_layout.keymap", providers=providers)
```

---

## Provider Composition

Providers can be composed for complex scenarios:

```python
class CompositeConfigProvider:
    def __init__(self, *providers):
        self.providers = providers
    
    def get_behavior_definitions(self) -> list[SystemBehavior]:
        all_behaviors = []
        for provider in self.providers:
            behaviors = provider.get_behavior_definitions()
            all_behaviors.extend(behaviors)
        return all_behaviors
    
    def get_validation_rules(self) -> dict[str, int | list[int] | list[str]]:
        # Merge rules from all providers, with first provider taking precedence
        merged_rules = {}
        for provider in reversed(self.providers):  # Reverse for precedence
            rules = provider.get_validation_rules()
            merged_rules.update(rules)
        return merged_rules
    
    # Implement other methods similarly...

# Use multiple config sources
composite = CompositeConfigProvider(
    MyCustomConfigProvider(),      # Primary source
    DefaultConfigurationProvider()  # Fallback
)
```

---

## Testing with Providers

Providers make testing easy by allowing mock implementations:

```python
import pytest
from unittest.mock import Mock
from zmk_layout.providers.configuration import SystemBehavior

def test_layout_with_mock_providers():
    # Create mock providers
    mock_config = Mock(spec=ConfigurationProvider)
    mock_config.get_behavior_definitions.return_value = [
        SystemBehavior("kp", "Key press"),
        SystemBehavior("trans", "Transparent")
    ]
    mock_config.get_validation_rules.return_value = {
        "max_layers": 8,
        "key_positions": list(range(60)),
        "supported_behaviors": ["kp", "trans"]
    }
    
    mock_logger = Mock(spec=LayoutLogger)
    mock_template = Mock(spec=TemplateProvider)
    
    providers = LayoutProviders(
        configuration=mock_config,
        template=mock_template,
        logger=mock_logger
    )
    
    # Test with mocked providers
    layout = Layout.create_empty("test_keyboard", providers=providers)
    
    # Verify interactions
    mock_config.get_behavior_definitions.assert_called()
    mock_logger.info.assert_called()
```

---

## Default Provider Selection

When no providers are specified, the library automatically creates default providers:

```python
from zmk_layout.providers.factory import create_default_providers

def create_default_providers() -> LayoutProviders:
    """Create a set of default providers for basic functionality.
    
    These providers offer minimal functionality to get started.
    For full features, external implementations should be provided.
    """
    return LayoutProviders(
        configuration=DefaultConfigurationProvider(),
        template=DefaultTemplateProvider(),
        logger=DefaultLogger(),
    )

# Usage
providers = create_default_providers()
layout = Layout("my_layout.keymap", providers=providers)

# Or let Layout create defaults automatically
layout = Layout("my_layout.keymap")  # Uses create_default_providers() internally
```

---

## Best Practices

1. **Always implement all protocol methods** - Even if some return empty lists or default values
2. **Use type hints** - Helps with IDE support and type checking
3. **Handle missing dependencies gracefully** - Provide fallbacks for optional features
4. **Keep providers stateless** - Avoid storing state in providers when possible
5. **Document provider behavior** - Especially for custom implementations
6. **Test with mock providers** - Makes unit testing much easier
7. **Use composition for complex scenarios** - Combine multiple providers
8. **Provide sensible defaults** - Users shouldn't need to configure providers for basic usage
9. **Use factory functions** - `create_default_providers()` and `create_data_only_providers()`
10. **Log provider operations** - Help users understand what providers are doing