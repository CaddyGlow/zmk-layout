# ZMK Layout Infrastructure & Performance Guide

## Overview

The infrastructure module provides essential building blocks for the ZMK Layout Fluent API, including provider configuration, template context building, performance optimizations, and debugging tools.

## Table of Contents

1. [Provider Configuration](#provider-configuration)
2. [Template Context Building](#template-context-building)
3. [Performance Optimization](#performance-optimization)
4. [Debug Tools](#debug-tools)
5. [Pipeline Composition](#pipeline-composition)
6. [Best Practices](#best-practices)

## Provider Configuration

The `ProviderBuilder` enables fluent configuration of external dependencies through protocol-based interfaces.

### Basic Usage

```python
from zmk_layout.infrastructure import ProviderBuilder

# Configure providers fluently
providers = (ProviderBuilder()
    .with_file_adapter(my_file_adapter)
    .with_template_adapter(jinja_adapter)
    .with_logger(structured_logger)
    .enable_caching(size=512)
    .enable_debug_mode()
    .build())
```

### Protocol Interfaces

The provider system uses Python protocols for clean abstraction:

```python
from pathlib import Path
from typing import Protocol, Any

class FileAdapterProtocol(Protocol):
    """Protocol for file operations."""

    def read_file(self, path: Path) -> str:
        """Read file contents."""
        ...

    def write_file(self, path: Path, content: str) -> None:
        """Write file contents."""
        ...

    def exists(self, path: Path) -> bool:
        """Check if file exists."""
        ...
```

### Environment Configuration

Configure providers from environment variables:

```python
# Set environment variables
export ZMK_LAYOUT_DEBUG=true
export ZMK_LAYOUT_CACHE_SIZE=1024
export ZMK_LAYOUT_PERFORMANCE=true

# Load from environment
providers = (ProviderBuilder()
    .from_environment()
    .validate()
    .build())
```

### Custom Implementations

Create custom provider implementations:

```python
class MyFileAdapter:
    """Custom file adapter implementation."""

    def read_file(self, path: Path) -> str:
        # Custom implementation
        with open(path, 'r') as f:
            return f.read()

    def write_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)

    def exists(self, path: Path) -> bool:
        return path.exists()

# Use custom adapter
providers = (ProviderBuilder()
    .with_file_adapter(MyFileAdapter())
    .build())
```

## Template Context Building

The `TemplateContextBuilder` provides comprehensive template context construction for ZMK generation.

### Basic Usage

```python
from zmk_layout.infrastructure import TemplateContextBuilder

context = (TemplateContextBuilder()
    .with_layout(layout_data)
    .with_profile(keyboard_profile)
    .with_behaviors(behaviors, combos, macros)
    .with_generation_metadata(
        author="John Doe",
        version="2.0.0"
    )
    .build())
```

### Complete Example

```python
from zmk_layout.infrastructure import TemplateContextBuilder
from zmk_layout.models.metadata import LayoutData

# Create layout data
layout_data = LayoutData(
    keyboard="glove80",
    title="My Custom Layout",
    layers=[...],
    layer_names=["base", "lower", "raise"]
)

# Build comprehensive context
context = (TemplateContextBuilder()
    # Layout information
    .with_layout(layout_data)

    # Keyboard profile
    .with_profile(glove80_profile)

    # Behaviors
    .with_behaviors(
        behaviors=[home_row_mod],
        combos=[esc_combo],
        macros=[vim_save]
    )

    # DTSI content
    .with_dtsi_content(
        layer_defines=layer_defines_str,
        behaviors_dtsi=behaviors_dtsi_str,
        keymap_node=keymap_node_str
    )

    # Metadata
    .with_generation_metadata(
        author="John Doe",
        version="2.0.0"
    )

    # Custom variables
    .with_custom_vars(
        theme="dark",
        layout_style="ergonomic"
    )

    # Feature flags
    .with_features(
        home_row_mods=True,
        mouse_keys=False,
        rgb_underglow=True
    )

    # Validate and build
    .validate_completeness()
    .build())

# Use in template rendering
rendered = template.render(**context.build_dict())
```

### Context Transformation

Add custom transformers to modify context:

```python
def add_copyright(ctx: TemplateContext) -> TemplateContext:
    """Add copyright notice to context."""
    return ctx.model_copy(update={
        "custom_vars": {
            **ctx.custom_vars,
            "copyright": f"© {datetime.now().year} John Doe"
        }
    })

context = (TemplateContextBuilder()
    .with_layout(layout_data)
    .add_transformer(add_copyright)
    .build())
```

### Context Merging

Merge multiple contexts:

```python
# Create base context
base_context = (TemplateContextBuilder()
    .with_features(home_row_mods=True)
    .with_custom_vars(theme="dark")
    .build())

# Merge with specific layout
final_context = (TemplateContextBuilder()
    .merge_with(base_context)
    .with_layout(layout_data)
    .build())
```

## Performance Optimization

The performance module provides various optimization utilities for the fluent API.

### LRU Cache

Thread-safe least-recently-used cache:

```python
from zmk_layout.infrastructure.performance import LRUCache

# Create cache
cache = LRUCache(maxsize=256)

# Use cache
cache.put("key", expensive_computation())
result = cache.get("key")  # Returns cached value

# Get statistics
stats = cache.stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
```

### Memoization

Decorator for caching function results:

```python
from zmk_layout.infrastructure.performance import memoize

@memoize(maxsize=128)
def expensive_function(x: int, y: int) -> int:
    """Expensive computation that will be cached."""
    time.sleep(1)  # Simulate expensive operation
    return x ** y

# First call: takes 1 second
result = expensive_function(2, 10)  # 1024

# Second call: instant (cached)
result = expensive_function(2, 10)  # 1024

# Check cache statistics
print(expensive_function.cache_stats())
```

### Lazy Properties

Compute expensive properties once:

```python
from zmk_layout.infrastructure.performance import LazyProperty

class LayoutAnalyzer:
    def __init__(self, layout_data):
        self.layout_data = layout_data

    @LazyProperty
    def complexity_score(self) -> float:
        """Expensive complexity analysis (computed once)."""
        # Complex calculation
        score = analyze_layout_complexity(self.layout_data)
        return score

analyzer = LayoutAnalyzer(layout_data)
# First access: computes value
score1 = analyzer.complexity_score
# Second access: returns cached value
score2 = analyzer.complexity_score
```

### Performance Monitoring

Track and analyze performance:

```python
from zmk_layout.infrastructure.performance import (
    get_performance_monitor,
    profile
)

monitor = get_performance_monitor()

# Manual measurement
with monitor.measure("layout_processing"):
    process_layout(layout_data)

# Using decorator
@profile("validation")
def validate_layout(layout):
    # Validation logic
    pass

# Get performance report
monitor.print_report()
```

### Weak Cache

Memory-efficient caching with weak references:

```python
from zmk_layout.infrastructure.performance import WeakCache

cache = WeakCache()

# Cache large objects
large_obj = create_large_object()
cache.put("key", large_obj)

# Object can be garbage collected when not in use
del large_obj
# Cache entry may be cleared by GC
```

## Debug Tools

Comprehensive debugging utilities for development and troubleshooting.

### Chain Inspector

Track and debug fluent API chains:

```python
from zmk_layout.infrastructure import ChainInspector

# Create inspector
inspector = ChainInspector()

# Wrap builder for inspection
builder = inspector.wrap(LayoutBindingBuilder("&kp"))

# Use builder normally - all calls are tracked
result = (builder
    .modifier("LC")
    .modifier("LS")
    .key("A")
    .build())

# Inspect chain history
inspector.print_chain_history()
inspector.print_performance_summary()

# Export for analysis
inspector.export_history("debug_chain.json")
```

### Debug Formatter

Format complex objects for debugging:

```python
from zmk_layout.infrastructure import DebugFormatter

formatter = DebugFormatter(
    max_depth=3,
    max_width=80,
    show_private=False
)

# Format complex object
layout = create_complex_layout()
formatted = formatter.format(layout)
print(formatted)

# Highlight differences
old_layout = layout
new_layout = modify_layout(layout)
diff = formatter.diff(old_layout, new_layout)
print(diff)
```

### Builder State Snapshots

Capture builder state for debugging:

```python
from zmk_layout.infrastructure import BuilderState

# Capture current state
state = BuilderState.from_builder(my_builder)

# Inspect state
print(f"Class: {state.class_name}")
print(f"Methods called: {state.method_calls}")
print(f"Attributes: {state.attributes}")

# Export for debugging
state.to_json("builder_state.json")
```

### Introspection Example

Complete debugging workflow:

```python
from zmk_layout.infrastructure import (
    ChainInspector,
    DebugFormatter,
    BuilderState
)

# Setup debugging
inspector = ChainInspector()
formatter = DebugFormatter()

# Create wrapped builder
builder = inspector.wrap(
    LayoutBindingBuilder("&kp")
)

# Perform operations
binding = (builder
    .modifier("LC")
    .modifier("LS")
    .key("A")
    .build())

# Capture state at any point
state = BuilderState.from_builder(builder)

# Debug output
print("\n=== Chain History ===")
inspector.print_chain_history()

print("\n=== Current State ===")
print(formatter.format(state))

print("\n=== Performance ===")
inspector.print_performance_summary()

# Check for issues
issues = inspector.find_redundant_calls()
if issues:
    print("\n=== Potential Issues ===")
    for issue in issues:
        print(f"- {issue}")
```

## Pipeline Composition

Combine multiple pipelines into complex workflows.

### Basic Composition

```python
from zmk_layout.infrastructure import PipelineComposer

composer = PipelineComposer()

# Add pipeline stages
result = (composer
    .add_processing(processing_pipeline)
    .add_transformation(transformation_pipeline)
    .add_validation(lambda layout: ValidationPipeline(layout))
    .execute(layout_data))
```

### Error Handling & Rollback

```python
# Enable rollback on error
composer = (PipelineComposer()
    .add_processing(processing_pipeline)
    .checkpoint("after_processing")
    .add_transformation(transformation_pipeline)
    .checkpoint("after_transformation")
    .add_validation(validation_factory)
    .with_rollback()
    .execute(layout_data))

# Custom error handling
def handle_error(exc: Exception, stage: str) -> None:
    logger.error(f"Pipeline failed at {stage}: {exc}")
    # Could notify, retry, etc.

composer = (PipelineComposer()
    .add_processing(processing_pipeline)
    .with_error_handler(handle_error)
    .execute(layout_data))
```

### Pre-built Workflows

```python
from zmk_layout.infrastructure import WorkflowBuilder

# QMK Migration
workflow = WorkflowBuilder.qmk_migration_workflow()
zmk_layout = workflow.execute(qmk_layout_data)

# Layout Optimization
workflow = WorkflowBuilder.layout_optimization_workflow(
    max_layers=8
)
optimized = workflow.execute(layout_data)

# Home Row Mods
workflow = WorkflowBuilder.home_row_mods_workflow(
    mod_config={"positions": [15, 16, 17, 18]}
)
with_hrm = workflow.execute(layout_data)
```

### Custom Workflows

```python
from zmk_layout.infrastructure import PipelineComposer

def create_custom_workflow():
    """Create custom processing workflow."""
    composer = PipelineComposer()

    # Add custom stages
    def normalize_stage(data):
        # Custom normalization
        return normalize_layout(data)

    def optimize_stage(data):
        # Custom optimization
        return optimize_for_performance(data)

    def validate_stage(layout):
        return (ValidationPipeline(layout)
            .validate_bindings()
            .validate_layer_references()
            .with_custom_rules(my_rules))

    return (composer
        .add_custom_stage("normalize", normalize_stage)
        .checkpoint("after_normalization")
        .add_custom_stage("optimize", optimize_stage)
        .add_validation(validate_stage)
        .with_rollback())

# Use custom workflow
workflow = create_custom_workflow()
result = workflow.execute(layout_data)
```

## Best Practices

### 1. Provider Configuration

**DO:**
- Use protocol interfaces for clean abstraction
- Configure from environment for flexibility
- Validate provider configuration
- Enable caching for performance

**DON'T:**
- Hard-code provider implementations
- Skip validation
- Ignore performance tracking in production

### 2. Template Context

**DO:**
- Build contexts incrementally
- Validate completeness before use
- Use transformers for reusable modifications
- Merge contexts for composition

**DON'T:**
- Modify contexts after building
- Skip validation
- Duplicate context logic

### 3. Performance

**DO:**
- Use appropriate cache sizes
- Profile critical paths
- Monitor performance in production
- Clear caches when appropriate

**DON'T:**
- Over-cache (memory issues)
- Profile everything (overhead)
- Ignore cache statistics
- Use weak cache for primitives

### 4. Debugging

**DO:**
- Use chain inspector during development
- Export debug data for analysis
- Clean up debug code for production
- Use appropriate detail levels

**DON'T:**
- Leave inspectors in production code
- Ignore performance overhead
- Export sensitive data
- Use excessive debug depth

### 5. Pipeline Composition

**DO:**
- Use checkpoints for complex workflows
- Implement error handlers
- Test rollback scenarios
- Compose reusable workflows

**DON'T:**
- Create deeply nested pipelines
- Skip error handling
- Ignore rollback overhead
- Duplicate workflow logic

## Performance Guidelines

### Cache Sizing

```python
# Small layouts (< 50 bindings)
cache = LRUCache(maxsize=64)

# Medium layouts (50-200 bindings)
cache = LRUCache(maxsize=256)

# Large layouts (200+ bindings)
cache = LRUCache(maxsize=512)

# Memory-constrained environments
cache = WeakCache()  # GC-friendly
```

### Profiling Strategy

```python
# Development: Profile everything
if DEBUG:
    @profile("every_operation")
    def my_function():
        pass

# Production: Profile critical paths only
@profile("critical_path")
def process_large_layout():
    pass

# Conditional profiling
if PERFORMANCE_TRACKING:
    monitor = get_performance_monitor()
    with monitor.measure("operation"):
        perform_operation()
```

### Memory Management

```python
# Use weak references for large objects
cache = WeakCache()
cache.put("large_layout", large_layout_obj)

# Clear caches periodically
def periodic_cleanup():
    cache.clear()
    gc.collect()

# Use lazy evaluation
class LayoutProcessor:
    @LazyProperty
    def expensive_analysis(self):
        return analyze_entire_layout()
```

## Integration Example

Complete integration of all infrastructure components:

```python
from zmk_layout.infrastructure import (
    ProviderBuilder,
    TemplateContextBuilder,
    ChainInspector,
    PipelineComposer,
    get_performance_monitor
)

# 1. Configure providers
providers = (ProviderBuilder()
    .with_file_adapter(file_adapter)
    .with_template_adapter(template_adapter)
    .with_logger(logger)
    .enable_caching(size=256)
    .from_environment()
    .build())

# 2. Setup debugging (development only)
if DEBUG:
    inspector = ChainInspector()
    monitor = get_performance_monitor()

# 3. Create processing workflow
workflow = (PipelineComposer()
    .add_processing(processing_pipeline)
    .checkpoint("after_processing")
    .add_transformation(transformation_pipeline)
    .add_validation(validation_factory)
    .with_rollback()
    .with_error_handler(handle_error))

# 4. Process layout
with monitor.measure("total_processing"):
    processed_data = workflow.execute(layout_data)

# 5. Build template context
context = (TemplateContextBuilder()
    .with_layout(processed_data)
    .with_profile(keyboard_profile)
    .with_behaviors(behaviors, combos, macros)
    .with_generation_metadata(
        author="Generated",
        version="1.0.0"
    )
    .validate_completeness()
    .build())

# 6. Generate output
output = template_adapter.render("keymap.dtsi", context.build_dict())

# 7. Performance report (development)
if DEBUG:
    monitor.print_report()
    inspector.export_history("debug_session.json")
```

## Troubleshooting

### Common Issues

**Issue: High cache miss rate**
```python
# Check cache statistics
stats = cache.stats()
if stats['hit_rate'] < 0.5:
    # Increase cache size
    cache = LRUCache(maxsize=cache.maxsize * 2)
```

**Issue: Memory growth**
```python
# Use weak cache for large objects
cache = WeakCache()

# Clear caches periodically
cache.clear()

# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

**Issue: Slow pipeline execution**
```python
# Profile each stage
monitor = get_performance_monitor()

with monitor.measure("stage_1"):
    result1 = stage1.execute()

with monitor.measure("stage_2"):
    result2 = stage2.execute()

# Identify bottleneck
monitor.print_report()
```

**Issue: Debug overhead in production**
```python
# Conditional debugging
if os.getenv("ENABLE_DEBUG") == "true":
    inspector = ChainInspector()
    builder = inspector.wrap(builder)
else:
    # No wrapping in production
    pass
```

## API Reference

For detailed API documentation, see:
- [ProviderBuilder API](api/provider_builder.md)
- [TemplateContextBuilder API](api/template_context.md)
- [Performance API](api/performance.md)
- [Debug Tools API](api/debug_tools.md)
- [Pipeline Composition API](api/pipeline_composition.md)
