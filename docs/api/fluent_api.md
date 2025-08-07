# ZMK Layout Library - Fluent API Documentation

## Overview

The ZMK Layout Library provides a comprehensive fluent API that enables intuitive, chainable operations for keyboard layout manipulation. This document covers all fluent interfaces available in the library, from basic layout operations to advanced pipeline configurations.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Layout API](#core-layout-api)
3. [Layer Management](#layer-management)
4. [Behavior Management](#behavior-management)
5. [Binding Builder](#binding-builder)
6. [Generation Pipeline](#generation-pipeline)
7. [Processing Pipeline](#processing-pipeline)
8. [Validation Pipeline](#validation-pipeline)
9. [Provider Configuration](#provider-configuration)
10. [Advanced Patterns](#advanced-patterns)
11. [Migration Guide](#migration-guide)

## Getting Started

### Installation

```bash
pip install zmk-layout
```

### Basic Usage

The fluent API follows an immutable builder pattern where each method call returns a new instance:

```python
from zmk_layout import Layout

# Create a new layout using fluent chains
layout = (Layout
    .create_empty("crkbd", "My Custom Layout")
    .layers.add("base")
        .set(0, "&kp Q")
        .set(1, "&kp W")
        .set(2, "&kp E")
        .set(3, "&kp R")
        .set(4, "&kp T")
    .parent()
    .layers.add("nav")
        .pad_to(42, "&trans")
    .parent()
    .save("my_layout.json"))
```

### Key Principles

1. **Immutability**: Methods return new instances, preserving the original
2. **Type Safety**: Full type hints and IDE support with `Self` return types
3. **Lazy Evaluation**: Operations are deferred until terminal methods
4. **Context Navigation**: Use `.parent()` to navigate up the chain

## Core Layout API

### Layout Creation

```python
from zmk_layout import Layout

# From scratch
layout = Layout.create_empty("crkbd", "My Layout")

# From existing file
layout = Layout.from_file("existing_layout.json")

# From DTSI
layout = Layout.from_dtsi("keymap.dtsi")

# Clone existing
new_layout = layout.clone().with_name("Modified Layout")
```

### Layout Properties

```python
# Chainable property setters
layout = (layout
    .with_name("New Name")
    .with_description("Updated description")
    .with_author("Your Name")
    .with_metadata({"version": "2.0", "date": "2024-01-15"})
    .with_keyboard("sofle")
    .validate())
```

### Layout Operations

```python
# Complex operations
layout = (layout
    .normalize()  # Normalize all bindings
    .optimize()   # Remove redundant definitions
    .compress()   # Minimize JSON size
    .export("output.json", format="zmk"))  # Export in specific format
```

## Layer Management

### Adding Layers

```python
# Add single layer
layout = layout.layers.add("gaming")

# Add multiple layers at once
layout = (layout.layers
    .add("base")
    .add("nav")
    .add("num")
    .add("sym"))

# Add with initial bindings
layout = (layout.layers
    .add("base", bindings=["&kp Q", "&kp W", "&kp E"])
    .pad_to(42, "&trans"))
```

### Layer Manipulation

```python
# Access specific layer
base_layer = layout.layers.get("base")

# Layer operations
layout = (layout.layers
    .get("base")
        .set(0, "&kp Q")
        .set_range(0, 5, ["&kp Q", "&kp W", "&kp E", "&kp R", "&kp T"])
        .fill(10, 20, "&kp SPACE")
        .pad_to(42, "&trans")
        .clear()
        .copy_from("template_layer")
    .parent()  # Return to layout context
    .layers.get("nav")
        .mirror_from("base", transform=lambda b: b.replace("kp", "mo"))
    .parent())
```

### Layer Reordering

```python
# Reorder layers
layout = (layout.layers
    .move("nav", 1)  # Move nav to position 1
    .swap("num", "sym")  # Swap two layers
    .sort()  # Sort alphabetically
    .reverse())  # Reverse layer order
```

### Layer Removal

```python
# Remove layers
layout = (layout.layers
    .remove("temp")
    .remove_all(["debug", "test"])
    .keep_only(["base", "nav", "num"]))
```

## Behavior Management

### Adding Behaviors

```python
# Add hold-tap behavior
layout = (layout.behaviors
    .add_hold_tap("hm",
        hold="&kp",
        tap="&mo",
        tapping_term_ms=200,
        quick_tap_ms=125,
        flavor="tap-preferred")
    .add_hold_tap("lt",
        hold="&mo",
        tap="&kp",
        tapping_term_ms=150))

# Add macro
layout = (layout.behaviors
    .add_macro("copy_all",
        bindings=["&kp LC(A)", "&kp LC(C)"],
        wait_ms=30,
        tap_ms=40))

# Add combo
layout = (layout.behaviors
    .add_combo("esc_combo",
        keys=[0, 1],
        bindings=["&kp ESC"],
        timeout_ms=50,
        layers=["base", "nav"]))

# Add tap dance
layout = (layout.behaviors
    .add_tap_dance("td_quotes",
        bindings=["&kp SQT", "&kp DQT", "&kp GRAVE"]))
```

### Behavior Configuration

```python
# Configure existing behaviors
layout = (layout.behaviors
    .configure("hm", tapping_term_ms=180)
    .configure_all("hold_tap", quick_tap_ms=100)
    .set_default("tapping_term_ms", 200))
```

### Behavior Queries

```python
# Query behaviors
hold_taps = layout.behaviors.filter(type="hold_tap")
fast_behaviors = layout.behaviors.filter(lambda b: b.tapping_term_ms < 150)
layer_behaviors = layout.behaviors.used_in_layer("base")
```

## Binding Builder

### Basic Bindings

```python
from zmk_layout import Binding

# Simple key press
binding = Binding.kp("A")  # &kp A

# Modified key
binding = Binding.kp("A").with_mods("LC", "LS")  # &kp LC(LS(A))

# Layer tap
binding = Binding.lt(1, "SPACE")  # &lt 1 SPACE

# Momentary layer
binding = Binding.mo(2)  # &mo 2
```

### Complex Bindings

```python
# Hold-tap with mods
binding = (Binding
    .ht("hm")
    .hold("&kp LSHIFT")
    .tap("&kp A")
    .build())  # &hm LSHIFT A

# Macro binding
binding = (Binding
    .macro("email_sig")
    .build())  # &email_sig

# Conditional binding
binding = (Binding
    .when(layer="gaming")
        .then("&kp SPACE")
        .else_("&lt 1 SPACE")
    .build())
```

### Binding Transformations

```python
# Transform existing binding
original = "&kp A"
modified = (Binding
    .parse(original)
    .add_mod("LCTRL")
    .add_mod("LSHIFT")
    .stringify())  # &kp LC(LS(A))

# Batch transformation
bindings = ["&kp Q", "&kp W", "&kp E"]
modified = [Binding.parse(b).add_mod("LGUI").stringify() for b in bindings]
```

## Generation Pipeline

### Basic Generation

```python
from zmk_layout import GeneratorPipeline

# Generate ZMK files
result = (GeneratorPipeline()
    .from_layout(layout)
    .generate_keymap()
    .generate_behaviors()
    .generate_combos()
    .write_to("output/"))
```

### Custom Generation

```python
# Configure generation
result = (GeneratorPipeline()
    .from_layout(layout)
    .with_template("custom_template.dtsi.j2")
    .with_context({
        "author": "Your Name",
        "version": "1.0.0",
        "timestamp": datetime.now()
    })
    .filter_layers(["base", "nav"])
    .transform_bindings(lambda b: b.replace("trans", "none"))
    .validate()
    .generate())
```

### Output Formats

```python
# Multiple output formats
result = (GeneratorPipeline()
    .from_layout(layout)
    .as_dtsi()  # Generate DTSI
    .as_json()  # Generate JSON
    .as_yaml()  # Generate YAML
    .as_header()  # Generate C header
    .write_all("output/"))
```

## Processing Pipeline

### AST Processing

```python
from zmk_layout import ProcessingPipeline

# Process keymaps
result = (ProcessingPipeline()
    .from_dtsi("keymap.dtsi")
    .parse()
    .extract_layers()
    .extract_behaviors()
    .normalize_bindings()
    .optimize()
    .to_layout())
```

### Transformations

```python
# Apply transformations
result = (ProcessingPipeline()
    .from_layout(layout)
    .transform(lambda node: node.replace_binding("&trans", "&none"))
    .filter(lambda node: node.layer != "debug")
    .map(lambda node: node.with_metadata({"processed": True}))
    .reduce(lambda acc, node: acc.merge(node))
    .build())
```

### Custom Processors

```python
# Add custom processor
class CustomProcessor:
    def process(self, node):
        # Custom processing logic
        return modified_node

result = (ProcessingPipeline()
    .add_processor(CustomProcessor())
    .add_validator(lambda n: n.is_valid())
    .process())
```

## Validation Pipeline

### Basic Validation

```python
from zmk_layout import ValidationPipeline

# Validate layout
result = (ValidationPipeline()
    .for_layout(layout)
    .check_binding_syntax()
    .check_layer_consistency()
    .check_behavior_definitions()
    .validate())

if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")
```

### Custom Validators

```python
# Add custom validators
result = (ValidationPipeline()
    .for_layout(layout)
    .add_rule(lambda l: len(l.layers) > 0, "Layout must have at least one layer")
    .add_rule(lambda l: l.keyboard in SUPPORTED_KEYBOARDS, "Unsupported keyboard")
    .add_warning(lambda l: len(l.layers) > 10, "Too many layers may impact performance")
    .validate())
```

### Validation Levels

```python
# Configure validation strictness
result = (ValidationPipeline()
    .for_layout(layout)
    .with_level("strict")  # strict, normal, lenient
    .ignore_warnings()
    .fail_fast()  # Stop on first error
    .validate())
```

## Provider Configuration

### Basic Configuration

```python
from zmk_layout import ProviderBuilder

# Configure providers
providers = (ProviderBuilder()
    .with_file_adapter(my_file_adapter)
    .with_template_adapter(jinja_adapter)
    .with_logger(structured_logger)
    .build())
```

### Advanced Configuration

```python
# Full configuration
providers = (ProviderBuilder()
    .with_file_adapter(custom_file_adapter)
    .with_template_adapter(jinja2_adapter)
    .with_logger(structlog.get_logger())
    .with_configuration_provider(profile_provider)
    .enable_caching(size=512)
    .enable_debug_mode()
    .enable_performance_tracking()
    .from_environment()  # Load from env vars
    .validate()
    .build())

# Create service with providers
service = providers.create_layout_service()
```

### Environment Configuration

```python
# Configure from environment
import os
os.environ["ZMK_LAYOUT_DEBUG"] = "true"
os.environ["ZMK_LAYOUT_CACHE_SIZE"] = "1024"

providers = (ProviderBuilder()
    .from_environment()
    .build())
```

## Advanced Patterns

### Pipeline Composition

```python
# Compose multiple pipelines
result = (ProcessingPipeline()
    .from_dtsi("input.dtsi")
    .parse()
    .pipe_to(ValidationPipeline()
        .check_syntax()
        .check_semantics())
    .pipe_to(GeneratorPipeline()
        .generate_keymap()
        .generate_behaviors())
    .execute())
```

### Conditional Chains

```python
# Conditional operations
layout = (layout
    .when(lambda l: l.keyboard == "crkbd")
        .then(lambda l: l.layers.add("thumb_cluster"))
    .when(lambda l: len(l.layers) > 5)
        .then(lambda l: l.optimize())
    .otherwise(lambda l: l))
```

### Batch Operations

```python
# Process multiple layouts
layouts = ["layout1.json", "layout2.json", "layout3.json"]

results = (Layout
    .batch(layouts)
    .map(lambda l: l.normalize())
    .filter(lambda l: l.is_valid())
    .transform(lambda l: l.optimize())
    .collect())
```

### Error Handling

```python
# Graceful error handling
result = (Layout
    .from_file("layout.json")
    .try_operation(lambda l: l.layers.add("new"))
    .catch(FileNotFoundError, lambda: Layout.create_empty("crkbd", "Fallback"))
    .catch(ValidationError, lambda e: print(f"Validation failed: {e}"))
    .finally_(lambda l: l.save("backup.json")))
```

### Debugging Support

```python
# Enable debugging
layout = (Layout
    .from_file("layout.json")
    .debug()  # Enable debug output
    .tap(lambda l: print(f"Layers: {len(l.layers)}"))  # Inspection
    .breakpoint()  # Debugger breakpoint
    .profile()  # Performance profiling
    .layers.add("test")
    .end_profile())  # End profiling
```

## Migration Guide

### From Imperative to Fluent

#### Before (Imperative)
```python
# Old imperative style
layout = Layout()
layout.keyboard = "crkbd"
layout.name = "My Layout"

base_layer = Layer("base")
base_layer.bindings[0] = "&kp Q"
base_layer.bindings[1] = "&kp W"
layout.layers.append(base_layer)

nav_layer = Layer("nav")
for i in range(42):
    nav_layer.bindings[i] = "&trans"
layout.layers.append(nav_layer)

layout.save("output.json")
```

#### After (Fluent)
```python
# New fluent style
layout = (Layout
    .create_empty("crkbd", "My Layout")
    .layers.add("base")
        .set(0, "&kp Q")
        .set(1, "&kp W")
    .parent()
    .layers.add("nav")
        .pad_to(42, "&trans")
    .parent()
    .save("output.json"))
```

### Gradual Migration

The library supports gradual migration - you can mix imperative and fluent styles:

```python
# Mixed style (during migration)
layout = Layout.create_empty("crkbd", "My Layout")

# Imperative for complex logic
if complex_condition:
    base_layer = layout.layers.add("base")
    for i, key in enumerate(complex_key_list):
        base_layer.set(i, key)

# Fluent for simple operations
layout = layout.layers.add("nav").pad_to(42, "&trans").parent()

layout.save("output.json")
```

### Compatibility Patterns

```python
# Backward compatible wrapper
class LayoutCompat:
    """Wrapper for backward compatibility"""

    def __init__(self, layout):
        self._layout = layout

    # Old API
    def add_layer(self, name, bindings=None):
        self._layout = self._layout.layers.add(name, bindings)
        return self

    # Bridge to new API
    def fluent(self):
        return self._layout
```

## Best Practices

### 1. Use Context Navigation

```python
# Good: Use parent() to navigate contexts
layout = (layout.layers
    .add("base")
        .set(0, "&kp Q")
    .parent()  # Return to layers context
    .add("nav")
        .set(0, "&mo 1")
    .parent())  # Return to layers context

# Avoid: Breaking the chain
base = layout.layers.add("base")
base.set(0, "&kp Q")
nav = layout.layers.add("nav")  # Lost fluent context
```

### 2. Leverage Immutability

```python
# Good: Save intermediate states
base_layout = layout.layers.add("base").parent()
with_nav = base_layout.layers.add("nav").parent()
final = with_nav.layers.add("sym").parent()

# Can still use base_layout unchanged
alternative = base_layout.layers.add("gaming").parent()
```

### 3. Use Terminal Methods

```python
# Good: Clear terminal operations
result = (pipeline
    .configure()
    .validate()
    .build())  # Terminal method executes pipeline

# Avoid: Forgetting terminal methods
pipeline.configure().validate()  # Nothing happens!
```

### 4. Type-Safe Patterns

```python
from typing import Self

class CustomLayout(Layout):
    def custom_operation(self) -> Self:
        # Returns same type for chaining
        return self._copy_with(custom=True)

# Type checker knows the type
layout: CustomLayout = CustomLayout().custom_operation().layers.add("test")
```

### 5. Error Handling

```python
# Good: Handle errors gracefully
layout = (Layout
    .from_file_safe("layout.json")
    .or_else(Layout.create_empty("crkbd", "Fallback"))
    .validate_safe()
    .unwrap_or_log())

# Good: Validate before operations
if layout.can_add_layer("test"):
    layout = layout.layers.add("test")
```

## Performance Considerations

### Lazy Evaluation

Most fluent operations are lazy and don't execute until needed:

```python
# Operations are deferred
pipeline = (GeneratorPipeline()
    .from_layout(layout)
    .filter_layers(["base", "nav"])  # Not executed yet
    .transform_bindings(transform_fn))  # Not executed yet

# Execution happens here
result = pipeline.generate()  # Now all operations execute
```

### Caching

Enable caching for repeated operations:

```python
providers = (ProviderBuilder()
    .enable_caching(size=512)
    .build())

# Cached operations
layout = Layout.with_providers(providers)
result1 = layout.validate()  # First call, cached
result2 = layout.validate()  # Retrieved from cache
```

### Memory Management

The immutable pattern creates new objects, but with optimizations:

```python
# Structural sharing minimizes memory overhead
layout1 = Layout.create_empty("crkbd", "Layout")
layout2 = layout1.with_name("New Name")  # Shares most data with layout1
```

## Troubleshooting

### Common Issues

#### 1. Lost Context
```python
# Problem: Lost fluent context
layer = layout.layers.add("base")
layer.set(0, "&kp Q")
# Can't continue chaining from layout

# Solution: Use parent()
layout = layout.layers.add("base").set(0, "&kp Q").parent()
```

#### 2. Forgotten Terminal Methods
```python
# Problem: Pipeline not executing
pipeline.from_layout(layout).generate_keymap()
# Nothing happens!

# Solution: Call terminal method
result = pipeline.from_layout(layout).generate_keymap().execute()
```

#### 3. Type Errors
```python
# Problem: Type checker confusion
layout = layout.layers.add("base")  # Type is now LayerProxy

# Solution: Use parent() or type annotations
layout: Layout = layout.layers.add("base").parent()
```

### Debug Mode

Enable debug mode for detailed operation logs:

```python
# Enable globally
Layout.enable_debug_mode()

# Or per instance
layout = Layout.create_empty("crkbd", "Debug").debug()

# Detailed operation logging
layout = (layout
    .tap(print)  # Print current state
    .layers.add("test")
    .tap(lambda l: print(f"Added layer: {l.name}"))
    .parent())
```

## API Reference

For complete API documentation, see:
- [Layout API](./layout_api.md)
- [Layer Manager API](./layer_manager_api.md)
- [Behavior Manager API](./behavior_manager_api.md)
- [Pipeline APIs](./pipeline_apis.md)
- [Provider API](./provider_api.md)

## Examples Repository

Find complete examples at: [github.com/zmk-layout/examples](https://github.com/zmk-layout/examples)

- Basic layout creation
- Complex behavior definitions
- Multi-keyboard support
- Pipeline compositions
- Custom processors
- Migration patterns

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines on:
- Adding new fluent methods
- Creating custom processors
- Extending validation rules
- Performance optimizations

## Support

- **Issues**: [github.com/zmk-layout/issues](https://github.com/zmk-layout/issues)
- **Discussions**: [github.com/zmk-layout/discussions](https://github.com/zmk-layout/discussions)
- **Documentation**: [zmk-layout.readthedocs.io](https://zmk-layout.readthedocs.io)
