# Fluent API Complete Guide

## Overview

The zmk-layout library provides a powerful fluent API that enables intuitive method chaining for keyboard layout manipulation. This guide covers all aspects of the fluent API design, patterns, and best practices.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [API Flow](#api-flow)
3. [Method Chaining](#method-chaining)
4. [Navigation Patterns](#navigation-patterns)
5. [Export API](#export-api)
6. [Common Patterns](#common-patterns)
7. [Advanced Usage](#advanced-usage)
8. [Best Practices](#best-practices)
9. [Complete Examples](#complete-examples)

---

## Core Concepts

### Fluent Interface Design

The fluent API is designed around these principles:

1. **Method Chaining**: Every method returns an appropriate object for continued operations
2. **Intuitive Navigation**: Clear paths between different API components
3. **Type Safety**: Full type hints for IDE support
4. **Immutability Options**: Support for both mutable and immutable operations
5. **Context Preservation**: Operations maintain context for natural flow

### Object Hierarchy

```
Layout (entry point)
├── LayerManager (.layers)
│   └── LayerProxy (individual layer operations)
└── BehaviorManager (.behaviors)
```

Each level provides specific operations while maintaining navigation paths back to parent objects.

---

## API Flow

### Standard Flow Pattern

```python
# 1. Create/Load Layout
layout = Layout("my_layout.keymap")

# 2. Navigate to Manager
layer_manager = layout.layers

# 3. Perform Operation
layer_proxy = layer_manager.add("new_layer")

# 4. Configure
layer_proxy.set(0, "&kp A")

# 5. Navigate Back
layout_again = layer_proxy.parent

# 6. Export/Save
layout_again.export.keymap().generate()  # Generate keymap content
# or
layout_again.export.to_json()  # Generate JSON string
```

### Chained Flow

```python
Layout("my_layout.keymap")
    .layers.add("new_layer")
    .set(0, "&kp A")
    .parent
    .export.keymap().generate()
```

---

## Method Chaining

### Chain Types

#### 1. Self-Returning Chains

Methods that return `self` for continued operations on the same object:

```python
layout.layers
    .add_multiple(["layer1", "layer2", "layer3"])
    .remove("old_layer")
    .reorder(["default", "layer1", "layer2", "layer3"])
```

#### 2. Navigation Chains

Methods that return different objects for navigation:

```python
layout
    .layers           # Returns LayerManager
    .add("gaming")   # Returns LayerProxy
    .parent          # Returns Layout
    .behaviors       # Returns BehaviorManager
```

#### 3. Transformation Chains

Methods that create modified copies:

```python
modified = layout
    .copy()
    .layers.add("test")
    .parent
```

### Return Type Reference

| Class | Method | Returns | Purpose |
|-------|--------|---------|---------|
| Layout | `.layers` | LayerManager | Access layer operations |
| Layout | `.behaviors` | BehaviorManager | Access behavior operations |
| Layout | `.copy()` | Layout | Create a copy |
| Layout | `.export` | ExportManager | Access export functionality |
| Layout | `.validate()` | Layout | Validate and return self for chaining |
| LayerManager | `.add()` | LayerProxy | Add and configure layer |
| LayerManager | `.get()` | LayerProxy | Get existing layer |
| LayerManager | `.remove()` | LayerManager | Remove and continue |
| LayerProxy | `.set()` | LayerProxy | Set binding and continue |
| LayerProxy | `.parent` | Layout | Navigate back to Layout |
| LayerProxy | `.set_range()` | LayerProxy | Set multiple bindings and continue |

---

## Navigation Patterns

### Parent Navigation

Use `.parent` property to navigate back:

```python
# From LayerProxy to Layout
layout.layers.add("test").parent  # Back to Layout

# From BehaviorManager to Layout
layout.behaviors.add_combo(...).parent  # Back to Layout
```

### Deep Navigation

Navigate through multiple levels:

```python
layout
    .layers.add("layer1")      # In LayerProxy
    .parent                     # Back to Layout
    .layers.add("layer2")      # In LayerProxy
    .parent                     # Back to Layout
    .behaviors.add_macro(...)  # In BehaviorManager
    .parent                     # Back to Layout
```

### Sibling Navigation

Move between managers:

```python
layout.layers
    .add("test")
    .parent        # Back to Layout
    .behaviors     # To BehaviorManager
    .add_combo(...)
    .parent        # Back to Layout
    .layers        # To LayerManager again
```

---

## Export API

The export API provides a fluent interface for generating various output formats from layouts. All export operations are accessed through the `.export` property of a Layout.

### Basic Export Operations

```python
# Export as JSON
json_string = layout.export.to_json(indent=2)
json_dict = layout.export.to_dict()

# Export as keymap with default settings  
keymap_content = layout.export.keymap().generate()

# Export config file
config_content, kconfig_dict = layout.export.config().generate()
```

### Keymap Export with Options

The keymap builder provides extensive customization options:

```python
# Customized keymap export
keymap_content = (layout.export
    .keymap(profile)  # Optional profile for keyboard-specific settings
    .with_headers(True)  # Include standard ZMK headers
    .with_behaviors(True)  # Include hold-tap definitions
    .with_combos(True)  # Include combo definitions
    .with_macros(True)  # Include macro definitions
    .with_tap_dances(True)  # Include tap dance definitions
    .with_template("custom_template.j2")  # Use custom template
    .with_context(author="John Doe", version="1.0")  # Add template variables
    .generate())

# Minimal keymap (no headers, behaviors, etc.)
minimal_keymap = (layout.export
    .keymap()
    .with_headers(False)
    .with_behaviors(False)
    .with_combos(False)
    .with_macros(False)
    .generate())
```

### Config Export with Options

```python
# Basic config export
config_content, kconfig_dict = layout.export.config().generate()

# Config with custom options
config_content, kconfig_dict = (layout.export
    .config(profile)
    .with_options(
        CONFIG_ZMK_SLEEP=True,
        CONFIG_ZMK_IDLE_SLEEP_TIMEOUT=600000
    )
    .with_defaults(True)  # Include default options
    .generate())
```

### Export Chaining

Since export methods are designed for terminal operations, they typically end the fluent chain:

```python
# Export after layout operations
keymap_content = (Layout.create_empty("crkbd", "My Layout")
    .layers.add("default")
    .set_range(0, 5, ["&kp Q", "&kp W", "&kp E", "&kp R", "&kp T"])
    .parent
    .validate()
    .export.keymap().generate())

# Multiple exports from same layout
json_data = layout.export.to_json()
keymap_data = layout.export.keymap().generate()
config_data, kconfig = layout.export.config().generate()
```

---

## Common Patterns

### Pattern 1: Create and Configure

```python
# Create empty layout and configure
Layout.create_empty("crkbd", "My Layout")
    .layers.add("default")
    .set_range(0, 5, ["&kp Q", "&kp W", "&kp E", "&kp R", "&kp T"])
    .parent
    .layers.add("navigation")
    .copy_from("default")
    .set(10, "&kp UP")
    .parent
)

# Generate keymap content
keymap_content = layout.export.keymap().generate()
```

### Pattern 2: Load and Modify

```python
# Load existing and modify
Layout("existing.keymap")
    .layers.remove("unused")
    .add("new_layer")
    .pad_to(42, "&trans")  # Assuming 42-key layout
    .set(20, "&kp SPACE")
    .parent
    .validate()
)

# Generate modified keymap content
modified_keymap_content = enhanced.export.keymap().generate()
```

### Pattern 3: Batch Operations

```python
# Perform multiple operations efficiently
with layout.batch_operation():
    layout.layers
        .add_multiple(["nav", "sym", "num"])
        .get("nav").set_range(0, len(arrow_keys), arrow_keys)
        .parent.layers
        .get("sym").set_range(0, len(symbols), symbols)
        .parent.layers
        .get("num").set_range(0, len(numbers), numbers)
```

### Pattern 4: Conditional Operations

```python
# Add layer only if it doesn't exist
if "gaming" not in layout.layers:
    layout.layers.add("gaming").copy_from("default")

# Modify existing or create new
layer = (layout.layers.get("gaming") 
         if "gaming" in layout.layers 
         else layout.layers.add("gaming"))
layer.set(0, "&kp W")
```

### Pattern 5: Iterator Chains

```python
# Process all layers
for layer_name in layout.layers:
    layer = layout.layers.get(layer_name)
    if layer.size < 60:
        layer.pad_to(60, "&trans")
```

---

## Advanced Usage

### Custom Fluent Wrappers

Create custom fluent wrappers for specific workflows:

```python
class FluentLayoutBuilder:
    def __init__(self, keyboard: str):
        self.layout = Layout.create_empty(keyboard, "Custom")
    
    def with_layer(self, name: str) -> "FluentLayoutBuilder":
        self.layout.layers.add(name)
        return self
    
    def with_gaming_layer(self) -> "FluentLayoutBuilder":
        self.layout.layers.add("gaming").set_range(0, 4, [
            "&kp W", "&kp A", "&kp S", "&kp D"
        ])
        return self
    
    def build(self) -> Layout:
        return self.layout

# Usage
layout = (FluentLayoutBuilder("crkbd")
    .with_layer("default")
    .with_gaming_layer()
    .with_layer("symbols")
    .build())
```

### Functional Composition

Compose operations functionally:

```python
from functools import reduce

operations = [
    lambda l: l.layers.add("layer1").parent,
    lambda l: l.layers.add("layer2").parent,
    lambda l: l.layers.get("layer1").set(0, "&kp A").parent,
    lambda l: l.validate()
]

result = reduce(lambda layout, op: op(layout), operations, layout)
```

### Pipeline Pattern

Create processing pipelines:

```python
class LayoutPipeline:
    def __init__(self):
        self.steps = []
    
    def add_step(self, func):
        self.steps.append(func)
        return self
    
    def process(self, layout):
        for step in self.steps:
            layout = step(layout)
        return layout

# Define pipeline
pipeline = (LayoutPipeline()
    .add_step(lambda l: l.layers.add("test").parent)
    .add_step(lambda l: l.layers.get("test").pad_to(42, "&trans").parent)
    .add_step(lambda l: l.validate()))

# Process layout
result = pipeline.process(layout)
```

### Context Managers

Use context managers for transactional operations:

```python
class LayoutTransaction:
    def __init__(self, layout):
        self.layout = layout
        self.backup = None
    
    def __enter__(self):
        self.backup = self.layout.copy()
        return self.layout
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Restore backup on error
            self.layout._data = self.backup._data
        return False

# Usage
with LayoutTransaction(layout) as txn:
    txn.layers.add("experimental")
    txn.layers.get("experimental").set(0, "&kp TEST")
    # Automatically rolled back if error occurs
```

---

## Best Practices

### 1. Chain Length

Keep chains readable - break long chains:

```python
# Good - Readable chunks
layout = Layout("my.keymap")
gaming_layer = layout.layers.add("gaming")
gaming_layer.copy_from("default")
gaming_layer.set(0, "&kp W").set(1, "&kp A")
keymap_content = layout.export.keymap().generate()

# Avoid - Too long
Layout("my.keymap").layers.add("gaming").copy_from("default").set(0, "&kp W").set(1, "&kp A").set(2, "&kp S").set(3, "&kp D").parent.layers.add("nav").set(0, "&kp UP").parent.export.keymap().generate()
```

### 2. Variable Assignment

Assign intermediate results when needed:

```python
# Good - Clear intent
layout = Layout("config.keymap")
nav_layer = layout.layers.add("navigation")
nav_layer.set_range(0, len(arrow_keys), arrow_keys)

# Also good - When you need the reference
default = layout.layers.get("default")
gaming = layout.layers.copy(default.name, "gaming")
```

### 3. Error Handling

Handle errors in chains appropriately:

```python
try:
    result = (Layout("input.keymap")
        .layers.get("nonexistent")  # May raise KeyError
        .set(0, "&kp A"))
except KeyError:
    print("Layer not found")
```

### 4. Type Hints

Use type hints for clarity:

```python
from zmk_layout import Layout, LayerProxy

def configure_layer(layer: LayerProxy) -> LayerProxy:
    return layer.set(0, "&kp ESC").set(1, "&kp TAB")

layout: Layout = Layout("my.keymap")
layer: LayerProxy = layout.layers.add("custom")
configured: LayerProxy = configure_layer(layer)
```

### 5. Immutability

Use `.copy()` for immutable operations:

```python
# Original unchanged
original = Layout("base.keymap")
modified = original.copy().layers.add("test").parent

# Original modified
layout = Layout("base.keymap")
layout.layers.add("test")  # Modifies layout
```

---

## Complete Examples

### Example 1: Building a Complete Layout

```python
from zmk_layout import Layout

# Create a complete Corne keyboard layout
corne_layout = (
    Layout.create_empty("crkbd", "My Corne Layout", size=42)
    
    # Configure default layer
    .layers.add("default")
    .set_range(0, 15, [
        "&kp Q", "&kp W", "&kp E", "&kp R", "&kp T",
        "&kp A", "&kp S", "&kp D", "&kp F", "&kp G",
        "&kp Z", "&kp X", "&kp C", "&kp V", "&kp B",
    ])
    .set(36, "&mo 1")  # Layer tap
    .set(37, "&kp SPACE")
    .set(38, "&kp ENTER")
    .parent
    
    # Add navigation layer
    .layers.add("navigation")
    .pad_to(42, "&trans")  # Assuming 42-key layout
    .set_range(15, 19, [
        "&kp LEFT", "&kp DOWN", "&kp UP", "&kp RIGHT"
    ])
    .parent
    
    # Add symbols layer
    .layers.add("symbols")
    .pad_to(42, "&trans")  # Assuming 42-key layout
    .set_range(0, 5, [
        "&kp EXCL", "&kp AT", "&kp HASH", "&kp DOLLAR", "&kp PERCENT"
    ])
    .parent
    
    # Add behaviors
    .behaviors.add_combo(
        "escape_combo",
        keys=[0, 1],
        binding="&kp ESC",
        timeout_ms=30
    )
    .add_hold_tap(
        "hm_shift",
        tap="&kp A",
        hold="&kp LSHIFT",
        tapping_term_ms=200
    )
    .parent
    
    # Validate and export
    .validate()
    .export("corne_complete.keymap")
)
```

### Example 2: Modifying Existing Layout

```python
# Load and enhance an existing layout
enhanced = (
    Layout("basic.keymap")
    
    # Clean up
    .layers.remove_multiple(["temp", "test", "unused"])
    
    # Enhance default layer
    .layers.get("default")
    .set(36, "&mt LCTRL SPACE")  # Add mod-tap
    .parent
    
    # Add gaming layer if not exists
    .layers.add("gaming") if "gaming" not in layout.layers else layout
    .layers.get("gaming")
    .copy_from("default")
    .set_range(10, 14, ["&kp W", "&kp A", "&kp S", "&kp D"])
    .parent
    
    # Add useful combos
    .behaviors
    .add_combo("copy", [2, 3], "&kp LC(C)")
    .add_combo("paste", [3, 4], "&kp LC(V)")
    .add_combo("undo", [1, 2], "&kp LC(Z)")
    .parent
    
    # Export enhanced version
    .export("enhanced.keymap")
)
```

### Example 3: Template-based Generation

```python
def create_programmer_layout(keyboard: str, hand_size: str = "medium"):
    """Create an optimized programmer layout."""
    
    # Base layout
    layout = Layout.create_empty(keyboard, f"Programmer {hand_size.title()}")
    
    # Define key positions based on hand size
    if hand_size == "small":
        home_row = [10, 11, 12, 13]  # Closer together
    else:
        home_row = [11, 12, 13, 14]  # Standard positions
    
    return (
        layout
        # Coding layer with easy brackets
        .layers.add("code")
        .set(home_row[0], "&kp LBKT")
        .set(home_row[1], "&kp RBKT")
        .set(home_row[2], "&kp LPAR")
        .set(home_row[3], "&kp RPAR")
        .parent
        
        # Vim navigation layer
        .layers.add("vim")
        .set_range(home_row[0], home_row[0] + 4, [
            "&kp H", "&kp J", "&kp K", "&kp L"
        ])
        .parent
        
        # Common programming combos
        .behaviors
        .add_combo("arrow", [0, 1], "&macro_arrow")  # ->
        .add_combo("comment", [2, 3], "&macro_comment")  # //
        .parent
    )

# Generate for different keyboards
corne_programmer = create_programmer_layout("crkbd").export("corne_prog.keymap")
sofle_programmer = create_programmer_layout("sofle").export("sofle_prog.keymap")
```

### Example 4: Bulk Processing

```python
def standardize_layouts(directory: Path):
    """Standardize all layouts in a directory."""
    
    for keymap_file in directory.glob("*.keymap"):
        try:
            (Layout(keymap_file)
                # Ensure standard layers exist
                .layers.add("default") if "default" not in layout.layers else layout
                .layers.add("nav") if "nav" not in layout.layers else layout
                .layers.add("sym") if "sym" not in layout.layers else layout
                
                # Standardize layer order
                .layers.reorder(["default", "nav", "sym"] + 
                               [l for l in layout.layers.names 
                                if l not in ["default", "nav", "sym"]])
                
                # Validate
                .validate()
                
                # Save with backup
            )
            
            # Generate standardized content
            standardized_content = layout.export.keymap().generate()
            
            # Save to file
            standardized_path = keymap_file.with_suffix(".standardized.keymap")
            standardized_path.write_text(standardized_content))
                
            print(f"✓ Standardized {keymap_file.name}")
            
        except Exception as e:
            print(f"✗ Failed {keymap_file.name}: {e}")
```

---

## Fluent API Quick Reference

### Layout Methods
- `Layout.from_dict(data)` → Layout
- `Layout.from_string(content)` → Layout
- `Layout.create_empty(keyboard, title)` → Layout
- `.layers` → LayerManager
- `.behaviors` → BehaviorManager
- `.copy()` → Layout
- `.export` → ExportManager
- `.validate()` → Layout
- `.to_dict()` → dict
- `.get_statistics()` → dict

### LayerManager Methods
- `.add(name, position=None)` → LayerProxy
- `.get(name)` → LayerProxy
- `.remove(name)` → LayerManager
- `.move(name, position)` → LayerManager
- `.rename(old_name, new_name)` → LayerManager
- `.copy(source, target)` → LayerProxy
- `.clear(name)` → LayerProxy
- `.add_multiple(names)` → LayerManager
- `.remove_multiple(names)` → LayerManager
- `.reorder(names)` → LayerManager
- `.find(predicate)` → list[str]
- `.names` → list[str] (property)
- `.count` → int (property)

### LayerProxy Methods
- `.set(pos, binding)` → LayerProxy
- `.set_range(start, end, bindings)` → LayerProxy
- `.copy_from(source)` → LayerProxy
- `.fill(binding, size)` → LayerProxy
- `.pad_to(size, padding)` → LayerProxy
- `.append(binding)` → LayerProxy
- `.insert(index, binding)` → LayerProxy
- `.remove(index)` → LayerProxy
- `.clear()` → LayerProxy
- `.get(index)` → LayoutBinding
- `.parent` → Layout (property, not method)
- `.name` → str (property)
- `.size` → int (property)
- `.bindings` → list[LayoutBinding] (property)

### BehaviorManager Methods
- `.add_hold_tap(name, tap, hold, ...)` → BehaviorManager
- `.add_combo(name, keys, binding, ...)` → BehaviorManager
- `.add_macro(name, bindings, ...)` → BehaviorManager
- `.add_tap_dance(name, bindings, ...)` → BehaviorManager
- `.remove(name)` → BehaviorManager
- `.clear()` → BehaviorManager
- `.parent` → Layout (property)

### ExportManager Methods
- `.keymap(profile=None)` → KeymapBuilder
- `.config(profile=None)` → ConfigBuilder
- `.to_dict()` → dict
- `.to_json(indent=2)` → str

### KeymapBuilder Methods
- `.with_headers(include=True)` → KeymapBuilder
- `.with_behaviors(include=True)` → KeymapBuilder
- `.with_combos(include=True)` → KeymapBuilder
- `.with_macros(include=True)` → KeymapBuilder
- `.with_tap_dances(include=True)` → KeymapBuilder
- `.with_template(template_path)` → KeymapBuilder
- `.with_context(**kwargs)` → KeymapBuilder
- `.generate()` → str

### ConfigBuilder Methods
- `.with_options(**options)` → ConfigBuilder
- `.with_defaults(use=True)` → ConfigBuilder
- `.generate()` → tuple[str, dict]