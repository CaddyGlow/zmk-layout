# Manager Classes API Reference

## Overview

Manager classes provide specialized interfaces for manipulating specific aspects of a layout. They implement the fluent API pattern, allowing for method chaining and intuitive operations.

## LayerManager

The `LayerManager` class provides methods for managing layers within a layout.

### Import

```python
from zmk_layout.core.managers import LayerManager
```

### Class: `LayerManager`

Manages the collection of layers in a layout. Accessed via `layout.layers`.

### Methods

#### `add`

```python
def add(
    self,
    name: str,
    position: Optional[int] = None
) -> LayerProxy
```

Adds a new layer to the layout.

**Parameters:**
- `name` (str): Layer name (must be unique)
- `position` (Optional[int]): Optional position to insert at (default: append)

**Returns:** `LayerProxy` for the newly created layer

**Raises:** `LayerExistsError` if layer name already exists

**Example:**
```python
# Add empty layer
layer = layout.layers.add("gaming")

# Add layer at specific position
layer = layout.layers.add("nav", position=1)

# Chain operations
layout.layers.add("gaming").set(0, "&kp W").set(1, "&kp A")
```

#### `get`

```python
def get(self, name: str) -> LayerProxy
```

Gets a layer by name.

**Parameters:**
- `name` (str): Layer name

**Returns:** `LayerProxy` for the specified layer

**Raises:** `LayerNotFoundError` if layer doesn't exist

**Example:**
```python
default_layer = layout.layers.get("default")
```

#### `remove`

```python
def remove(self, name: str) -> "LayerManager"
```

Removes a layer from the layout.

**Parameters:**
- `name` (str): Layer name to remove

**Returns:** `self` for chaining

**Raises:** `LayerNotFoundError` if layer doesn't exist

**Example:**
```python
layout.layers.remove("unused_layer")
```

#### `move`

```python
def move(self, name: str, new_index: int) -> "LayerManager"
```

Moves a layer to a new position.

**Parameters:**
- `name` (str): Layer name to move
- `new_index` (int): New position (0-based index)

**Returns:** `self` for chaining

**Example:**
```python
# Move "gaming" layer to position 1
layout.layers.move("gaming", 1)
```

#### `rename`

```python
def rename(self, old_name: str, new_name: str) -> "LayerManager"
```

Renames a layer.

**Parameters:**
- `old_name` (str): Current layer name
- `new_name` (str): New layer name

**Returns:** `self` for chaining

**Raises:** `KeyError` if layer doesn't exist, `ValueError` if new name already exists

**Example:**
```python
layout.layers.rename("layer1", "navigation")
```

#### `copy`

```python
def copy(
    self,
    source_name: str,
    target_name: str
) -> LayerProxy
```

Creates a copy of an existing layer.

**Parameters:**
- `source_name` (str): Source layer name
- `target_name` (str): Target layer name

**Returns:** `LayerProxy` for the new layer

**Raises:** `ValueError` if source not found or target exists

**Example:**
```python
# Copy default layer as template
gaming = layout.layers.copy("default", "gaming")
gaming.set(0, "&kp W")  # Customize the copy
```

#### `clear`

```python
def clear(self, name: str) -> LayerProxy
```

Clears all bindings from a specific layer.

**Parameters:**
- `name` (str): Layer name to clear

**Returns:** `LayerProxy` for the cleared layer

**Raises:** `LayerNotFoundError` if layer not found

**Example:**
```python
# Clear specific layer and continue chaining
layout.layers.clear("temp").set(0, "&kp A")
```

#### `add_multiple`

```python
def add_multiple(self, names: list[str]) -> "LayerManager"
```

Adds multiple layers at once.

**Parameters:**
- `names` (list[str]): List of layer names

**Returns:** `self` for chaining

**Example:**
```python
layout.layers.add_multiple(["nav", "sym", "num", "fn"])
```

#### `remove_multiple`

```python
def remove_multiple(self, names: list[str]) -> "LayerManager"
```

Removes multiple layers at once.

**Parameters:**
- `names` (list[str]): List of layer names to remove

**Returns:** `self` for chaining

**Example:**
```python
layout.layers.remove_multiple(["temp1", "temp2", "test"])
```

#### `reorder`

```python
def reorder(self, order: list[str]) -> "LayerManager"
```

Reorders layers according to the specified order.

**Parameters:**
- `order` (list[str]): New order of layer names

**Returns:** `self` for chaining

**Example:**
```python
layout.layers.reorder(["default", "nav", "sym", "num"])
```

#### `find`

```python
def find(self, predicate: Callable[[str], bool]) -> list[str]
```

Finds layers matching predicate function.

**Parameters:**
- `predicate` (Callable[[str], bool]): Function that takes layer name and returns bool

**Returns:** List of matching layer names

**Example:**
```python
# Find layers with "nav" in name
nav_layers = layout.layers.find(lambda name: "nav" in name)

# Find layers starting with "temp"
temp_layers = layout.layers.find(lambda name: name.startswith("temp"))
```

### Properties

#### `names`

```python
@property
def names(self) -> list[str]
```

Returns list of all layer names.

**Example:**
```python
all_layers = layout.layers.names
print(f"Layers: {', '.join(all_layers)}")
```

#### `count`

```python
@property
def count(self) -> int
```

Returns the number of layers.

**Example:**
```python
print(f"Total layers: {layout.layers.count}")
```

### Special Methods

- `__contains__(name)`: Check if layer exists
- `__len__()`: Get number of layers
- `__iter__()`: Iterate over layer names

**Example:**
```python
# Check existence
if "gaming" in layout.layers:
    print("Gaming layer exists")

# Get count
num_layers = len(layout.layers)

# Iterate
for layer_name in layout.layers:
    print(f"Processing {layer_name}")
```

---

## LayerProxy

The `LayerProxy` class provides a fluent interface for manipulating individual layers.

### Import

```python
from zmk_layout.core.managers import LayerProxy
```

### Class: `LayerProxy`

Proxy for manipulating a specific layer. Obtained via `LayerManager.add()` or `LayerManager.get()`.

### Properties

#### `parent` (Missing from Implementation)

**Note:** The `parent` property is referenced in documentation examples but is not implemented in the current LayerProxy class. Navigation back to Layout requires accessing the manager and then the Layout instance.

#### `name`

```python
@property
def name(self) -> str
```

Returns the layer name.

#### `bindings`

```python
@property
def bindings(self) -> list[LayoutBinding]
```

Returns the list of bindings in the layer.

#### `size`

```python
@property
def size(self) -> int
```

Returns the number of bindings in the layer.

### Methods

#### `set`

```python
def set(
    self,
    index: int,
    binding: Union[str, LayoutBinding]
) -> "LayerProxy"
```

Sets a binding at a specific index.

**Parameters:**
- `index` (int): Key position index (0-based)
- `binding` (Union[str, LayoutBinding]): Binding to set

**Returns:** `self` for chaining

**Note:** Layer will be automatically expanded if index is beyond current size

**Example:**
```python
layer.set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E")
```

#### `set_range`

```python
def set_range(
    self,
    start: int,
    end: int,
    bindings: list[Union[str, LayoutBinding]]
) -> "LayerProxy"
```

Sets multiple bindings in a range.

**Parameters:**
- `start` (int): Starting position (inclusive)
- `end` (int): End position (exclusive)
- `bindings` (list): List of bindings to set

**Returns:** `self` for chaining

**Raises:** `ValueError` if bindings count doesn't match range, `IndexError` if range out of bounds

**Example:**
```python
# Set WASD keys at positions 10-13
layer.set_range(10, 14, ["&kp W", "&kp A", "&kp S", "&kp D"])
```

#### `copy_from`

```python
def copy_from(self, source_layer: str) -> "LayerProxy"
```

Copies bindings from another layer.

**Parameters:**
- `source_layer` (str): Source layer name

**Returns:** `self` for chaining

**Raises:** `LayerNotFoundError` if source layer not found

**Example:**
```python
# Copy all bindings from default layer
gaming.copy_from("default")
```

#### `append`

```python
def append(self, binding: Union[str, LayoutBinding]) -> "LayerProxy"
```

Appends a binding to the end of the layer.

**Parameters:**
- `binding` (Union[str, LayoutBinding]): Binding to append

**Returns:** `self` for chaining

**Example:**
```python
layer.append("&kp SPACE").append("&kp ENTER")
```

#### `insert`

```python
def insert(
    self,
    index: int,
    binding: Union[str, LayoutBinding]
) -> "LayerProxy"
```

Inserts a binding at a specific index.

**Parameters:**
- `index` (int): Index to insert at
- `binding` (Union[str, LayoutBinding]): Binding to insert

**Returns:** `self` for chaining

**Example:**
```python
layer.insert(5, "&kp TAB")
```

#### `remove`

```python
def remove(self, index: int) -> "LayerProxy"
```

Removes a binding at a specific index.

**Parameters:**
- `index` (int): Index to remove

**Returns:** `self` for chaining

**Raises:** `IndexError` if index out of range

**Example:**
```python
layer.remove(10)
```

#### `clear`

```python
def clear(self) -> "LayerProxy"
```

Clears all bindings from the layer.

**Returns:** `self` for chaining

**Example:**
```python
layer.clear().set_range(0, new_bindings)
```

#### `fill`

```python
def fill(self, binding: Union[str, LayoutBinding], size: int) -> "LayerProxy"
```

Fills layer with binding up to specified size.

**Parameters:**
- `binding` (Union[str, LayoutBinding]): Binding to fill with
- `size` (int): Target size

**Returns:** `self` for chaining

**Example:**
```python
# Fill layer with 60 transparent bindings
layer.fill("&trans", 60)

# Fill with none bindings
layer.fill("&none", 36)
```

#### `pad_to`

```python
def pad_to(
    self,
    size: int,
    padding: Union[str, LayoutBinding] = "&trans"
) -> "LayerProxy"
```

Pads the layer to a specific size with padding binding.

**Parameters:**
- `size` (int): Target size
- `padding` (Union[str, LayoutBinding]): Binding to pad with (default: &trans)

**Returns:** `self` for chaining

**Example:**
```python
# Ensure layer has at least 60 keys
layer.pad_to(60, "&trans")
```

#### `get`

```python
def get(self, index: int) -> LayoutBinding
```

Gets a binding at a specific index.

**Parameters:**
- `index` (int): Index to get

**Returns:** LayoutBinding at index

**Raises:** `IndexError` if index out of range

**Example:**
```python
binding = layer.get(0)
# Will raise IndexError if position doesn't exist
```

### Special Methods

- `__len__()`: Get number of bindings
- `__getitem__(position)`: Get binding at position
- `__setitem__(position, binding)`: Set binding at position

**Example:**
```python
# Get length
size = len(layer)

# Get binding
binding = layer[0]

# Set binding
layer[0] = "&kp A"
```

---

## BehaviorManager

The `BehaviorManager` class provides methods for managing custom behaviors.

### Import

```python
from zmk_layout.core.managers import BehaviorManager
```

### Class: `BehaviorManager`

Manages custom behaviors like hold-taps, combos, and macros. Accessed via `layout.behaviors`.

### Methods

#### `add_hold_tap`

```python
def add_hold_tap(
    self,
    name: str,
    tap: str,
    hold: str,
    tapping_term_ms: Optional[int] = None,
    flavor: Optional[str] = None,
    **kwargs
) -> "BehaviorManager"
```

Adds a hold-tap behavior.

**Parameters:**
- `name` (str): Behavior name (with or without & prefix)
- `tap` (str): Tap binding
- `hold` (str): Hold binding
- `tapping_term_ms` (Optional[int]): Tapping term in milliseconds
- `flavor` (Optional[str]): Hold-tap flavor
- `**kwargs`: Additional hold-tap parameters

**Returns:** `self` for chaining

**Example:**
```python
layout.behaviors.add_hold_tap(
    "hm_shift",
    tap="&kp A",
    hold="&kp LSHIFT",
    tapping_term_ms=200,
    flavor="tap-preferred"
)
```

#### `add_combo`

```python
def add_combo(
    self,
    name: str,
    keys: list[int],
    binding: Union[str, LayoutBinding],
    timeout_ms: Optional[int] = None,
    layers: Optional[list[int]] = None,
    **kwargs
) -> "BehaviorManager"
```

Adds a combo behavior.

**Parameters:**
- `name` (str): Combo name
- `keys` (list[int]): List of key positions
- `binding` (Union[str, LayoutBinding]): Binding to trigger
- `timeout_ms` (Optional[int]): Combo timeout in milliseconds
- `layers` (Optional[list[int]]): Layers where combo is active (None = all layers)
- `**kwargs`: Additional combo parameters

**Returns:** `self` for chaining

**Example:**
```python
layout.behaviors.add_combo(
    "copy_combo",
    keys=[10, 11],  # Positions for C and V
    binding="&kp LC(C)",
    timeout_ms=30,
    layers=[0, 1]  # Layer indices, not names
)
```

#### `add_macro`

```python
def add_macro(
    self,
    name: str,
    sequence: list[str],
    wait_ms: Optional[int] = None,
    tap_ms: Optional[int] = None,
    **kwargs
) -> "BehaviorManager"
```

Adds a macro behavior.

**Parameters:**
- `name` (str): Macro name (with or without & prefix)
- `sequence` (list[str]): List of macro bindings
- `wait_ms` (Optional[int]): Wait time between macro steps
- `tap_ms` (Optional[int]): Tap duration for macro steps
- `**kwargs`: Additional macro parameters

**Returns:** `self` for chaining

**Example:**
```python
layout.behaviors.add_macro(
    "email_macro",
    sequence=["&kp M", "&kp Y", "&kp AT", "&kp E", "&kp M", "&kp A", "&kp I", "&kp L"],
    wait_ms=30,
    tap_ms=30
)
```

#### `add_tap_dance`

```python
def add_tap_dance(
    self,
    name: str,
    bindings: list[str],
    tapping_term_ms: Optional[int] = None,
    **kwargs
) -> "BehaviorManager"
```

Adds a tap dance behavior.

**Parameters:**
- `name` (str): Tap dance name (with or without & prefix)
- `bindings` (list[str]): List of tap dance bindings
- `tapping_term_ms` (Optional[int]): Tapping term in milliseconds
- `**kwargs`: Additional tap dance parameters

**Returns:** `self` for chaining

#### `remove_hold_tap`

```python
def remove_hold_tap(self, name: str) -> "BehaviorManager"
```

Removes a hold-tap behavior.

**Parameters:**
- `name` (str): Behavior name to remove

**Returns:** `self` for chaining

#### `remove_combo`

```python
def remove_combo(self, name: str) -> "BehaviorManager"
```

Removes a combo behavior.

**Parameters:**
- `name` (str): Combo name to remove

**Returns:** `self` for chaining

#### `remove_macro`

```python
def remove_macro(self, name: str) -> "BehaviorManager"
```

Removes a macro behavior.

**Parameters:**
- `name` (str): Macro name to remove

**Returns:** `self` for chaining

#### `remove_tap_dance`

```python
def remove_tap_dance(self, name: str) -> "BehaviorManager"
```

Removes a tap dance behavior.

**Parameters:**
- `name` (str): Tap dance name to remove

**Returns:** `self` for chaining

#### `clear_all`

```python
def clear_all(self) -> "BehaviorManager"
```

Clears all behaviors.

**Returns:** `self` for chaining

**Example:**
```python
# Clear all behaviors
layout.behaviors.clear_all()
```

#### `has_hold_tap`

```python
def has_hold_tap(self, name: str) -> bool
```

Checks if hold-tap behavior exists.

**Parameters:**
- `name` (str): Behavior name

**Returns:** True if hold-tap exists

#### `has_combo`

```python
def has_combo(self, name: str) -> bool
```

Checks if combo behavior exists.

**Parameters:**
- `name` (str): Combo name

**Returns:** True if combo exists

#### `has_macro`

```python
def has_macro(self, name: str) -> bool
```

Checks if macro behavior exists.

**Parameters:**
- `name` (str): Macro name

**Returns:** True if macro exists

#### `has_tap_dance`

```python
def has_tap_dance(self, name: str) -> bool
```

Checks if tap dance behavior exists.

**Parameters:**
- `name` (str): Tap dance name

**Returns:** True if tap dance exists

### Properties

#### `parent` (Missing from Implementation)

**Note:** The `parent` property is referenced in documentation examples but is not implemented in the current BehaviorManager class.

#### `hold_tap_count`

```python
@property
def hold_tap_count(self) -> int
```

Returns the number of hold-tap behaviors.

#### `combo_count`

```python
@property
def combo_count(self) -> int
```

Returns the number of combo behaviors.

#### `macro_count`

```python
@property
def macro_count(self) -> int
```

Returns the number of macro behaviors.

#### `tap_dance_count`

```python
@property
def tap_dance_count(self) -> int
```

Returns the number of tap dance behaviors.

#### `total_count`

```python
@property
def total_count(self) -> int
```

Returns the total number of behaviors.

**Example:**
```python
print(f"Hold-taps: {layout.behaviors.hold_tap_count}")
print(f"Combos: {layout.behaviors.combo_count}")
print(f"Macros: {layout.behaviors.macro_count}")
print(f"Tap dances: {layout.behaviors.tap_dance_count}")
print(f"Total: {layout.behaviors.total_count}")
```

## Fluent API Patterns

### Method Chaining

All manager methods return appropriate types for continued chaining:

```python
# Chain layer operations
layout.layers
    .add("gaming")
    .set(0, "&kp W")
    .set(1, "&kp A")
    .set(2, "&kp S")
    .set(3, "&kp D")
    .parent  # Return to Layout
    .export("gaming_layout.json")

# Chain multiple layer additions
layout.layers
    .add("nav")
    .parent.layers
    .add("sym")
    .parent.layers
    .add("num")
```

### Parent Navigation

**Note:** The `parent` property is not currently implemented in LayerProxy or BehaviorManager. Navigation back to the Layout requires accessing the manager and then the Layout instance.

```python
# Current workaround for navigation:
layout.layers
    .add("custom")
    .fill("&trans", 60)
    .set(10, "&kp SPACE")
# No direct .parent access - need to reference layout directly
layout.validate()
# layout.export() would be accessed directly
```

### Batch Operations

Combine with Layout's batch operation context:

```python
with layout.batch_operation():
    layout.layers.add_multiple(["l1", "l2", "l3"])
    layout.layers.get("l1").set_range(0, ["&kp A", "&kp B"])
    layout.behaviors.add_combo("test", [0, 1], "&kp ESC")
    # Validation happens automatically
```

## Error Handling

Manager classes raise specific exceptions:

- `LayerNotFoundError`: When accessing non-existent layers
- `LayerExistsError`: When trying to create layers that already exist
- `ValueError`: For invalid parameters or operations
- `IndexError`: For out-of-range positions

**Example:**
```python
from zmk_layout.core.exceptions import LayerNotFoundError, LayerExistsError

try:
    layer = layout.layers.get("nonexistent")
except LayerNotFoundError:
    print("Layer not found")

try:
    layout.layers.add("existing")
except LayerExistsError:
    print("Layer already exists")

try:
    layer.get(1000)  # Index out of range
except IndexError:
    print("Index out of range")
```