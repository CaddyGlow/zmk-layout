# Layout Class API Reference

## Overview

The `Layout` class is the main entry point for the zmk-layout library's fluent API. It provides a comprehensive interface for creating, loading, manipulating, and exporting ZMK keyboard layouts.

## Import

```python
from zmk_layout import Layout
# or
from zmk_layout.core.layout import Layout
```

## Class: `Layout`

### Constructor

```python
Layout(
    layout_data: LayoutData,
    providers: LayoutProviders | None = None
) -> Layout
```

Creates a new Layout instance with layout data and providers.

**Parameters:**
- `layout_data` (LayoutData): Layout data model instance
- `providers` (Optional[LayoutProviders]): Custom provider configuration for dependency injection

**Returns:** `Layout` instance

**Note:** The constructor is typically not called directly. Use class methods like `from_dict`, `from_string`, or `create_empty` instead.

**Example:**
```python
# Typically use class methods instead
layout = Layout.from_dict({"keyboard": "crkbd", "layers": []})
```

### Class Methods

#### `from_dict`

```python
@classmethod
def from_dict(
    cls,
    data: dict[str, Any],
    providers: LayoutProviders | None = None
) -> Layout
```

Creates a layout from a dictionary representation.

**Parameters:**
- `data` (dict): Layout data dictionary
- `providers` (Optional[LayoutProviders]): Custom provider configuration

**Returns:** `Layout` instance

**Example:**
```python
data = {
    "keyboard": "crkbd",
    "name": "My Layout",
    "layers": [
        {"name": "default", "bindings": ["&kp Q", "&kp W"]}
    ]
}
layout = Layout.from_dict(data)
```

#### `from_string`

```python
@classmethod
def from_string(
    cls,
    content: str,
    title: str = "Untitled",
    providers: LayoutProviders | None = None
) -> Layout
```

Creates a layout from a string in various formats (auto-detects JSON or keymap format).

**Parameters:**
- `content` (str): String content (JSON or ZMK keymap)
- `title` (str): Optional title for the layout (used for keymap parsing)
- `providers` (Optional[LayoutProviders]): Custom provider configuration

**Returns:** `Layout` instance

**Raises:** `ValueError` if content format cannot be determined or parsed

**Example:**
```python
# From ZMK keymap string (auto-detected)
keymap_str = """
keymap {
    compatible = "zmk,keymap";
    default_layer {
        bindings = <&kp Q &kp W>;
    };
};
"""
layout = Layout.from_string(keymap_str, title="My Layout")

# From JSON string (auto-detected)
json_str = '{"keyboard": "crkbd", "title": "Test", "layers": []}'
layout = Layout.from_string(json_str)
```

#### `create_empty`

```python
@classmethod
def create_empty(
    cls,
    keyboard: str,
    title: str = "",
    providers: LayoutProviders | None = None
) -> Layout
```

Creates an empty layout with specified parameters.

**Parameters:**
- `keyboard` (str): Keyboard identifier (e.g., "crkbd", "sofle", "glove80")
- `title` (str): Layout title (defaults to "New {keyboard} Layout" if empty)
- `providers` (Optional[LayoutProviders]): Custom provider configuration

**Returns:** `Layout` instance with empty layers

**Example:**
```python
layout = Layout.create_empty("glove80", "My Glove80 Layout")
# Or use default title
layout = Layout.create_empty("crkbd")  # Creates "New crkbd Layout"
```

### Properties

#### `layers`

```python
@property
def layers(self) -> LayerManager
```

Returns the LayerManager for manipulating layers.

**Returns:** `LayerManager` instance

**Example:**
```python
# Access layer manager
layers = layout.layers

# Chain operations
layout.layers.add("gaming").set(0, "&kp W").set(1, "&kp A")
```

#### `behaviors`

```python
@property
def behaviors(self) -> BehaviorManager
```

Returns the BehaviorManager for manipulating behaviors.

**Returns:** `BehaviorManager` instance

**Example:**
```python
# Access behavior manager
behaviors = layout.behaviors

# Add custom behavior
layout.behaviors.add_hold_tap("my_mt", tap="&kp A", hold="&mo 1")
```

#### `data`

```python
@property
def data(self) -> LayoutData
```

Returns the underlying LayoutData model.

**Returns:** `LayoutData` instance

**Example:**
```python
# Access raw data
data = layout.data
print(f"Keyboard: {data.keyboard}")
print(f"Number of layers: {len(data.layers)}")
```

### Methods

#### `to_dict`

```python
def to_dict(self) -> dict[str, Any]
```

Converts the layout to a dictionary representation.

**Returns:** Dictionary representation of the layout

**Example:**
```python
data = layout.to_dict()
print(json.dumps(data, indent=2))
```

#### `export` (Property)

```python
@property
def export(self) -> ExportManager
```

Returns the ExportManager for generating various output formats with a fluent interface.

**Returns:** `ExportManager` instance

**Example:**
```python
# Export as keymap
keymap_content = layout.export.keymap().generate()

# Export as keymap with headers
keymap_content = layout.export.keymap().with_headers(True).generate()

# Export with custom profile
keymap_content = layout.export.keymap(profile).generate()

# Export as JSON
json_content = layout.export.to_json()

# Export as dictionary
data_dict = layout.export.to_dict()
```

#### `validate`

```python
def validate(self) -> "Layout"
```

Validates the layout and returns self for chaining.

**Returns:** `self` for method chaining

**Raises:** `ValidationError` if layout is invalid

**Example:**
```python
# Validate and continue chaining
layout.validate().layers.add("new_layer")

# Handle validation errors
try:
    layout.validate()
    print("Layout is valid!")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

#### `copy`

```python
def copy(self) -> "Layout"
```

Creates a copy of the layout.

**Returns:** New `Layout` instance with copied data

**Example:**
```python
# Create a copy for experimentation
experimental = layout.copy()
experimental.layers.add("test_layer")
# Original layout remains unchanged
```

#### `batch_operation`

```python
def batch_operation(self, operations: list[Callable[["Layout"], Any]]) -> "Layout"
```

Execute multiple operations in batch and return self for chaining.

**Parameters:**
- `operations` (list[Callable[["Layout"], Any]]): List of functions that take Layout as argument

**Returns:** `self` for method chaining

**Example:**
```python
layout.batch_operation([
    lambda l: l.layers.add("gaming"),
    lambda l: l.layers.get("gaming").set(0, "&kp ESC"),
    lambda l: l.behaviors.add_hold_tap("hm", "&kp A", "&mo 1")
])
```

#### `find_layers`

```python
def find_layers(self, predicate: Callable[[str], bool]) -> list[str]
```

Find layers matching predicate.

**Parameters:**
- `predicate` (Callable[[str], bool]): Function that takes layer name and returns bool

**Returns:** List of matching layer names

**Example:**
```python
# Find all layers with "game" in the name
gaming_layers = layout.find_layers(lambda name: "game" in name.lower())

# Find layers with specific naming pattern
nav_layers = layout.find_layers(lambda name: name.startswith("nav_"))
```

#### `get_statistics`

```python
def get_statistics(self) -> dict[str, Any]
```

Get layout statistics.

**Returns:** Dictionary containing:
- `keyboard`: Keyboard name
- `title`: Layout title
- `layer_count`: Number of layers
- `layer_names`: List of layer names
- `total_bindings`: Total number of bindings
- `behavior_counts`: Dictionary with counts of hold_taps, combos, macros, tap_dances
- `total_behaviors`: Total behavior count
- `layer_sizes`: Dictionary mapping layer names to layer sizes (if layers exist)
- `avg_layer_size`: Average layer size (if layers exist)
- `max_layer_size`: Maximum layer size (if layers exist)
- `min_layer_size`: Minimum layer size (if layers exist)

**Example:**
```python
stats = layout.get_statistics()
print(f"Layers: {stats['layer_count']}")
print(f"Total bindings: {stats['total_bindings']}")
print(f"Layer names: {stats['layer_names']}")
print(f"Hold-taps: {stats['behavior_counts']['hold_taps']}")
```

### Context Manager Support

The Layout class supports context manager protocol for automatic resource management:

```python
with Layout.create_empty("crkbd", "Test Layout") as layout:
    layout.layers.add("new_layer")
    # Resources are automatically cleaned up
```

### Special Methods

#### `__repr__`

```python
def __repr__(self) -> str
```

Returns a string representation of the layout.

**Example:**
```python
layout = Layout.create_empty("crkbd", "My Layout")
print(layout)  # Output: Layout(keyboard='crkbd', layers=0)
```

## Error Handling

The Layout class uses custom exceptions for error handling:

- `LayoutError`: Base exception for all layout-related errors
- `ValidationError`: Raised when validation fails
- `ParseError`: Raised when parsing fails
- `ExportError`: Raised when export fails

**Example:**
```python
from pathlib import Path
from zmk_layout.core.exceptions import LayoutError, ValidationError

try:
    invalid_content = Path("invalid_file.keymap").read_text()
    layout = Layout.from_string(invalid_content)
except ValueError as e:  # from_string raises ValueError for parsing errors
    print(f"Failed to parse layout: {e}")
except ValidationError as e:
    print(f"Validation failed: {e}")
except LayoutError as e:
    print(f"Layout error: {e}")
```

## Best Practices

1. **Use context managers** for automatic resource cleanup:
   ```python
   with Layout.create_empty("crkbd", "Test Layout") as layout:
       # Operations here
   ```

2. **Validate before export** to ensure correctness:
   ```python
   layout.validate()  # Returns self for chaining, raises ValidationError if invalid
   keymap_content = layout.export.keymap().generate()
   ```

3. **Use batch operations** for multiple changes:
   ```python
   layout.batch_operation([
       lambda l: l.layers.add("new_layer"),
       lambda l: l.behaviors.add_hold_tap("hm", "&kp A", "&mo 1")
   ])
   ```

4. **Chain operations** for concise code:
   ```python
   layout = Layout.create_empty("crkbd", "New")
   layout.layers.add("nav").set(0, "&kp UP")
   json_content = layout.export.to_json()
   ```

5. **Create copies** for experimentation:
   ```python
   test_layout = layout.copy()
   # Experiment with test_layout
   ```