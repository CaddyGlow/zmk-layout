# Phase 4 API Reference

## Overview

Phase 4 provides infrastructure and polish components for the ZMK Layout Fluent API. These components focus on provider configuration, template context building, performance optimization, and debugging capabilities.

## Module Structure

```
zmk_layout.infrastructure/
├── __init__.py              # Public exports
├── provider_builder.py      # Provider configuration
├── template_context.py      # Template context building
├── performance.py           # Performance optimizations
└── debug_tools.py          # Debug and introspection tools
```

## Core Components

### 1. Provider Configuration

**Module:** `zmk_layout.infrastructure.provider_builder`

**Key Classes:**
- `ProviderBuilder` - Fluent builder for provider configuration
- `ProviderConfig` - Configuration data model
- `FileAdapterProtocol` - File operations interface
- `TemplateAdapterProtocol` - Template rendering interface
- `LoggerProtocol` - Logging interface
- `ConfigurationProviderProtocol` - Configuration provider interface

**Example:**
```python
from zmk_layout.infrastructure import ProviderBuilder

providers = (ProviderBuilder()
    .with_file_adapter(file_adapter)
    .with_template_adapter(template_adapter)
    .enable_caching(size=512)
    .build())
```

### 2. Template Context Building

**Module:** `zmk_layout.infrastructure.template_context`

**Key Classes:**
- `TemplateContextBuilder` - Fluent builder for template contexts
- `TemplateContext` - Template context data model

**Example:**
```python
from zmk_layout.infrastructure import TemplateContextBuilder

context = (TemplateContextBuilder()
    .with_layout(layout_data)
    .with_profile(keyboard_profile)
    .with_behaviors(behaviors, combos, macros)
    .build())
```

### 3. Performance Optimization

**Module:** `zmk_layout.infrastructure.performance`

**Key Classes:**
- `LRUCache` - Thread-safe LRU cache
- `WeakCache` - Weak reference cache
- `LazyProperty` - Lazy property decorator
- `PerformanceMonitor` - Performance tracking
- `OptimizedBuilder` - Base class for optimized builders

**Functions:**
- `memoize(maxsize)` - Function memoization decorator
- `profile(name)` - Function profiling decorator
- `get_performance_monitor()` - Get global monitor

**Example:**
```python
from zmk_layout.infrastructure.performance import memoize, LRUCache

@memoize(maxsize=128)
def expensive_function(x, y):
    return x ** y

cache = LRUCache(maxsize=256)
cache.put("key", "value")
```

### 4. Debug Tools

**Module:** `zmk_layout.infrastructure.debug_tools`

**Key Classes:**
- `ChainInspector` - Fluent chain inspection
- `DebugFormatter` - Object formatting for debugging
- `BuilderState` - Builder state snapshots

**Example:**
```python
from zmk_layout.infrastructure import ChainInspector

inspector = ChainInspector()
builder = inspector.wrap(my_builder)
# Use builder normally - all calls tracked
inspector.print_chain_history()
```

## Protocol Interfaces

### FileAdapterProtocol

```python
class FileAdapterProtocol(Protocol):
    def read_file(self, path: Path) -> str: ...
    def write_file(self, path: Path, content: str) -> None: ...
    def exists(self, path: Path) -> bool: ...
```

### TemplateAdapterProtocol

```python
class TemplateAdapterProtocol(Protocol):
    def render(self, template_name: str, context: dict[str, Any]) -> str: ...
    def render_string(self, template_str: str, context: dict[str, Any]) -> str: ...
```

### LoggerProtocol

```python
class LoggerProtocol(Protocol):
    def debug(self, message: str, **kwargs: Any) -> None: ...
    def info(self, message: str, **kwargs: Any) -> None: ...
    def warning(self, message: str, **kwargs: Any) -> None: ...
    def error(self, message: str, **kwargs: Any) -> None: ...
```

## Environment Variables

Phase 4 components support configuration through environment variables:

- `ZMK_LAYOUT_DEBUG` - Enable debug mode ("true")
- `ZMK_LAYOUT_PERFORMANCE` - Enable performance tracking ("true")
- `ZMK_LAYOUT_CACHE_SIZE` - Set cache size (integer)
- `ZMK_LAYOUT_NO_CACHE` - Disable caching ("true")

## Performance Characteristics

### Cache Performance
- LRU Cache: O(1) get/put operations
- Weak Cache: O(1) operations with GC-friendly behavior
- Memoization: First call O(n), cached calls O(1)

### Memory Usage
- LRU Cache: Fixed size, bounded memory
- Weak Cache: Allows GC of unused values
- Lazy Properties: Single computation per instance

### Threading
- LRU Cache: Thread-safe with RLock
- Performance Monitor: Thread-safe measurements
- Weak Cache: Thread-safe operations

## Integration with Other Phases

### With Phase 1 (Builders)
```python
from zmk_layout.builders.binding import LayoutBindingBuilder
from zmk_layout.infrastructure import ChainInspector

inspector = ChainInspector()
builder = inspector.wrap(LayoutBindingBuilder("&kp"))
```

### With Phase 2 (Generators)
```python
from zmk_layout.builders import ZMKGeneratorBuilder
from zmk_layout.infrastructure import TemplateContextBuilder

context = TemplateContextBuilder()
    .with_behaviors(behaviors)
    .build()
```

### With Phase 3 (Processing)
```python
from zmk_layout.processing import PipelineComposer
from zmk_layout.infrastructure.performance import profile

@profile("pipeline_execution")
def execute_pipeline(data):
    return composer.execute(data)
```

## Best Practices

1. **Caching Strategy**
   - Use LRU for fixed-size caches
   - Use WeakCache for large objects
   - Clear caches periodically

2. **Debug Mode**
   - Enable only during development
   - Remove debug code for production
   - Use conditional debugging

3. **Performance Monitoring**
   - Profile critical paths only
   - Monitor in production sparingly
   - Analyze cache hit rates

4. **Provider Configuration**
   - Validate providers before use
   - Use environment variables for flexibility
   - Implement protocol interfaces correctly

## Common Patterns

### Cached Builder Pattern
```python
class OptimizedBuilder(OptimizedBuilder):
    def expensive_operation(self):
        return self._get_cached("key", lambda: compute_expensive())
```

### Monitored Workflow Pattern
```python
monitor = get_performance_monitor()
with monitor.measure("workflow"):
    result = workflow.execute(data)
monitor.print_report()
```

### Debug Wrapper Pattern
```python
if DEBUG:
    builder = inspector.wrap(builder)
# Use builder normally
```

## Error Handling

### Provider Validation
```python
try:
    providers = builder.validate().build()
except ValueError as e:
    # Handle invalid configuration
    pass
```

### Cache Failures
```python
try:
    cache.put("key", non_weakref_object)
except TypeError:
    # Object doesn't support weak references
    use_regular_cache()
```

## Thread Safety

All Phase 4 components are designed to be thread-safe:

- **LRUCache**: Uses RLock for all operations
- **PerformanceMonitor**: Thread-safe measurements
- **WeakCache**: Thread-safe weak references
- **Builders**: Immutable pattern ensures safety

## Migration Guide

### From Direct Configuration
```python
# Before
config = {"file_adapter": adapter, "cache": True}

# After
config = (ProviderBuilder()
    .with_file_adapter(adapter)
    .enable_caching()
    .build())
```

### From Manual Caching
```python
# Before
cache_dict = {}
if key in cache_dict:
    return cache_dict[key]

# After
cache = LRUCache(maxsize=256)
return cache.get(key) or cache.put(key, compute())
```

## Testing

### Testing with Mocks
```python
from unittest.mock import MagicMock

mock_adapter = MagicMock(spec=FileAdapterProtocol)
providers = ProviderBuilder()
    .with_file_adapter(mock_adapter)
    .build()
```

### Performance Testing
```python
@pytest.mark.benchmark
def test_cache_performance(benchmark):
    cache = LRUCache(maxsize=100)
    result = benchmark(cache.get, "key")
    assert result is None or isinstance(result, str)
```

## Troubleshooting

### Issue: Cache not working
- Check cache size configuration
- Verify cache key generation
- Monitor hit/miss rates

### Issue: Memory growth
- Use WeakCache for large objects
- Clear caches periodically
- Check for circular references

### Issue: Debug overhead
- Disable in production
- Use conditional debugging
- Profile sparingly

## See Also

- [Infrastructure Guide](../infrastructure.md)
- [Performance Guide](../performance.md)
- [Debug Tools Guide](../debug.md)
- [Phase 1 API](phase1_api.md)
- [Phase 2 API](phase2_api.md)
- [Phase 3 API](phase3_api.md)