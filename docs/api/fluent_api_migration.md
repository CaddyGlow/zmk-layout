# ZMK Layout Library - Fluent API Migration Guide

## Overview

This guide helps you migrate from the traditional imperative API to the new fluent API in the ZMK Layout Library. The fluent API provides better readability, type safety, and a more intuitive development experience while maintaining full backward compatibility.

## Table of Contents

1. [Migration Strategy](#migration-strategy)
2. [API Comparison](#api-comparison)
3. [Step-by-Step Migration](#step-by-step-migration)
4. [Common Patterns](#common-patterns)
5. [Troubleshooting](#troubleshooting)
6. [Compatibility Layer](#compatibility-layer)

## Migration Strategy

### Gradual Migration Approach

The library is designed to support gradual migration. You can:

1. **Mix both styles** in the same codebase
2. **Migrate file by file** or feature by feature
3. **Keep existing code** working without changes
4. **Adopt fluent patterns** where they provide the most value

### Migration Priorities

Focus on migrating these areas first for maximum benefit:

1. **Layout creation and configuration** - Biggest readability improvement
2. **Layer management** - Most frequently used operations
3. **Pipeline operations** - Best performance gains
4. **Behavior definitions** - Clearest intent expression

## API Comparison

### Layout Creation

#### Old API (Imperative)
```python
# Traditional imperative approach
layout = Layout()
layout.keyboard = "crkbd"
layout.name = "My Layout"
layout.author = "John Doe"
layout.description = "A custom Corne layout"
layout.metadata = {"version": "1.0"}
```

#### New API (Fluent)
```python
# Fluent chainable approach
layout = (Layout
    .create_empty("crkbd", "My Layout")
    .with_author("John Doe")
    .with_description("A custom Corne layout")
    .with_metadata({"version": "1.0"}))
```

### Layer Management

#### Old API (Imperative)
```python
# Adding and configuring layers
layer = Layer("base")
layer.bindings = [None] * 42

# Set individual bindings
layer.bindings[0] = "&kp Q"
layer.bindings[1] = "&kp W"
layer.bindings[2] = "&kp E"

# Fill remaining with trans
for i in range(3, 42):
    layer.bindings[i] = "&trans"

layout.layers.append(layer)
```

#### New API (Fluent)
```python
# Fluent layer management
layout = (layout.layers
    .add("base")
    .set(0, "&kp Q")
    .set(1, "&kp W")
    .set(2, "&kp E")
    .pad_to(42, "&trans")
    .parent())
```

### Behavior Definition

#### Old API (Imperative)
```python
# Define hold-tap behavior
ht = HoldTapBehavior()
ht.name = "hm"
ht.hold_behavior = "&kp"
ht.tap_behavior = "&kp"
ht.tapping_term_ms = 200
ht.quick_tap_ms = 150
ht.flavor = "tap-preferred"

layout.behaviors.append(ht)
```

#### New API (Fluent)
```python
# Fluent behavior definition
layout = (layout.behaviors
    .add_hold_tap("hm",
        hold="&kp",
        tap="&kp",
        tapping_term_ms=200,
        quick_tap_ms=150,
        flavor="tap-preferred")
    .parent())
```

### File Operations

#### Old API (Imperative)
```python
# Load and save
with open("layout.json", "r") as f:
    data = json.load(f)
layout = Layout.from_dict(data)

# Modify
layout.name = "Modified"

# Save
with open("output.json", "w") as f:
    json.dump(layout.to_dict(), f)
```

#### New API (Fluent)
```python
# Fluent file operations
layout = (Layout
    .from_file("layout.json")
    .with_name("Modified")
    .save("output.json"))
```

## Step-by-Step Migration

### Step 1: Identify Migration Candidates

Start by identifying code that would benefit most from migration:

```python
# Look for patterns like this:
layout = Layout()
layout.prop1 = value1
layout.prop2 = value2
layout.method1()
layout.method2()

# These are perfect candidates for fluent chains
```

### Step 2: Create a Migration Wrapper

For complex migrations, create a wrapper to maintain compatibility:

```python
class LayoutMigrationWrapper:
    """Wrapper to support both old and new APIs during migration"""

    def __init__(self, layout=None):
        self._layout = layout or Layout.create_empty("crkbd", "Default")

    # Old API support
    @property
    def keyboard(self):
        return self._layout.keyboard

    @keyboard.setter
    def keyboard(self, value):
        self._layout = self._layout.with_keyboard(value)

    # Bridge to new API
    def fluent(self):
        """Get fluent interface"""
        return self._layout

    # Forward fluent methods
    def __getattr__(self, name):
        return getattr(self._layout, name)
```

### Step 3: Migrate Layer Operations

Convert layer operations incrementally:

```python
# Before: Imperative layer creation
def create_base_layer_old():
    layer = Layer("base")
    for i, key in enumerate(QWERTY_KEYS):
        layer.bindings[i] = f"&kp {key}"
    return layer

# After: Fluent layer creation
def create_base_layer_new(layout):
    return (layout.layers
        .add("base")
        .set_range(0, len(QWERTY_KEYS),
                  [f"&kp {key}" for key in QWERTY_KEYS])
        .parent())
```

### Step 4: Migrate Behavior Definitions

Convert behavior definitions to fluent style:

```python
# Before: Multiple behavior definitions
def add_behaviors_old(layout):
    # Hold-tap
    ht = HoldTapBehavior()
    ht.name = "hm"
    ht.hold_behavior = "&kp"
    ht.tap_behavior = "&kp"
    layout.behaviors.append(ht)

    # Macro
    macro = MacroBehavior()
    macro.name = "copy"
    macro.bindings = ["&kp LC(C)"]
    layout.behaviors.append(macro)

    return layout

# After: Fluent behavior definitions
def add_behaviors_new(layout):
    return (layout.behaviors
        .add_hold_tap("hm", hold="&kp", tap="&kp")
        .add_macro("copy", bindings=["&kp LC(C)"])
        .parent())
```

### Step 5: Migrate Pipeline Operations

Convert processing pipelines:

```python
# Before: Imperative pipeline
def process_layout_old(input_file):
    # Load
    with open(input_file) as f:
        data = json.load(f)

    # Parse
    layout = Layout.from_dict(data)

    # Validate
    validator = Validator()
    errors = validator.validate(layout)
    if errors:
        raise ValidationError(errors)

    # Generate
    generator = Generator()
    keymap = generator.generate_keymap(layout)
    behaviors = generator.generate_behaviors(layout)

    return keymap, behaviors

# After: Fluent pipeline
def process_layout_new(input_file):
    return (ProcessingPipeline()
        .from_file(input_file)
        .validate()
        .generate_keymap()
        .generate_behaviors()
        .execute())
```

## Common Patterns

### Pattern 1: Conditional Operations

#### Old Pattern
```python
layout = Layout()
if condition:
    layout.add_layer("extra")
    layout.layers[-1].bindings = bindings
```

#### New Pattern
```python
layout = Layout.create_empty("crkbd", "Conditional")
if condition:
    layout = layout.layers.add("extra", bindings=bindings).parent()
```

### Pattern 2: Bulk Operations

#### Old Pattern
```python
# Add multiple layers
for name in ["base", "nav", "num", "sym"]:
    layer = Layer(name)
    layout.layers.append(layer)
```

#### New Pattern
```python
# Chain multiple additions
layout = (layout.layers
    .add("base")
    .add("nav")
    .add("num")
    .add("sym")
    .parent())

# Or use batch operation
layout = layout.layers.add_multiple(["base", "nav", "num", "sym"]).parent()
```

### Pattern 3: Complex Transformations

#### Old Pattern
```python
# Transform all bindings
for layer in layout.layers:
    for i, binding in enumerate(layer.bindings):
        if binding == "&trans":
            layer.bindings[i] = "&none"
```

#### New Pattern
```python
# Use transformation pipeline
layout = (layout
    .transform_bindings(lambda b: b.replace("&trans", "&none"))
    .validate())
```

### Pattern 4: Error Handling

#### Old Pattern
```python
try:
    layout = load_layout(file_path)
except FileNotFoundError:
    layout = Layout()
    layout.keyboard = "crkbd"
except ValidationError as e:
    print(f"Error: {e}")
    layout = None
```

#### New Pattern
```python
layout = (Layout
    .from_file_safe(file_path)
    .or_else(Layout.create_empty("crkbd", "Fallback"))
    .validate_safe()
    .unwrap_or_none())
```

## Troubleshooting

### Issue 1: Lost Fluent Context

**Problem**: Can't continue chaining after certain operations

```python
# Problem: Lost context
layer = layout.layers.add("base")
layer.set(0, "&kp Q")  # Now we're on LayerProxy
# Can't get back to layout easily
```

**Solution**: Use `.parent()` to navigate back

```python
# Solution: Use parent()
layout = (layout.layers
    .add("base")
    .set(0, "&kp Q")
    .parent()  # Back to layout
    .layers.add("nav")
    .parent())
```

### Issue 2: Type Hints Not Working

**Problem**: IDE doesn't recognize fluent methods

```python
# Problem: Type lost
layout = layout.layers.add("base")  # Type is now LayerProxy
layout.save()  # Error: LayerProxy has no 'save' method
```

**Solution**: Use type annotations

```python
# Solution: Maintain type
from zmk_layout import Layout

layout: Layout = layout.layers.add("base").parent()
layout.save()  # Works: IDE knows it's a Layout
```

### Issue 3: Immutability Confusion

**Problem**: Original object unexpectedly unchanged

```python
# Problem: Expecting mutation
original = Layout.create_empty("crkbd", "Original")
original.with_name("Modified")  # Returns new instance
print(original.name)  # Still "Original"!
```

**Solution**: Capture returned instance

```python
# Solution: Capture new instance
original = Layout.create_empty("crkbd", "Original")
modified = original.with_name("Modified")
print(modified.name)  # "Modified"
print(original.name)  # "Original" (unchanged)
```

### Issue 4: Missing Terminal Methods

**Problem**: Pipeline doesn't execute

```python
# Problem: No execution
pipeline = GeneratorPipeline().from_layout(layout).generate_keymap()
# Nothing happens!
```

**Solution**: Call terminal method

```python
# Solution: Call execute()
result = (GeneratorPipeline()
    .from_layout(layout)
    .generate_keymap()
    .execute())  # Terminal method triggers execution
```

## Compatibility Layer

### Maintaining Both APIs

For libraries that need to support both APIs:

```python
class DualAPILayout:
    """Layout supporting both imperative and fluent APIs"""

    def __init__(self):
        self._layout = Layout.create_empty("crkbd", "Dual API")

    # Imperative API (deprecated)
    def add_layer(self, name: str) -> None:
        """Deprecated: Use fluent API instead"""
        warnings.warn("add_layer is deprecated, use .layers.add()",
                     DeprecationWarning)
        self._layout = self._layout.layers.add(name).parent()

    # Fluent API
    @property
    def layers(self):
        """Access fluent layer manager"""
        return self._layout.layers

    # Allow fluent chaining from imperative instance
    def fluent(self) -> Layout:
        """Convert to fluent interface"""
        return self._layout
```

### Deprecation Strategy

```python
import warnings
from functools import wraps

def deprecated(message: str):
    """Decorator for deprecated methods"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated. {message}",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

class Layout:
    @deprecated("Use .with_name() instead")
    def set_name(self, name: str) -> None:
        """Deprecated method for backward compatibility"""
        self.name = name
```

### Migration Utilities

```python
class MigrationHelper:
    """Utilities to help with migration"""

    @staticmethod
    def convert_imperative_to_fluent(old_code: str) -> str:
        """Convert imperative code to fluent style"""
        # Simple pattern replacements
        replacements = [
            (r'layout\.keyboard = "(.*)"', r'layout = layout.with_keyboard("\1")'),
            (r'layout\.name = "(.*)"', r'layout = layout.with_name("\1")'),
            (r'layout\.add_layer\((.*)\)', r'layout = layout.layers.add(\1).parent()'),
        ]

        result = old_code
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)

        return result

    @staticmethod
    def validate_migration(old_layout, new_layout) -> bool:
        """Verify migration produced equivalent result"""
        return (
            old_layout.to_dict() == new_layout.to_dict() and
            old_layout.layers == new_layout.layers and
            old_layout.behaviors == new_layout.behaviors
        )
```

## Migration Checklist

Use this checklist to track your migration progress:

- [ ] **Phase 1: Assessment**
  - [ ] Identify all files using the old API
  - [ ] Prioritize files for migration
  - [ ] Set up compatibility layer if needed

- [ ] **Phase 2: Core Migration**
  - [ ] Migrate layout creation and configuration
  - [ ] Migrate layer management operations
  - [ ] Migrate behavior definitions
  - [ ] Update file I/O operations

- [ ] **Phase 3: Advanced Features**
  - [ ] Convert processing pipelines
  - [ ] Update validation logic
  - [ ] Migrate generation pipelines
  - [ ] Convert transformation operations

- [ ] **Phase 4: Testing**
  - [ ] Update unit tests
  - [ ] Add migration tests
  - [ ] Verify backward compatibility
  - [ ] Performance testing

- [ ] **Phase 5: Documentation**
  - [ ] Update code examples
  - [ ] Add migration notes to docs
  - [ ] Update API reference
  - [ ] Create migration guide for users

- [ ] **Phase 6: Cleanup**
  - [ ] Remove deprecated code (after grace period)
  - [ ] Update type hints
  - [ ] Remove compatibility layers (if appropriate)
  - [ ] Final documentation review

## Next Steps

After completing your migration:

1. **Review the [Fluent API Documentation](./fluent_api.md)** for advanced features
2. **Check out [Examples](./fluent_api_examples.md)** for real-world usage patterns
3. **Join the community** for migration support and best practices
4. **Contribute** your migration experiences to help others

## Support

If you encounter issues during migration:

- Check the [Troubleshooting](#troubleshooting) section
- Review the [GitHub Issues](https://github.com/zmk-layout/issues)
- Ask in [Discussions](https://github.com/zmk-layout/discussions)
- Consult the [API Reference](./api_reference.md)
