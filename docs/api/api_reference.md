# ZMK Layout Library - API Reference

## Overview

Complete API reference for the zmk-layout library v0.1.0. This document covers all public classes, methods, and functions available in the library.

## Table of Contents

1. [Core Module](#core-module-zmk_layoutcore)
2. [Models Module](#models-module-zmk_layoutmodels)
3. [Parsers Module](#parsers-module-zmk_layoutparsers)
4. [Generators Module](#generators-module-zmk_layoutgenerators)
5. [Providers Module](#providers-module-zmk_layoutproviders)
6. [Exceptions](#exceptions)
7. [Complete Example](#complete-example)

---

## Core Module (`zmk_layout.core`)

### Class: `Layout`

The main entry point for the fluent API. Provides methods for creating, loading, and manipulating keyboard layouts.

```python
from zmk_layout import Layout
```

#### Constructor

The Layout class cannot be instantiated directly with a source parameter. Use the class methods instead.

#### Class Methods

##### `create_empty()`

```python
@classmethod
def create_empty(
    cls,
    keyboard: str,
    name: str = "New Layout",
    size: int = 60,
    providers: LayoutProviders | None = None
) -> Layout
```

Create an empty layout with specified keyboard and size.

**Parameters:**
- `keyboard`: Keyboard identifier (e.g., "crkbd", "sofle", "glove80")
- `name`: Layout name
- `size`: Number of keys (default: 60)
- `providers`: Optional provider configuration

**Returns:** New Layout instance

**Example:**
```python
layout = Layout.create_empty("crkbd", "My Layout", size=42)
```

##### `from_string()`

```python
@classmethod
def from_string(
    cls,
    content: str,
    title: str = "Untitled",
    providers: LayoutProviders | None = None
) -> Layout
```

Create Layout from string content (auto-detects JSON or keymap format).

**Parameters:**
- `content`: String content (JSON or ZMK keymap)
- `title`: Optional title for the layout (used for keymap parsing)
- `providers`: Optional provider dependencies

**Returns:** Layout instance

**Example:**
```python
# Auto-detects format
layout = Layout.from_string(keymap_content)
layout = Layout.from_string(json_content)
```

##### `from_dict()`

```python
@classmethod
def from_dict(
    cls,
    data: dict[str, Any],
    providers: LayoutProviders | None = None
) -> Layout
```

Create layout from dictionary data.

**Parameters:**
- `data`: Layout data dictionary
- `providers`: Optional provider configuration

**Returns:** Layout instance

#### Instance Properties

##### `layers`

```python
@property
def layers(self) -> LayerManager
```

Access the layer manager for layer operations.

**Returns:** LayerManager instance

##### `behaviors`

```python
@property
def behaviors(self) -> BehaviorManager
```

Access the behavior manager for behavior operations.

**Returns:** BehaviorManager instance

##### `data`

```python
@property
def data(self) -> LayoutData
```

Get the underlying layout data model.

**Returns:** LayoutData instance

##### `export` (Property)

```python
@property
def export(self) -> ExportManager
```

Access export functionality with fluent interface.

**Returns:** ExportManager for generating various output formats

**Example:**
```python
# Export to keymap
keymap_str = layout.export.keymap().with_headers(True).generate()

# Export to JSON
json_str = layout.export.to_json()

# Export to dictionary
data_dict = layout.export.to_dict()
```

#### Instance Methods

##### `validate()`

```python
def validate(self) -> Layout
```

Validate layout structure and bindings.

**Returns:** Self for chaining

**Example:**
```python
layout.validate().export.to_json()
```

##### `to_dict()`

```python
def to_dict(self) -> dict[str, Any]
```

Export layout as dictionary.

**Returns:** Layout data dictionary

##### `copy()`

```python
def copy(self, deep: bool = True) -> Layout
```

Create a copy of the layout.

**Parameters:**
- `deep`: Whether to create a deep copy

**Returns:** New Layout instance

##### `get_statistics()`

```python
def get_statistics(self) -> dict[str, Any]
```

Get layout statistics.

**Returns:** Dictionary with statistics:
- `layer_count`: Number of layers
- `total_bindings`: Total number of bindings
- `binding_usage`: Dictionary of binding usage counts
- `empty_positions`: List of empty positions per layer

---

### Class: `ExportManager`

Manages export operations for layouts.

```python
# Accessed via layout.export property
export_manager = layout.export
```

#### Methods

##### `keymap()`

```python
def keymap(self, profile: Any = None) -> KeymapBuilder
```

Create a keymap builder for generating ZMK keymaps.

**Parameters:**
- `profile`: Optional keyboard profile

**Returns:** KeymapBuilder instance

##### `to_dict()`

```python
def to_dict(self) -> dict[str, Any]
```

Export layout as dictionary.

**Returns:** Layout data dictionary

##### `to_json()`

```python
def to_json(self, indent: int = 2) -> str
```

Export layout as JSON string.

**Parameters:**
- `indent`: JSON indentation

**Returns:** JSON string

---

### Class: `KeymapBuilder`

Fluent builder for keymap generation.

#### Methods

##### `with_headers()`

```python
def with_headers(self, include: bool = True) -> KeymapBuilder
```

Include/exclude headers in generated keymap.

##### `with_behaviors()`

```python
def with_behaviors(self, include: bool = True) -> KeymapBuilder
```

Include/exclude behavior definitions.

##### `with_combos()`

```python
def with_combos(self, include: bool = True) -> KeymapBuilder
```

Include/exclude combo definitions.

##### `with_macros()`

```python
def with_macros(self, include: bool = True) -> KeymapBuilder
```

Include/exclude macro definitions.

##### `generate()`

```python
def generate(self) -> str
```

Generate the final keymap string.

**Returns:** ZMK keymap content

---

### Class: `LayerManager`

Manages layout layers with fluent operations.

```python
# Accessed via layout.layers property
layer_manager = layout.layers
```

#### Properties

##### `count`

```python
@property
def count(self) -> int
```

Get the number of layers.

##### `names`

```python
@property
def names(self) -> list[str]
```

Get all layer names.

#### Methods

##### `add()`

```python
def add(
    self,
    name: str,
    position: Optional[int] = None
) -> LayerProxy
```

Add a new layer.

**Parameters:**
- `name`: Layer name
- `position`: Insert position (default: end)

**Returns:** LayerProxy for the new layer

**Raises:** `LayerExistsError` if layer already exists

##### `get()`

```python
def get(self, name: str) -> LayerProxy
```

Get layer by name.

**Parameters:**
- `name`: Layer name

**Returns:** LayerProxy for the layer

**Raises:** `LayerNotFoundError` if not found

##### `remove()`

```python
def remove(self, name: str) -> LayerManager
```

Remove a layer.

**Parameters:**
- `name`: Layer name to remove

**Returns:** Self for chaining

**Raises:** `LayerNotFoundError` if not found

##### `move()`

```python
def move(self, name: str, new_index: int) -> LayerManager
```

Move layer to new position.

**Parameters:**
- `name`: Layer name
- `new_index`: New position

**Returns:** Self for chaining

##### `rename()`

```python
def rename(self, old_name: str, new_name: str) -> LayerManager
```

Rename a layer.

**Parameters:**
- `old_name`: Current layer name
- `new_name`: New layer name

**Returns:** Self for chaining

##### `copy()`

```python
def copy(self, source_name: str, target_name: str) -> LayerProxy
```

Create a copy of an existing layer.

**Parameters:**
- `source_name`: Source layer name
- `target_name`: Target layer name

**Returns:** LayerProxy for the new layer

##### `clear()`

```python
def clear(self, name: str) -> LayerProxy
```

Clear all bindings from a specific layer.

**Parameters:**
- `name`: Layer name to clear

**Returns:** LayerProxy for the cleared layer

**Raises:** `LayerNotFoundError` if not found

##### `reorder()`

```python
def reorder(self, names: list[str]) -> LayerManager
```

Reorder all layers.

**Parameters:**
- `names`: New layer order

**Returns:** Self for chaining

##### `find()`

```python
def find(self, predicate: Callable[[str], bool]) -> list[str]
```

Find layers matching a predicate function.

**Parameters:**
- `predicate`: Function that returns True for matching layers

**Returns:** List of matching layer names

**Example:**
```python
# Find layers with "nav" in the name
nav_layers = layout.layers.find(lambda name: "nav" in name)
```

---

### Class: `LayerProxy`

Proxy for individual layer operations.

```python
# Obtained from LayerManager
layer = layout.layers.add("my_layer")
layer = layout.layers.get("existing_layer")
```

#### Properties

##### `parent`

```python
@property
def parent(self) -> Layout
```

Return to parent Layout (Note: May not be implemented in all versions).

##### `name`

```python
@property
def name(self) -> str
```

Get the layer name.

##### `size`

```python
@property
def size(self) -> int
```

Get the number of bindings.

##### `bindings`

```python
@property
def bindings(self) -> list[LayoutBinding]
```

Get the list of bindings.

#### Methods

##### `set()`

```python
def set(self, index: int, binding: str) -> LayerProxy
```

Set binding at index.

**Parameters:**
- `index`: Key position
- `binding`: ZMK binding string

**Returns:** Self for chaining

##### `set_range()`

```python
def set_range(
    self,
    start: int,
    end: int,
    bindings: list[str]
) -> LayerProxy
```

Set multiple bindings in a range.

**Parameters:**
- `start`: Start index (inclusive)
- `end`: End index (exclusive)
- `bindings`: List of bindings

**Returns:** Self for chaining

##### `copy_from()`

```python
def copy_from(self, source_layer: str) -> LayerProxy
```

Copy all bindings from another layer.

**Parameters:**
- `source_layer`: Source layer name

**Returns:** Self for chaining

**Raises:** `LayerNotFoundError` if source layer not found

##### `append()`

```python
def append(self, binding: str) -> LayerProxy
```

Append a binding to the end of the layer.

**Parameters:**
- `binding`: Binding to append

**Returns:** Self for chaining

##### `insert()`

```python
def insert(self, index: int, binding: str) -> LayerProxy
```

Insert a binding at a specific position.

**Parameters:**
- `index`: Position to insert at
- `binding`: Binding to insert

**Returns:** Self for chaining

##### `remove()`

```python
def remove(self, index: int) -> LayerProxy
```

Remove a binding at a specific position.

**Parameters:**
- `index`: Position to remove

**Returns:** Self for chaining

##### `clear()`

```python
def clear(self) -> LayerProxy
```

Clear all bindings from the layer.

**Returns:** Self for chaining

##### `fill()`

```python
def fill(self, binding: str, size: int) -> LayerProxy
```

Fill the layer with a repeated binding.

**Parameters:**
- `binding`: Binding to fill with
- `size`: Number of times to repeat

**Returns:** Self for chaining

##### `pad_to()`

```python
def pad_to(self, size: int, padding: str = "&trans") -> LayerProxy
```

Pad layer to specified size.

**Parameters:**
- `size`: Target size
- `padding`: Padding binding (default: "&trans")

**Returns:** Self for chaining

##### `get()`

```python
def get(self, index: int) -> LayoutBinding
```

Get binding at a specific position.

**Parameters:**
- `index`: Position to get

**Returns:** Binding at position

**Raises:** `IndexError` if index out of range

---

### Class: `BehaviorManager`

Manages layout behaviors (hold-taps, combos, macros, etc.).

```python
# Accessed via layout.behaviors property
behavior_manager = layout.behaviors
```

#### Properties

##### `hold_tap_count`

```python
@property
def hold_tap_count(self) -> int
```

Get the number of hold-tap behaviors.

##### `combo_count`

```python
@property
def combo_count(self) -> int
```

Get the number of combos.

##### `macro_count`

```python
@property
def macro_count(self) -> int
```

Get the number of macros.

##### `tap_dance_count`

```python
@property
def tap_dance_count(self) -> int
```

Get the number of tap dances.

#### Methods

##### `add_hold_tap()`

```python
def add_hold_tap(
    self,
    name: str,
    tap: str,
    hold: str,
    tapping_term_ms: int = 200,
    flavor: str = "tap-preferred",
    **kwargs
) -> BehaviorManager
```

Add hold-tap behavior.

**Parameters:**
- `name`: Behavior name
- `tap`: Tap binding
- `hold`: Hold binding
- `tapping_term_ms`: Tapping term (default: 200)
- `flavor`: HT flavor (default: "tap-preferred")

**Returns:** Self for chaining

##### `add_combo()`

```python
def add_combo(
    self,
    name: str,
    keys: list[int],
    binding: Union[str, LayoutBinding],
    timeout_ms: Optional[int] = None,
    layers: Optional[list[int]] = None,
    **kwargs
) -> BehaviorManager
```

Add combo behavior.

**Parameters:**
- `name`: Combo name
- `keys`: Key positions
- `binding`: Combo binding
- `timeout_ms`: Timeout in milliseconds
- `layers`: Layer indices where combo is active (not layer names)

**Returns:** Self for chaining

##### `add_macro()`

```python
def add_macro(
    self,
    name: str,
    sequence: list[str],
    wait_ms: Optional[int] = None,
    tap_ms: Optional[int] = None,
    **kwargs
) -> BehaviorManager
```

Add macro behavior.

**Parameters:**
- `name`: Macro name
- `sequence`: Macro sequence
- `wait_ms`: Wait time between keys
- `tap_ms`: Tap duration

**Returns:** Self for chaining

##### `add_tap_dance()`

```python
def add_tap_dance(
    self,
    name: str,
    bindings: list[str],
    tapping_term_ms: int = 200,
    **kwargs
) -> BehaviorManager
```

Add tap dance behavior.

**Parameters:**
- `name`: Tap dance name
- `bindings`: Tap sequence bindings
- `tapping_term_ms`: Tapping term (default: 200)

**Returns:** Self for chaining

##### `remove_hold_tap()`

```python
def remove_hold_tap(self, name: str) -> BehaviorManager
```

Remove a hold-tap behavior.

##### `remove_combo()`

```python
def remove_combo(self, name: str) -> BehaviorManager
```

Remove a combo.

##### `remove_macro()`

```python
def remove_macro(self, name: str) -> BehaviorManager
```

Remove a macro.

##### `remove_tap_dance()`

```python
def remove_tap_dance(self, name: str) -> BehaviorManager
```

Remove a tap dance.

##### `has_hold_tap()`

```python
def has_hold_tap(self, name: str) -> bool
```

Check if a hold-tap exists.

##### `has_combo()`

```python
def has_combo(self, name: str) -> bool
```

Check if a combo exists.

##### `has_macro()`

```python
def has_macro(self, name: str) -> bool
```

Check if a macro exists.

##### `has_tap_dance()`

```python
def has_tap_dance(self, name: str) -> bool
```

Check if a tap dance exists.

##### `clear_all()`

```python
def clear_all(self) -> BehaviorManager
```

Clear all behaviors.

**Returns:** Self for chaining

---

## Models Module (`zmk_layout.models`)

### Class: `LayoutBaseModel`

Base model for all layout models, providing serialization and validation.

```python
from zmk_layout.models import LayoutBaseModel
```

#### Configuration

```python
model_config = ConfigDict(
    populate_by_name=True,
    use_enum_values=True,
    arbitrary_types_allowed=True,
    extra="allow",
    str_strip_whitespace=True,
    validate_assignment=True
)
```

#### Methods

##### `to_dict()`

```python
def to_dict(self, exclude_none: bool = True) -> dict[str, Any]
```

Export model to dictionary with field aliases.

##### `to_json_string()`

```python
def to_json_string(self, indent: int = 2) -> str
```

Export model to JSON string.

##### `from_dict()`

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> LayoutBaseModel
```

Create model from dictionary.

---

### Class: `LayoutData`

Top-level layout data model (extends `LayoutMetadata`).

```python
from zmk_layout.models.metadata import LayoutData
```

#### Fields

- `keyboard` (str): Keyboard identifier (required)
- `title` (str): Layout title (required)
- `layer_names` (list[str]): Layer names
- `layers` (list[list[LayoutBinding]]): Layer definitions
- `hold_taps` (list[HoldTapBehavior]): Hold-tap behaviors (alias: "holdTaps")
- `combos` (list[ComboBehavior]): Combo definitions
- `macros` (list[MacroBehavior]): Macro definitions
- `tap_dances` (list[TapDanceBehavior]): Tap dance behaviors (alias: "tapDances")
- Additional behavior collections for sticky keys, caps words, mod morphs, etc.

---

### Class: `LayoutBinding`

Individual key binding model.

```python
from zmk_layout.models.core import LayoutBinding
```

#### Fields

- `value` (str): Binding value
- `params` (list[LayoutParam]): Binding parameters

#### Methods

##### `from_str()`

```python
@classmethod
def from_str(cls, binding_str: str) -> LayoutBinding
```

Parse binding from ZMK string.

**Parameters:**
- `binding_str`: ZMK binding (e.g., "&kp A", "&mt LCTRL ESC")

**Returns:** LayoutBinding instance

##### `to_str()`

```python
def to_str(self) -> str
```

Convert binding to ZMK string.

**Returns:** ZMK binding string

---

### Class: `HoldTapBehavior`

Hold-tap behavior definition.

```python
from zmk_layout.models.behaviors import HoldTapBehavior
```

#### Fields

- `name` (str): Behavior name
- `bindings` (list[LayoutBinding]): Hold and tap bindings
- `tapping_term_ms` (int): Tapping term
- `quick_tap_ms` (Optional[int]): Quick tap time
- `flavor` (str): HT flavor
- Additional configuration fields

---

### Class: `ComboBehavior`

Combo behavior definition.

```python
from zmk_layout.models.behaviors import ComboBehavior
```

#### Fields

- `name` (str): Combo name
- `key_positions` (list[int]): Key positions
- `bindings` (LayoutBinding): Combo binding
- `timeout_ms` (Optional[int]): Timeout
- `layers` (Optional[list[int]]): Active layer indices
- `require_prior_idle_ms` (Optional[int]): Idle requirement

---

### Class: `MacroBehavior`

Macro behavior definition.

```python
from zmk_layout.models.behaviors import MacroBehavior
```

#### Fields

- `name` (str): Macro name
- `bindings` (list[LayoutBinding]): Macro sequence
- `wait_ms` (Optional[int]): Wait between keys
- `tap_ms` (Optional[int]): Tap duration

---

## Parsers Module (`zmk_layout.parsers`)

### Class: `ZMKKeymapParser`

Main parser for ZMK keymap files.

```python
from zmk_layout.parsers import ZMKKeymapParser
```

#### Constructor

```python
ZMKKeymapParser(
    configuration_provider: Optional[ConfigurationProvider] = None,
    logger: Optional[LayoutLogger] = None
) -> ZMKKeymapParser
```

#### Methods

##### `parse_keymap()`

```python
def parse_keymap(
    self,
    content: str,
    title: str = "Untitled",
    mode: ParsingMode = ParsingMode.FULL
) -> KeymapParseResult
```

Parse keymap content to LayoutData.

**Parameters:**
- `content`: Keymap content as string
- `title`: Layout title
- `mode`: Parsing mode (FULL, FAST, etc.)

**Returns:** KeymapParseResult with layout_data field

**Raises:** `DTParseError` if parsing fails

---

### Class: `DTParser`

Devicetree parser using tokenizer approach.

```python
from zmk_layout.parsers.dt_parser import DTParser
```

#### Methods

##### `parse()`

```python
def parse(self, tokens: list[Token]) -> DTNode
```

Parse devicetree tokens to AST.

**Parameters:**
- `tokens`: List of tokens

**Returns:** DTNode representing the AST

---

### Class: `DTWalker`

Walks the devicetree AST to extract information.

```python
from zmk_layout.parsers.ast_walker import DTWalker
```

#### Methods

##### `find_nodes()`

```python
def find_nodes(self, name: str) -> list[DTNode]
```

Find nodes by name.

##### `find_properties()`

```python
def find_properties(self, name: str) -> list[DTProperty]
```

Find properties by name.

---

## Generators Module (`zmk_layout.generators`)

### Class: `ZMKGenerator`

Core generator for ZMK configuration files.

```python
from zmk_layout.generators.zmk_generator import ZMKGenerator
```

#### Constructor

```python
ZMKGenerator(
    configuration_provider: ConfigurationProvider,
    template_provider: TemplateProvider,
    logger: LayoutLogger
) -> ZMKGenerator
```

#### Methods

##### `generate_keymap_dtsi()`

```python
def generate_keymap_dtsi(
    self,
    layout_data: LayoutData,
    context: dict[str, Any]
) -> str
```

Generate keymap DTSI content.

##### `generate_behaviors_dtsi()`

```python
def generate_behaviors_dtsi(
    self,
    layout_data: LayoutData,
    context: dict[str, Any]
) -> str
```

Generate behaviors DTSI content.

---

## Providers Module (`zmk_layout.providers`)

### Class: `LayoutProviders`

Container for all provider instances (dataclass).

```python
from zmk_layout.providers import LayoutProviders
```

#### Fields

- `configuration`: ConfigurationProvider instance
- `template`: TemplateProvider instance
- `logger`: LayoutLogger instance

### Factory Functions

```python
from zmk_layout.providers.factory import (
    create_default_providers,
    create_data_only_providers
)

# Get default providers
providers = create_default_providers()

# Get minimal providers for data operations
providers = create_data_only_providers()
```

### Protocol: `ConfigurationProvider`

Configuration provider protocol.

```python
from zmk_layout.providers import ConfigurationProvider
```

#### Required Methods

- `get_behavior_definitions() -> list[SystemBehavior]`
- `get_include_files() -> list[str]`
- `get_validation_rules() -> dict[str, int | list[int] | list[str]]`
- `get_template_context() -> dict[str, str | int | float | bool | None]`

### Protocol: `TemplateProvider`

Template rendering provider protocol.

```python
from zmk_layout.providers import TemplateProvider
```

#### Required Methods

- `render_string(template: str, context: dict[str, Any]) -> str`
- `render_template(template_path: Path, context: dict[str, Any]) -> str`
- `has_template_syntax(content: str) -> bool`

### Protocol: `LayoutLogger`

Logging provider protocol.

```python
from zmk_layout.providers import LayoutLogger
```

#### Required Methods

- `debug(message: str, **kwargs: Any) -> None`
- `info(message: str, **kwargs: Any) -> None`
- `warning(message: str, **kwargs: Any) -> None`
- `error(message: str, exc_info: bool = False, **kwargs: Any) -> None`

---

## Exceptions

### `LayoutError`

Base exception for all layout errors.

### `ValidationError`

Raised when validation fails.

```python
from zmk_layout.core.exceptions import ValidationError

try:
    layout.validate()
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### `LayerNotFoundError`

Raised when layer doesn't exist.

```python
from zmk_layout.core.exceptions import LayerNotFoundError

try:
    layout.layers.get("nonexistent")
except LayerNotFoundError as e:
    print(f"Layer not found: {e}")
```

### `LayerExistsError`

Raised when trying to add a layer that already exists.

### `DTParseError`

Raised when parsing fails.

```python
from zmk_layout.parsers.exceptions import DTParseError

try:
    parser.parse_keymap(content)
except DTParseError as e:
    print(f"Parse error: {e}")
```

---

## Complete Example

```python
from zmk_layout import Layout
from zmk_layout.providers.factory import create_default_providers

# Create providers
providers = create_default_providers()

# Create layout from string (auto-detects format)
json_string = '{"keyboard": "crkbd", "title": "My Layout", "layers": [], "layer_names": []}'
layout = Layout.from_string(json_string, providers=providers)

# Or load from keymap file
from pathlib import Path
keymap_content = Path("my_layout.keymap").read_text()
layout = Layout.from_string(keymap_content, title="My Layout", providers=providers)

# Or create empty layout
layout = (Layout
    .create_empty("crkbd", "My Custom Layout", providers=providers)
    .layers
        .add("base")
        .set_range(0, 10, ["&kp Q", "&kp W", "&kp E", "&kp R", "&kp T",
                           "&kp Y", "&kp U", "&kp I", "&kp O", "&kp P"])
        .parent  # Return to Layout (if implemented)
    .layers
        .add("nav")
        .copy_from("base")
        .set(0, "&kp UP")
        .set(1, "&kp DOWN")
    # Continue with behaviors...
    )

# Export using the fluent export API
keymap_string = layout.export.keymap().with_headers(True).generate()
json_string = layout.export.to_json()
layout_dict = layout.export.to_dict()

# Get statistics
stats = layout.get_statistics()
print(f"Created layout with {stats['layer_count']} layers")
print(f"Total bindings: {stats['total_bindings']}")

# Save files
Path("output.keymap").write_text(keymap_string)
Path("output.json").write_text(json_string)
```

---

## Version History

- **0.1.0** (2024): Initial release with fluent API

---

## Support

- GitHub Issues: [zmk-layout/issues](https://github.com/CaddyGlow/zmk-layout/issues)
- Documentation: This document and additional guides in the `docs/` directory