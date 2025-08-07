# Glovebox Integration Guide

## Overview

This guide provides comprehensive instructions for integrating the `zmk-layout` library back into the glovebox project. The integration maintains full backward compatibility while leveraging the clean architecture and fluent API of the standalone library.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Provider Implementation](#provider-implementation)
4. [Service Migration](#service-migration)
5. [Backward Compatibility](#backward-compatibility)
6. [Testing Integration](#testing-integration)
7. [Performance Validation](#performance-validation)
8. [Rollback Strategy](#rollback-strategy)
9. [Migration Timeline](#migration-timeline)

## Prerequisites

Before beginning the integration:

1. **Version Requirements**:
   - Python ≥ 3.11
   - glovebox ≥ current version
   - zmk-layout ≥ 0.1.0

2. **Backup Current State**:
   ```bash
   cd /path/to/zmk-glovebox
   git checkout -b pre-zmk-layout-integration
   git commit -am "Backup before zmk-layout integration"
   ```

3. **Review Breaking Changes**:
   - See [BREAKING_CHANGES.md](./BREAKING_CHANGES.md) for detailed list
   - Ensure all team members are aware of changes

## Installation

### Step 1: Add zmk-layout as Dependency

Update `pyproject.toml` in glovebox:

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "zmk-layout>=0.1.0",  # Add this line
]
```

### Step 2: Install the Library

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install zmk-layout

# For development (if working on both projects)
pip install -e ../zmk-layout
```

### Step 3: Verify Installation

```python
# Test in Python REPL
>>> import zmk_layout
>>> print(zmk_layout.__version__)
0.1.0
>>> from zmk_layout import Layout
>>> Layout.create_empty("crkbd", "test")
<Layout: test (crkbd) - 0 layers>
```

## Provider Implementation

The zmk-layout library uses a provider pattern to abstract external dependencies. Glovebox needs to implement these providers to integrate its existing services.

### Step 1: Create Provider Implementations

Create `glovebox/adapters/zmk_layout_providers.py`:

```python
"""Provider implementations for zmk-layout library integration."""

from pathlib import Path
from typing import Any, Optional

from zmk_layout.providers import (
    ConfigurationProvider,
    TemplateProvider,
    LayoutLogger,
    FileProvider,
    LayoutProviders,
)

from glovebox.services.keyboard_profile import KeyboardProfileService
from glovebox.services.behavior_registry import BehaviorRegistryProtocol
from glovebox.adapters.template_adapter import TemplateAdapterProtocol
from glovebox.adapters.file_adapter import FileAdapterProtocol
from glovebox.core.structlog_logger import get_struct_logger


class GloveboxConfigurationProvider(ConfigurationProvider):
    """Configuration provider using glovebox's profile system."""

    def __init__(
        self,
        profile_service: KeyboardProfileService,
        behavior_registry: BehaviorRegistryProtocol,
    ):
        self.profile_service = profile_service
        self.behavior_registry = behavior_registry
        self._profile = None

    def set_profile(self, profile_name: str) -> None:
        """Set the active keyboard profile."""
        self._profile = self.profile_service.get_profile(profile_name)

    def get_behavior_definitions(self) -> list[dict[str, Any]]:
        """Get all available ZMK behaviors for validation."""
        if not self._profile:
            return self.behavior_registry.get_default_behaviors()
        return self._profile.get_behaviors()

    def get_include_files(self) -> list[str]:
        """Get required include files for compilation."""
        if not self._profile:
            return []
        return self._profile.config.firmware.includes

    def get_validation_rules(self) -> dict[str, Any]:
        """Get keyboard-specific validation rules."""
        if not self._profile:
            return {}
        return {
            "key_count": self._profile.config.layout.key_count,
            "layer_limit": self._profile.config.layout.max_layers,
            "combo_limit": self._profile.config.firmware.max_combos,
        }

    def get_template_context(self) -> dict[str, Any]:
        """Get context data for template processing."""
        if not self._profile:
            return {}
        return {
            "keyboard": self._profile.name,
            "manufacturer": self._profile.manufacturer,
            "layout": self._profile.config.layout.to_dict(),
            "firmware": self._profile.config.firmware.to_dict(),
        }


class GloveboxTemplateProvider(TemplateProvider):
    """Template provider using glovebox's template adapter."""

    def __init__(self, template_adapter: TemplateAdapterProtocol):
        self.adapter = template_adapter

    def render_string(self, template: str, context: dict[str, Any]) -> str:
        """Render a template string with given context."""
        return self.adapter.render_string(template, context)

    def has_template_syntax(self, content: str) -> bool:
        """Check if content contains template syntax."""
        return self.adapter.has_template_syntax(content)

    def validate_template(self, template: str) -> list[str]:
        """Validate template syntax, return list of errors."""
        try:
            self.adapter.validate(template)
            return []
        except Exception as e:
            return [str(e)]


class GloveboxLayoutLogger(LayoutLogger):
    """Logger implementation using glovebox's structured logging."""

    def __init__(self, name: str = "zmk_layout"):
        self.logger = get_struct_logger(name)

    def info(self, message: str, **kwargs) -> None:
        self.logger.info(message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        self.logger.error(message, exc_info=exc_info, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self.logger.warning(message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        self.logger.debug(message, **kwargs)


class GloveboxFileProvider(FileProvider):
    """File provider using glovebox's file adapter."""

    def __init__(self, file_adapter: FileAdapterProtocol):
        self.adapter = file_adapter

    def read_text(self, path: Path) -> str:
        """Read file contents."""
        return self.adapter.read_text(path)

    def write_text(self, path: Path, content: str) -> None:
        """Write file contents."""
        self.adapter.write_text(path, content)

    def exists(self, path: Path) -> bool:
        """Check if file exists."""
        return self.adapter.exists(path)


def create_glovebox_providers(
    profile_service: Optional[KeyboardProfileService] = None,
    behavior_registry: Optional[BehaviorRegistryProtocol] = None,
    template_adapter: Optional[TemplateAdapterProtocol] = None,
    file_adapter: Optional[FileAdapterProtocol] = None,
) -> LayoutProviders:
    """Create provider instances using glovebox services."""

    # Use defaults if not provided
    if not profile_service:
        from glovebox.services import get_keyboard_profile_service
        profile_service = get_keyboard_profile_service()

    if not behavior_registry:
        from glovebox.services import get_behavior_registry
        behavior_registry = get_behavior_registry()

    if not template_adapter:
        from glovebox.adapters import get_template_adapter
        template_adapter = get_template_adapter()

    if not file_adapter:
        from glovebox.adapters import get_file_adapter
        file_adapter = get_file_adapter()

    return LayoutProviders(
        configuration=GloveboxConfigurationProvider(profile_service, behavior_registry),
        template=GloveboxTemplateProvider(template_adapter),
        logger=GloveboxLayoutLogger(),
        file=GloveboxFileProvider(file_adapter),
    )
```

### Step 2: Validate Provider Implementation

Create a test to ensure providers work correctly:

```python
# tests/test_zmk_layout_integration.py

import pytest
from glovebox.adapters.zmk_layout_providers import create_glovebox_providers
from zmk_layout.providers import validate_providers


def test_provider_validation():
    """Test that glovebox providers implement all required methods."""
    providers = create_glovebox_providers()

    # This will raise if any provider is missing required methods
    errors = validate_providers(providers)
    assert not errors, f"Provider validation failed: {errors}"


def test_provider_functionality():
    """Test basic provider functionality."""
    providers = create_glovebox_providers()

    # Test configuration provider
    behaviors = providers.configuration.get_behavior_definitions()
    assert isinstance(behaviors, list)

    # Test template provider
    rendered = providers.template.render_string("Hello {{name}}", {"name": "World"})
    assert rendered == "Hello World"

    # Test logger
    providers.logger.info("Test message", extra_field="value")

    # Test file provider (with temp file)
    from pathlib import Path
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        test_path = Path(f.name)
        providers.file.write_text(test_path, "test content")
        content = providers.file.read_text(test_path)
        assert content == "test content"
        test_path.unlink()
```

## Service Migration

Update glovebox services to use zmk-layout internally while maintaining the existing API.

### Step 1: Update LayoutService

Modify `glovebox/layout/service.py`:

```python
"""Layout service using zmk-layout library internally."""

from typing import Any, Optional
from pathlib import Path

from zmk_layout import Layout as ZmkLayout
from glovebox.adapters.zmk_layout_providers import create_glovebox_providers
from glovebox.services.base import BaseService
from glovebox.models.layout import LayoutResult


class LayoutService(BaseService):
    """Layout service with zmk-layout integration."""

    def __init__(self):
        super().__init__(service_name="LayoutService", service_version="2.0.0")
        self._providers = None

    def _get_providers(self, profile: Optional[str] = None):
        """Get or create providers."""
        if not self._providers:
            self._providers = create_glovebox_providers()

        if profile and hasattr(self._providers.configuration, 'set_profile'):
            self._providers.configuration.set_profile(profile)

        return self._providers

    def compile(
        self,
        layout_data: dict[str, Any],
        profile: Optional[str] = None,
    ) -> LayoutResult:
        """Compile layout using zmk-layout library."""
        try:
            # Get providers with profile
            providers = self._get_providers(profile)

            # Create layout from data
            layout = ZmkLayout.from_dict(layout_data, providers=providers)

            # Validate
            layout = layout.validate()

            # Generate output
            keymap = layout.generate_keymap()
            behaviors = layout.generate_behaviors()

            return LayoutResult(
                success=True,
                keymap=keymap,
                behaviors=behaviors,
                metadata=layout.get_metadata(),
            )

        except Exception as e:
            self.logger.error("Layout compilation failed", error=str(e))
            return LayoutResult(
                success=False,
                error=str(e),
            )

    def parse_keymap(self, file_path: Path) -> dict[str, Any]:
        """Parse a keymap file using zmk-layout."""
        providers = self._get_providers()
        layout = ZmkLayout.from_keymap(str(file_path), providers=providers)
        return layout.to_dict()

    def validate_layout(
        self,
        layout_data: dict[str, Any],
        profile: Optional[str] = None,
    ) -> tuple[bool, list[str]]:
        """Validate layout data."""
        try:
            providers = self._get_providers(profile)
            layout = ZmkLayout.from_dict(layout_data, providers=providers)
            layout.validate()
            return True, []
        except ValidationError as e:
            return False, e.errors
```

### Step 2: Update Layer Service

Modify `glovebox/layout/layer_service.py`:

```python
"""Layer service using zmk-layout fluent API."""

from typing import Any, Optional
from zmk_layout import Layout as ZmkLayout


class LayoutLayerService(BaseService):
    """Layer management service."""

    def add_layer(
        self,
        layout_data: dict[str, Any],
        layer_name: str,
        position: Optional[int] = None,
    ) -> dict[str, Any]:
        """Add a layer to the layout."""
        layout = ZmkLayout.from_dict(layout_data)

        # Use fluent API
        layout = layout.layers.add(layer_name, position=position).parent()

        return layout.to_dict()

    def remove_layer(
        self,
        layout_data: dict[str, Any],
        layer_name: str,
    ) -> dict[str, Any]:
        """Remove a layer from the layout."""
        layout = ZmkLayout.from_dict(layout_data)
        layout = layout.layers.remove(layer_name).parent()
        return layout.to_dict()

    def update_binding(
        self,
        layout_data: dict[str, Any],
        layer_name: str,
        position: int,
        binding: str,
    ) -> dict[str, Any]:
        """Update a single binding."""
        layout = ZmkLayout.from_dict(layout_data)
        layout = layout.layers.get(layer_name).set(position, binding).parent()
        return layout.to_dict()
```

## Backward Compatibility

Maintain backward compatibility during the transition period.

### Compatibility Wrapper

Create `glovebox/layout/compat.py`:

```python
"""Backward compatibility layer for layout operations."""

import warnings
from typing import Any
from zmk_layout import Layout as ZmkLayout


class LegacyLayoutWrapper:
    """Wrapper maintaining old API while using zmk-layout internally."""

    def __init__(self, layout_data: Optional[dict] = None):
        if layout_data:
            self._layout = ZmkLayout.from_dict(layout_data)
        else:
            self._layout = ZmkLayout.create_empty("crkbd", "Legacy")

        # Track deprecation warnings
        self._deprecation_shown = set()

    def _warn_deprecated(self, method: str, alternative: str):
        """Show deprecation warning once per method."""
        if method not in self._deprecation_shown:
            warnings.warn(
                f"{method} is deprecated. Use {alternative} instead.",
                DeprecationWarning,
                stacklevel=2
            )
            self._deprecation_shown.add(method)

    # Old API methods (deprecated)
    def add_layer(self, name: str) -> None:
        """Deprecated: Add layer using old API."""
        self._warn_deprecated("add_layer", "layout.layers.add()")
        self._layout = self._layout.layers.add(name).parent()

    def set_binding(self, layer: str, pos: int, binding: str) -> None:
        """Deprecated: Set binding using old API."""
        self._warn_deprecated("set_binding", "layout.layers.get().set()")
        self._layout = self._layout.layers.get(layer).set(pos, binding).parent()

    # Bridge to new API
    def to_fluent(self) -> ZmkLayout:
        """Get the fluent layout instance."""
        return self._layout

    def to_dict(self) -> dict[str, Any]:
        """Export to dictionary."""
        return self._layout.to_dict()
```

### Gradual Migration Strategy

1. **Phase 1**: Add zmk-layout alongside existing code
2. **Phase 2**: Update internal implementations to use zmk-layout
3. **Phase 3**: Deprecate old APIs with warnings
4. **Phase 4**: Remove deprecated code (after 2-3 releases)

## Testing Integration

### Unit Tests

Create comprehensive tests for the integration:

```python
# tests/integration/test_zmk_layout_service.py

import pytest
from glovebox.layout.service import LayoutService
from glovebox.adapters.zmk_layout_providers import create_glovebox_providers


class TestLayoutServiceIntegration:
    """Test layout service with zmk-layout integration."""

    def test_compile_with_profile(self):
        """Test compilation with keyboard profile."""
        service = LayoutService()

        layout_data = {
            "keyboard": "crkbd",
            "layers": [
                {"name": "base", "bindings": ["&kp Q"] * 42}
            ]
        }

        result = service.compile(layout_data, profile="crkbd")

        assert result.success
        assert result.keymap is not None
        assert "layer_base" in result.keymap

    def test_backward_compatibility(self):
        """Test that old API still works."""
        from glovebox.layout.compat import LegacyLayoutWrapper

        wrapper = LegacyLayoutWrapper()
        wrapper.add_layer("test")  # Should show deprecation warning

        data = wrapper.to_dict()
        assert "test" in data["layer_names"]

    def test_performance_comparison(self):
        """Compare performance with old implementation."""
        import time

        service = LayoutService()
        layout_data = create_test_layout(1000)  # Large layout

        start = time.time()
        result = service.compile(layout_data)
        duration = time.time() - start

        assert result.success
        assert duration < 1.0  # Should complete in under 1 second
```

### Integration Tests

Test end-to-end workflow:

```python
# tests/integration/test_e2e_workflow.py

def test_full_workflow():
    """Test complete workflow from parse to generate."""
    from pathlib import Path
    from glovebox.layout.service import LayoutService

    service = LayoutService()

    # Parse existing keymap
    keymap_path = Path("fixtures/sample.keymap")
    layout_data = service.parse_keymap(keymap_path)

    # Modify using fluent API
    from zmk_layout import Layout
    layout = Layout.from_dict(layout_data)
    layout = layout.layers.add("gaming").parent()

    # Compile back
    result = service.compile(layout.to_dict(), profile="crkbd")

    assert result.success
    assert "layer_gaming" in result.keymap
```

## Performance Validation

### Benchmarking

Create performance benchmarks:

```python
# scripts/benchmark_integration.py

import time
import statistics
from glovebox.layout.service import LayoutService


def benchmark_operation(operation, iterations=100):
    """Benchmark an operation."""
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        operation()
        times.append(time.perf_counter() - start)

    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
    }


def main():
    """Run performance benchmarks."""
    service = LayoutService()

    # Test data
    small_layout = create_layout(10)    # 10 bindings
    medium_layout = create_layout(100)  # 100 bindings
    large_layout = create_layout(1000)  # 1000 bindings

    print("Performance Benchmark Results")
    print("=" * 50)

    # Benchmark compilation
    for size, data in [("Small", small_layout), ("Medium", medium_layout), ("Large", large_layout)]:
        stats = benchmark_operation(lambda: service.compile(data))
        print(f"\n{size} Layout Compilation:")
        print(f"  Mean: {stats['mean']*1000:.2f}ms")
        print(f"  Median: {stats['median']*1000:.2f}ms")
        print(f"  Min/Max: {stats['min']*1000:.2f}ms / {stats['max']*1000:.2f}ms")

    # Compare with baseline
    print("\n\nPerformance vs Baseline:")
    print("Acceptable threshold: <5% overhead")
    # Add comparison logic here


if __name__ == "__main__":
    main()
```

### Performance Criteria

The integration must meet these performance targets:

| Operation | Target | Maximum |
|-----------|--------|---------|
| Small layout compile | <50ms | 100ms |
| Medium layout compile | <100ms | 200ms |
| Large layout compile | <500ms | 1000ms |
| Parse keymap file | <100ms | 200ms |
| Validate layout | <20ms | 50ms |
| Overall overhead | <5% | 10% |

## Rollback Strategy

If issues arise during integration, follow this rollback plan:

### Immediate Rollback (< 1 hour)

```bash
# Revert to previous commit
git revert HEAD
git push

# Or reset to backup branch
git reset --hard pre-zmk-layout-integration
git push --force-with-lease
```

### Gradual Rollback (1-2 days)

1. **Keep zmk-layout installed** but disable usage:

```python
# glovebox/config.py
USE_ZMK_LAYOUT = False  # Disable zmk-layout integration

# In services
if config.USE_ZMK_LAYOUT:
    # Use zmk-layout
else:
    # Use legacy implementation
```

2. **Fix issues** while running legacy code
3. **Re-enable** when ready

### Feature Flag Approach

Implement feature flags for gradual rollout:

```python
# glovebox/features.py
class Features:
    ZMK_LAYOUT_PARSER = os.getenv("FEATURE_ZMK_LAYOUT_PARSER", "false") == "true"
    ZMK_LAYOUT_GENERATOR = os.getenv("FEATURE_ZMK_LAYOUT_GENERATOR", "false") == "true"
    ZMK_LAYOUT_FULL = os.getenv("FEATURE_ZMK_LAYOUT_FULL", "false") == "true"

# Usage
if Features.ZMK_LAYOUT_PARSER:
    layout = ZmkLayout.from_keymap(path)
else:
    layout = legacy_parse_keymap(path)
```

## Migration Timeline

### Week 1: Preparation
- [ ] Review this guide with team
- [ ] Set up development environment
- [ ] Create backup branch
- [ ] Install zmk-layout in development

### Week 2: Provider Implementation
- [ ] Implement all providers
- [ ] Write provider tests
- [ ] Validate with real data
- [ ] Performance benchmarking

### Week 3: Service Migration
- [ ] Update LayoutService
- [ ] Update LayerService
- [ ] Update other dependent services
- [ ] Implement compatibility layer

### Week 4: Testing
- [ ] Run full test suite
- [ ] Integration testing
- [ ] Performance validation
- [ ] User acceptance testing

### Week 5: Staged Rollout
- [ ] Deploy to staging environment
- [ ] Monitor for issues
- [ ] Fix any problems
- [ ] Document learnings

### Week 6: Production Deployment
- [ ] Deploy with feature flags
- [ ] Gradual rollout (10% → 50% → 100%)
- [ ] Monitor metrics
- [ ] Full deployment

## Troubleshooting

### Common Issues and Solutions

#### Import Errors

**Problem**: `ImportError: cannot import name 'Layout' from 'zmk_layout'`

**Solution**: Ensure zmk-layout is installed:
```bash
pip show zmk-layout
pip install --upgrade zmk-layout
```

#### Provider Validation Failures

**Problem**: `ValueError: Provider missing required method: get_behavior_definitions`

**Solution**: Ensure all provider methods are implemented:
```python
# Check implementation
from zmk_layout.providers import validate_providers
errors = validate_providers(providers)
print(errors)  # Shows missing methods
```

#### Performance Degradation

**Problem**: Operations taking longer than expected

**Solution**:
1. Check cache configuration
2. Profile the code to find bottlenecks
3. Ensure providers are properly cached

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Run operation
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 time consumers
```

#### Backward Compatibility Issues

**Problem**: Old code breaking with new implementation

**Solution**: Use compatibility wrapper:
```python
# Instead of direct usage
from glovebox.layout.compat import LegacyLayoutWrapper
layout = LegacyLayoutWrapper(data)
# Old API works with deprecation warnings
```

## Support and Resources

### Documentation
- [zmk-layout API Reference](./api/api_reference.md)
- [Provider Implementation Guide](./providers_guide.md)
- [Breaking Changes](./BREAKING_CHANGES.md)

### Getting Help
- GitHub Issues: [zmk-layout/issues](https://github.com/CaddyGlow/zmk-layout/issues)
- Discussions: [zmk-layout/discussions](https://github.com/CaddyGlow/zmk-layout/discussions)
- Glovebox Slack: #zmk-layout-integration

### Examples
- [Basic Integration](../examples/glovebox_integration/basic_integration.py)
- [Provider Implementation](../examples/glovebox_integration/provider_implementation.py)
- [Service Wrapper](../examples/glovebox_integration/service_wrapper.py)

## Conclusion

The integration of zmk-layout into glovebox provides:

1. **Clean Architecture**: Separation of concerns with provider pattern
2. **Better API**: Fluent, chainable interface
3. **Improved Testing**: Easier to test with clear boundaries
4. **Ecosystem Growth**: Standalone library benefits entire ZMK community
5. **Performance**: Optimized operations with caching

Follow this guide step-by-step, test thoroughly at each stage, and maintain backward compatibility during the transition period. The investment in proper integration will pay dividends in maintainability and ecosystem growth.
