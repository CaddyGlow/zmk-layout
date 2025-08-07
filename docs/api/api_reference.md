# ZMK Layout Library - API Reference

## Overview

Complete API reference for the zmk-layout library v0.1.0. This document covers all public classes, methods, and functions available in the library.

## Table of Contents

1. [Core Module](#core-module-zmk_layoutcore)
2. [Models Module](#models-module-zmk_layoutmodels)
3. [Parsers Module](#parsers-module-zmk_layoutparsers)
4. [Generators Module](#generators-module-zmk_layoutgenerators)
5. [Providers Module](#providers-module-zmk_layoutproviders)
6. [Builders Module](#builders-module-zmk_layoutbuilders)
7. [Processing Module](#processing-module-zmk_layoutprocessing)
8. [Validation Module](#validation-module-zmk_layoutvalidation)
9. [Infrastructure Module](#infrastructure-module-zmk_layoutinfrastructure)
10. [Utils Module](#utils-module-zmk_layoututils)

---

## Core Module (`zmk_layout.core`)

### Class: `Layout`

The main entry point for the fluent API. Provides methods for creating, loading, and manipulating keyboard layouts.

```python
from zmk_layout import Layout
```

#### Constructor

```python
Layout(
    source: Union[str, Path, dict],
    providers: Optional[LayoutProviders] = None
) -> Layout
```

**Parameters:**
- `source`: File path, dictionary, or layout data
- `providers`: Optional provider configuration

#### Class Methods

##### `create_empty()`
```python
@classmethod
def create_empty(
    cls,
    keyboard: str,
    name: str,
    size: int = 60,
    providers: Optional[LayoutProviders] = None
) -> Layout
```
Create an empty layout with specified keyboard and size.

**Parameters:**
- `keyboard`: Keyboard identifier (e.g., "crkbd", "sofle")
- `name`: Layout name
- `size`: Number of keys (default: 60)
- `providers`: Optional provider configuration

**Returns:** New Layout instance

**Example:**
```python
layout = Layout.create_empty("crkbd", "My Layout", size=42)
```


##### `from_keymap_string()`
```python
@classmethod
def from_keymap_string(
    cls,
    keymap_content: str,
    providers: Optional[LayoutProviders] = None
) -> Layout
```
Parse layout from ZMK keymap string.

**Parameters:**
- `keymap_content`: Keymap content as string
- `providers`: Optional provider configuration

**Returns:** Layout instance

##### `from_dict()`
```python
@classmethod
def from_dict(
    cls,
    data: dict[str, Any],
    providers: Optional[LayoutProviders] = None
) -> Layout
```
Create layout from dictionary data.

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

##### `metadata`
```python
@property
def metadata(self) -> dict[str, Any]
```
Get layout metadata.

**Returns:** Metadata dictionary

#### Instance Methods


##### `validate()`
```python
def validate(self) -> Layout
```
Validate layout structure and bindings.

**Returns:** Self for chaining

**Raises:** `ValidationError` if invalid

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
- `indent`: JSON indentation (default: 2)

**Returns:** JSON string

##### `generate_keymap()`
```python
def generate_keymap(self, template: Optional[str] = None) -> str
```
Generate ZMK keymap code.

**Parameters:**
- `template`: Optional template string (if not provided, uses default template)

**Returns:** Keymap DTSI content as string

##### `generate_behaviors()`
```python
def generate_behaviors(self) -> str
```
Generate ZMK behavior definitions.

**Returns:** Behaviors DTSI content as string

##### `clone()`
```python
def clone(self) -> Layout
```
Create a deep copy of the layout.

**Returns:** New Layout instance

##### `with_name()`
```python
def with_name(self, name: str) -> Layout
```
Set layout name (fluent).

**Parameters:**
- `name`: New layout name

**Returns:** New Layout instance

##### `with_author()`
```python
def with_author(self, author: str) -> Layout
```
Set layout author (fluent).

**Parameters:**
- `author`: Author name

**Returns:** New Layout instance

##### `with_description()`
```python
def with_description(self, description: str) -> Layout
```
Set layout description (fluent).

**Parameters:**
- `description`: Layout description

**Returns:** New Layout instance

##### `get_statistics()`
```python
def get_statistics(self) -> dict[str, Any]
```
Get layout statistics.

**Returns:** Dictionary with statistics:
- `layer_count`: Number of layers
- `behavior_count`: Number of behaviors
- `binding_count`: Total bindings
- `combo_count`: Number of combos
- `macro_count`: Number of macros

---

### Class: `LayerManager`

Manages layout layers with fluent operations.

```python
from zmk_layout.core.managers import LayerManager
```

#### Methods

##### `add()`
```python
def add(
    self,
    name: str,
    position: Optional[int] = None,
    bindings: Optional[list[str]] = None
) -> LayerProxy
```
Add a new layer.

**Parameters:**
- `name`: Layer name
- `position`: Insert position (default: end)
- `bindings`: Initial bindings

**Returns:** LayerProxy for the new layer

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

##### `move()`
```python
def move(self, name: str, position: int) -> LayerManager
```
Move layer to new position.

**Parameters:**
- `name`: Layer name
- `position`: New position

**Returns:** Self for chaining

##### `reorder()`
```python
def reorder(self, names: list[str]) -> LayerManager
```
Reorder all layers.

**Parameters:**
- `names`: New layer order

**Returns:** Self for chaining

##### `list()`
```python
def list(self) -> list[str]
```
List all layer names.

**Returns:** List of layer names

##### `parent()`
```python
def parent(self) -> Layout
```
Return to parent Layout.

**Returns:** Parent Layout instance

---

### Class: `LayerProxy`

Proxy for individual layer operations.

```python
from zmk_layout.core.managers import LayerProxy
```

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
Set multiple bindings.

**Parameters:**
- `start`: Start index
- `end`: End index (exclusive)
- `bindings`: List of bindings

**Returns:** Self for chaining

##### `copy_from()`
```python
def copy_from(self, source_layer: str) -> LayerProxy
```
Copy bindings from another layer.

**Parameters:**
- `source_layer`: Source layer name

**Returns:** Self for chaining

##### `pad_to()`
```python
def pad_to(self, size: int, binding: str = "&trans") -> LayerProxy
```
Pad layer to specified size.

**Parameters:**
- `size`: Target size
- `binding`: Padding binding (default: "&trans")

**Returns:** Self for chaining

##### `parent()`
```python
def parent(self) -> Layout
```
Return to parent Layout.

**Returns:** Parent Layout instance

---

### Class: `BehaviorManager`

Manages layout behaviors (hold-taps, combos, macros, etc.).

```python
from zmk_layout.core.managers import BehaviorManager
```

#### Methods

##### `add_hold_tap()`
```python
def add_hold_tap(
    self,
    name: str,
    hold: str,
    tap: str,
    tapping_term_ms: int = 200,
    quick_tap_ms: int = 0,
    flavor: str = "tap-preferred",
    **kwargs
) -> BehaviorManager
```
Add hold-tap behavior.

**Parameters:**
- `name`: Behavior name
- `hold`: Hold binding
- `tap`: Tap binding
- `tapping_term_ms`: Tapping term (default: 200)
- `quick_tap_ms`: Quick tap time (default: 0)
- `flavor`: HT flavor (default: "tap-preferred")

**Returns:** Self for chaining

##### `add_combo()`
```python
def add_combo(
    self,
    name: str,
    keys: list[int],
    binding: str,
    timeout_ms: int = 50,
    layers: Optional[list[str]] = None,
    **kwargs
) -> BehaviorManager
```
Add combo behavior.

**Parameters:**
- `name`: Combo name
- `keys`: Key positions
- `binding`: Combo binding
- `timeout_ms`: Timeout (default: 50)
- `layers`: Active layers (default: all)

**Returns:** Self for chaining

##### `add_macro()`
```python
def add_macro(
    self,
    name: str,
    bindings: list[str],
    wait_ms: int = 30,
    tap_ms: int = 30,
    **kwargs
) -> BehaviorManager
```
Add macro behavior.

**Parameters:**
- `name`: Macro name
- `bindings`: Macro sequence
- `wait_ms`: Wait time between keys (default: 30)
- `tap_ms`: Tap time (default: 30)

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

##### `remove()`
```python
def remove(self, name: str) -> BehaviorManager
```
Remove a behavior.

**Parameters:**
- `name`: Behavior name

**Returns:** Self for chaining

##### `list()`
```python
def list(self) -> list[str]
```
List all behavior names.

**Returns:** List of behavior names

##### `parent()`
```python
def parent(self) -> Layout
```
Return to parent Layout.

**Returns:** Parent Layout instance

---

## Models Module (`zmk_layout.models`)

### Class: `LayoutBaseModel`

Base model for all layout models, providing serialization and validation.

```python
from zmk_layout.models import LayoutBaseModel
```

#### Methods

##### `to_dict()`
```python
def to_dict(self) -> dict[str, Any]
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

Top-level layout data model.

```python
from zmk_layout.models.metadata import LayoutData
```

#### Fields

- `keyboard` (str): Keyboard identifier
- `keymap` (str): Keymap name
- `layout` (str): Layout variant
- `layer_names` (list[str]): Layer names
- `layers` (list[LayoutLayer]): Layer definitions
- `behaviors` (list[Any]): Behavior definitions
- `combos` (list[ComboBehavior]): Combo definitions
- `macros` (list[MacroBehavior]): Macro definitions
- `metadata` (dict[str, Any]): Additional metadata

---

### Class: `LayoutLayer`

Layer definition model.

```python
from zmk_layout.models.core import LayoutLayer
```

#### Fields

- `name` (str): Layer name
- `bindings` (list[LayoutBinding]): Key bindings
- `description` (Optional[str]): Layer description

---

### Class: `LayoutBinding`

Individual key binding model.

```python
from zmk_layout.models.core import LayoutBinding
```

#### Fields

- `behavior` (str): Behavior name (e.g., "kp", "mt")
- `params` (list[str]): Behavior parameters
- `raw` (str): Raw binding string

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
- `hold` (str): Hold binding
- `tap` (str): Tap binding
- `tapping_term_ms` (int): Tapping term
- `quick_tap_ms` (int): Quick tap time
- `flavor` (str): HT flavor
- `retro_tap` (bool): Enable retro tap
- `hold_trigger_key_positions` (Optional[list[int]]): Trigger positions

---

### Class: `ComboBehavior`

Combo behavior definition.

```python
from zmk_layout.models.behaviors import ComboBehavior
```

#### Fields

- `name` (str): Combo name
- `key_positions` (list[int]): Key positions
- `bindings` (list[str]): Combo bindings
- `timeout_ms` (int): Timeout
- `layers` (Optional[list[str]]): Active layers
- `require_prior_idle_ms` (Optional[int]): Idle requirement

---

### Class: `MacroBehavior`

Macro behavior definition.

```python
from zmk_layout.models.behaviors import MacroBehavior
```

#### Fields

- `name` (str): Macro name
- `bindings` (list[str]): Macro sequence
- `wait_ms` (int): Wait between keys
- `tap_ms` (int): Tap duration

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
    providers: Optional[LayoutProviders] = None
) -> ZMKKeymapParser
```

#### Methods

##### `parse_string()`
```python
def parse_string(self, content: str) -> LayoutData
```
Parse keymap string to LayoutData.

**Parameters:**
- `content`: Keymap content as string

**Returns:** LayoutData instance

**Raises:**
- `ParseError`: If parsing fails


---

### Class: `DTParser`

Devicetree parser using Lark grammar.

```python
from zmk_layout.parsers.dt_parser import DTParser
```

#### Methods

##### `parse()`
```python
def parse(self, content: str) -> dict[str, Any]
```
Parse devicetree content.

**Parameters:**
- `content`: Devicetree content

**Returns:** Parsed AST dictionary

---

## Generators Module (`zmk_layout.generators`)

### Class: `ZMKGenerator`

Generate ZMK configuration from layout data.

```python
from zmk_layout.generators import ZMKGenerator
```

#### Constructor

```python
ZMKGenerator(
    providers: Optional[LayoutProviders] = None
) -> ZMKGenerator
```

#### Methods

##### `generate_keymap()`
```python
def generate_keymap(
    self,
    layout_data: LayoutData,
    template: Optional[str] = None
) -> str
```
Generate keymap DTSI content.

**Parameters:**
- `layout_data`: Layout data
- `template`: Optional template string

**Returns:** Keymap DTSI content as string

##### `generate_behaviors()`
```python
def generate_behaviors(
    self,
    layout_data: LayoutData
) -> str
```
Generate behavior definitions.

**Parameters:**
- `layout_data`: Layout data

**Returns:** Behaviors DTSI content as string

##### `generate_config()`
```python
def generate_config(
    self,
    layout_data: LayoutData
) -> str
```
Generate Kconfig content.

**Parameters:**
- `layout_data`: Layout data

**Returns:** Kconfig content as string

---

## Providers Module (`zmk_layout.providers`)

### Protocol: `ConfigurationProvider`

Configuration provider protocol.

```python
from zmk_layout.providers import ConfigurationProvider
```

#### Required Methods

- `get_behavior_definitions() -> list[dict[str, Any]]`
- `get_include_files() -> list[str]`
- `get_validation_rules() -> dict[str, Any]`
- `get_template_context() -> dict[str, Any]`

### Protocol: `TemplateProvider`

Template rendering provider protocol.

```python
from zmk_layout.providers import TemplateProvider
```

#### Required Methods

- `render_string(template: str, context: dict[str, Any]) -> str`
- `has_template_syntax(content: str) -> bool`
- `validate_template(template: str) -> list[str]`

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

### Protocol: `FileProvider`

File operations provider protocol.

```python
from zmk_layout.providers import FileProvider
```

#### Required Methods

- `read_text(path: Path) -> str`
- `write_text(path: Path, content: str) -> None`
- `exists(path: Path) -> bool`

### Class: `LayoutProviders`

Container for all providers.

```python
from zmk_layout.providers import LayoutProviders
```

#### Fields

- `configuration`: ConfigurationProvider instance
- `template`: TemplateProvider instance
- `logger`: LayoutLogger instance
- `file`: FileProvider instance

---

## Builders Module (`zmk_layout.builders`)

### Class: `LayoutBindingBuilder`

Fluent builder for creating bindings.

```python
from zmk_layout.builders import LayoutBindingBuilder
```

#### Constructor

```python
LayoutBindingBuilder(behavior: str = "&kp") -> LayoutBindingBuilder
```

#### Methods

##### `key()`
```python
def key(self, keycode: str) -> LayoutBindingBuilder
```
Set key code.

##### `modifier()`
```python
def modifier(self, mod: str) -> LayoutBindingBuilder
```
Add modifier.

##### `layer()`
```python
def layer(self, layer: Union[str, int]) -> LayoutBindingBuilder
```
Set layer reference.

##### `build()`
```python
def build(self) -> str
```
Build binding string.

**Example:**
```python
binding = (LayoutBindingBuilder("&mt")
    .modifier("LCTRL")
    .key("A")
    .build())  # Returns: "&mt LCTRL A"
```

---

### Class: `ComboBuilder`

Fluent builder for creating combos.

```python
from zmk_layout.builders import ComboBuilder
```

#### Methods

##### `name()`
```python
def name(self, name: str) -> ComboBuilder
```
Set combo name.

##### `keys()`
```python
def keys(self, *positions: int) -> ComboBuilder
```
Set key positions.

##### `binding()`
```python
def binding(self, binding: str) -> ComboBuilder
```
Set combo binding.

##### `timeout()`
```python
def timeout(self, ms: int) -> ComboBuilder
```
Set timeout.

##### `layers()`
```python
def layers(self, *layers: str) -> ComboBuilder
```
Set active layers.

##### `build()`
```python
def build(self) -> ComboBehavior
```
Build combo behavior.

---

### Class: `MacroBuilder`

Fluent builder for creating macros.

```python
from zmk_layout.builders import MacroBuilder
```

#### Methods

##### `name()`
```python
def name(self, name: str) -> MacroBuilder
```
Set macro name.

##### `tap()`
```python
def tap(self, binding: str) -> MacroBuilder
```
Add tap action.

##### `press()`
```python
def press(self, binding: str) -> MacroBuilder
```
Add press action.

##### `release()`
```python
def release(self, binding: str) -> MacroBuilder
```
Add release action.

##### `wait()`
```python
def wait(self, ms: int) -> MacroBuilder
```
Add wait time.

##### `build()`
```python
def build(self) -> MacroBehavior
```
Build macro behavior.

---

## Processing Module (`zmk_layout.processing`)

### Class: `ProcessingPipeline`

Pipeline for processing layout data.

```python
from zmk_layout.processing import ProcessingPipeline
```

#### Constructor

```python
ProcessingPipeline(
    providers: Optional[LayoutProviders] = None
) -> ProcessingPipeline
```

#### Methods

##### `from_file()`
```python
def from_file(self, file_path: Union[str, Path]) -> ProcessingPipeline
```
Load layout from file.

##### `validate()`
```python
def validate(self) -> ProcessingPipeline
```
Add validation step.

##### `transform()`
```python
def transform(
    self,
    transformer: Callable[[LayoutData], LayoutData]
) -> ProcessingPipeline
```
Add transformation step.

##### `generate_keymap()`
```python
def generate_keymap(self) -> ProcessingPipeline
```
Add keymap generation step.

##### `execute()`
```python
def execute(self) -> Any
```
Execute the pipeline.

**Example:**
```python
result = (ProcessingPipeline()
    .from_file("layout.json")
    .validate()
    .transform(add_home_row_mods)
    .generate_keymap()
    .execute())
```

---

### Class: `TransformationPipeline`

Pipeline for layout transformations.

```python
from zmk_layout.processing import TransformationPipeline
```

#### Methods

##### `add_home_row_mods()`
```python
def add_home_row_mods(
    self,
    positions: list[int],
    mods: list[str]
) -> TransformationPipeline
```
Add home row mods.

##### `normalize_bindings()`
```python
def normalize_bindings(self) -> TransformationPipeline
```
Normalize all bindings.

##### `optimize_combos()`
```python
def optimize_combos(self) -> TransformationPipeline
```
Optimize combo definitions.

---

## Validation Module (`zmk_layout.validation`)

### Class: `ValidationPipeline`

Pipeline for layout validation.

```python
from zmk_layout.validation import ValidationPipeline
```

#### Constructor

```python
ValidationPipeline(
    layout_data: LayoutData,
    providers: Optional[LayoutProviders] = None
) -> ValidationPipeline
```

#### Methods

##### `validate_bindings()`
```python
def validate_bindings(self) -> ValidationPipeline
```
Validate all bindings.

##### `validate_behaviors()`
```python
def validate_behaviors(self) -> ValidationPipeline
```
Validate behavior definitions.

##### `validate_layer_references()`
```python
def validate_layer_references(self) -> ValidationPipeline
```
Validate layer references.

##### `validate_key_positions()`
```python
def validate_key_positions(self) -> ValidationPipeline
```
Validate key positions.

##### `with_custom_rules()`
```python
def with_custom_rules(
    self,
    rules: list[Callable[[LayoutData], list[str]]]
) -> ValidationPipeline
```
Add custom validation rules.

##### `execute()`
```python
def execute(self) -> ValidationResult
```
Execute validation.

**Returns:** ValidationResult with:
- `is_valid` (bool): Overall validity
- `errors` (list[str]): Error messages
- `warnings` (list[str]): Warning messages

---

## Infrastructure Module (`zmk_layout.infrastructure`)

### Class: `ProviderBuilder`

Fluent builder for provider configuration.

```python
from zmk_layout.infrastructure import ProviderBuilder
```

#### Methods


##### `with_template_adapter()`
```python
def with_template_adapter(self, adapter: TemplateProvider) -> ProviderBuilder
```
Set template adapter.

##### `with_logger()`
```python
def with_logger(self, logger: LayoutLogger) -> ProviderBuilder
```
Set logger.

##### `enable_caching()`
```python
def enable_caching(self, size: int = 256) -> ProviderBuilder
```
Enable caching with size.

##### `from_environment()`
```python
def from_environment(self) -> ProviderBuilder
```
Configure from environment variables.

##### `build()`
```python
def build(self) -> LayoutProviders
```
Build provider configuration.

---

### Class: `TemplateContextBuilder`

Fluent builder for template contexts.

```python
from zmk_layout.infrastructure import TemplateContextBuilder
```

#### Methods

##### `with_layout()`
```python
def with_layout(self, layout_data: LayoutData) -> TemplateContextBuilder
```
Set layout data.

##### `with_profile()`
```python
def with_profile(self, profile: dict[str, Any]) -> TemplateContextBuilder
```
Set keyboard profile.

##### `with_behaviors()`
```python
def with_behaviors(
    self,
    behaviors: list[Any],
    combos: list[Any] = None,
    macros: list[Any] = None
) -> TemplateContextBuilder
```
Set behaviors.

##### `with_metadata()`
```python
def with_metadata(self, **kwargs) -> TemplateContextBuilder
```
Add metadata.

##### `build()`
```python
def build(self) -> TemplateContext
```
Build template context.

---

### Class: `ChainInspector`

Debug tool for inspecting fluent chains.

```python
from zmk_layout.infrastructure import ChainInspector
```

#### Methods

##### `wrap()`
```python
def wrap(self, builder: Any) -> Any
```
Wrap builder for inspection.

##### `print_chain_history()`
```python
def print_chain_history(self) -> None
```
Print chain call history.

##### `export_history()`
```python
def export_history(self, file_path: str) -> None
```
Export history to file.

---

### Performance Utilities

#### Function: `memoize`
```python
from zmk_layout.infrastructure.performance import memoize

@memoize(maxsize=128)
def expensive_function(x: int) -> int:
    # Cached function
    return x ** 2
```

#### Class: `LRUCache`
```python
from zmk_layout.infrastructure.performance import LRUCache

cache = LRUCache(maxsize=256)
cache.put("key", "value")
result = cache.get("key")
```

---

## Utils Module (`zmk_layout.utils`)

### Function: `validate_binding`
```python
from zmk_layout.utils.validation import validate_binding

def validate_binding(binding: str) -> bool
```
Validate ZMK binding string.

**Parameters:**
- `binding`: Binding string to validate

**Returns:** True if valid

### Function: `normalize_binding`
```python
from zmk_layout.utils.validation import normalize_binding

def normalize_binding(binding: str) -> str
```
Normalize binding format.

**Parameters:**
- `binding`: Binding to normalize

**Returns:** Normalized binding

### Function: `find_layer_references`
```python
from zmk_layout.utils.layer_references import find_layer_references

def find_layer_references(
    layout_data: LayoutData
) -> dict[str, list[str]]
```
Find all layer references in layout.

**Parameters:**
- `layout_data`: Layout data

**Returns:** Dictionary mapping layers to references

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
    print(f"Validation failed: {e.errors}")
```

### `LayerNotFoundError`
Raised when layer doesn't exist.

```python
from zmk_layout.core.exceptions import LayerNotFoundError

try:
    layout.layers.get("nonexistent")
except LayerNotFoundError as e:
    print(f"Layer not found: {e.layer_name}")
    print(f"Available layers: {e.available_layers}")
```

### `InvalidBindingError`
Raised for invalid binding strings.

```python
from zmk_layout.core.exceptions import InvalidBindingError

try:
    LayoutBinding.from_str("invalid")
except InvalidBindingError as e:
    print(f"Invalid binding: {e.binding}")
    print(f"Suggestion: {e.suggestion}")
```

### `ParseError`
Raised when parsing fails.

```python
from zmk_layout.parsers.exceptions import ParseError

try:
    parser.parse_file("bad.keymap")
except ParseError as e:
    print(f"Parse error at line {e.line}: {e.message}")
```

---

## Type Definitions

### Type Aliases

```python
from zmk_layout.models.types import (
    LayerIndex,      # int (0-based layer index)
    KeyPosition,     # int (0-based key position)
    LayerBindings,   # list[str] (layer binding list)
    ConfigValue,     # Union[str, int, bool, list, dict]
    ParamValue,      # Union[str, int]
)
```

---

## Constants

### Behaviors

```python
from zmk_layout.constants import (
    DEFAULT_BEHAVIORS,     # List of default ZMK behaviors
    BEHAVIOR_PREFIXES,     # Valid behavior prefixes
    MODIFIER_KEYS,         # Valid modifier keys
    LAYER_COMMANDS,        # Layer control commands
)
```

### Validation

```python
from zmk_layout.constants import (
    MAX_LAYERS,           # Maximum layer count (default: 32)
    MAX_COMBOS,           # Maximum combo count (default: 64)
    MAX_MACROS,           # Maximum macro count (default: 32)
    MAX_KEY_POSITIONS,    # Maximum keys (default: 256)
)
```

---

## Environment Variables

The library respects these environment variables:

- `ZMK_LAYOUT_DEBUG`: Enable debug mode ("true")
- `ZMK_LAYOUT_CACHE_SIZE`: Cache size (integer)
- `ZMK_LAYOUT_LOG_LEVEL`: Log level ("DEBUG", "INFO", "WARNING", "ERROR")
- `ZMK_LAYOUT_TEMPLATE_ENGINE`: Template engine ("jinja2", "simple")
- `ZMK_LAYOUT_BASE_PATH`: Base path for file operations

---

## Complete Example

```python
from zmk_layout import Layout
from zmk_layout.providers import LayoutProviders
from zmk_layout.infrastructure import ProviderBuilder

# Configure providers (FileProvider no longer needed)
providers = (ProviderBuilder()
    .with_template_adapter(my_template_adapter)
    .enable_caching(size=512)
    .from_environment()
    .build())

# Create layout from dictionary
layout_data = {"keyboard": "crkbd", "layers": [], "layer_names": []}
layout = Layout.from_dict(layout_data, providers=providers)

# Or create from string (auto-detects JSON or keymap format)
json_string = '{"keyboard": "crkbd", "layers": [], "layer_names": []}'
layout = Layout.from_string(json_string, title="My Layout", providers=providers)

# Or create empty layout
layout = (Layout
    .create_empty("crkbd", "My Custom Layout", providers=providers)
    .layers
        .add("base")
        .set_range(0, 10, ["&kp Q", "&kp W", "&kp E", "&kp R", "&kp T",
                           "&kp Y", "&kp U", "&kp I", "&kp O", "&kp P"])
        .parent()
    .layers
        .add("nav")
        .copy_from("base")
        .set(0, "&kp UP")
        .set(1, "&kp DOWN")
        .parent()
    .behaviors
        .add_hold_tap("hm", hold="&kp", tap="&kp", tapping_term_ms=200)
        .add_combo("copy", keys=[0, 1], binding="&kp LC(C)")
        .add_macro("hello", bindings=["&kp H", "&kp E", "&kp L", "&kp L", "&kp O"])
        .parent()
    .validate())

# Export to dictionary
layout_data = layout.to_dict()

# Export to ZMK keymap string
keymap_string = layout.to_keymap(keyboard_name="crkbd", include_headers=True)

# Get statistics
stats = layout.get_statistics()
print(f"Created layout with {stats['layer_count']} layers")

# File I/O is handled by the consuming application
import json
from pathlib import Path

# To save:
Path("layout.json").write_text(json.dumps(layout_data))
Path("keymap.dtsi").write_text(keymap_string)

# To load:
layout_data = json.loads(Path("layout.json").read_text())
layout = Layout.from_dict(layout_data)
```

---

## Version History

- **0.1.0** (2024-01): Initial release with fluent API
- **0.1.1** (Planned): Performance improvements
- **0.2.0** (Planned): QMK import support

---

## Support

- GitHub Issues: [zmk-layout/issues](https://github.com/CaddyGlow/zmk-layout/issues)
- Discussions: [zmk-layout/discussions](https://github.com/CaddyGlow/zmk-layout/discussions)
- Documentation: [zmk-layout.readthedocs.io](https://zmk-layout.readthedocs.io)