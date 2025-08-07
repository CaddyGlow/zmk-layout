# Generators API Reference

## Overview

The generator system provides fluent APIs for exporting layouts to various formats, primarily ZMK keymap files. The system uses an ExportManager with specialized builders for different output formats.

## Generator Architecture

```
ExportManager (fluent entry point)
├── KeymapBuilder        # ZMK keymap generation with fluent API
├── ConfigBuilder        # ZMK config generation with fluent API
├── to_dict()           # Dictionary export
└── to_json()           # JSON export

ZMKGenerator (core implementation)
├── BehaviorFormatter    # Format behavior bindings
├── BehaviorRegistry     # Track and validate behaviors
└── LayoutFormatter      # Format keyboard layout grids
```

## Import

```python
from zmk_layout.generators import (
    ExportManager,
    KeymapBuilder,
    ConfigBuilder,
    ZMKGenerator,
    BehaviorFormatter,
    BehaviorRegistry,
    LayoutFormatter,
)
```

---

## ExportManager

The main entry point for all export operations with a fluent interface.

### Usage via Layout.export

```python
layout = Layout.from_file("keymap.json")

# Export keymap with fluent API
keymap_content = layout.export.keymap().with_headers(True).generate()

# Export config
config_content, settings = layout.export.config().with_options(COMBO_MAX=20).generate()

# Export as dictionary
layout_dict = layout.export.to_dict()

# Export as JSON
json_content = layout.export.to_json(indent=4)
```

### Class: `ExportManager`

```python
class ExportManager:
    def __init__(self, layout: Layout) -> None
```

**Methods:**

#### `keymap`

```python
def keymap(self, profile: Any | None = None) -> KeymapBuilder
```

Start keymap export chain with fluent interface.

**Parameters:**
- `profile` (Any | None): Optional keyboard profile for configuration

**Returns:** KeymapBuilder for method chaining

#### `config`

```python
def config(self, profile: Any | None = None) -> ConfigBuilder
```

Start config export chain with fluent interface.

**Parameters:**
- `profile` (Any | None): Optional keyboard profile for configuration

**Returns:** ConfigBuilder for method chaining

#### `to_dict`

```python
def to_dict(self) -> dict[str, Any]
```

Export layout as dictionary.

#### `to_json`

```python
def to_json(self, indent: int = 2) -> str
```

Export layout as JSON string.

---

## KeymapBuilder

Fluent builder for ZMK keymap generation with chainable methods.

### Class: `KeymapBuilder`

```python
class KeymapBuilder:
    def __init__(self, layout: Layout, profile: Any | None = None) -> None
```

### Fluent Methods

All methods return `KeymapBuilder` for chaining except `generate()`.

#### `with_headers`

```python
def with_headers(self, include: bool = True) -> KeymapBuilder
```

Include/exclude standard ZMK headers and copyright.

#### `with_behaviors`

```python
def with_behaviors(self, include: bool = True) -> KeymapBuilder
```

Include/exclude behavior definitions (hold-taps, etc.).

#### `with_combos`

```python
def with_combos(self, include: bool = True) -> KeymapBuilder
```

Include/exclude combo definitions.

#### `with_macros`

```python
def with_macros(self, include: bool = True) -> KeymapBuilder
```

Include/exclude macro definitions.

#### `with_tap_dances`

```python
def with_tap_dances(self, include: bool = True) -> KeymapBuilder
```

Include/exclude tap dance definitions.

#### `with_template`

```python
def with_template(self, template_path: str) -> KeymapBuilder
```

Use custom Jinja2 template file.

#### `with_context`

```python
def with_context(self, **kwargs: Any) -> KeymapBuilder
```

Add custom template context variables.

#### `generate`

```python
def generate(self) -> str
```

Generate final keymap content as string.

### Examples

#### Basic Usage

```python
layout = Layout.from_file("my_layout.json")

# Generate complete keymap
keymap = layout.export.keymap().generate()
```

#### Custom Configuration

```python
# Generate keymap without headers and combos
keymap = (layout.export.keymap()
    .with_headers(False)
    .with_combos(False)
    .generate())
```

#### Template Usage

```python
# Use custom template with context
keymap = (layout.export.keymap()
    .with_template("custom_template.j2")
    .with_context(author="John Doe", version="2.1")
    .generate())
```

---

## ConfigBuilder

Fluent builder for ZMK configuration file generation.

### Class: `ConfigBuilder`

```python
class ConfigBuilder:
    def __init__(self, layout: Layout, profile: Any | None = None) -> None
```

### Fluent Methods

#### `with_options`

```python
def with_options(self, **options: Any) -> ConfigBuilder
```

Add kconfig options.

#### `with_defaults`

```python
def with_defaults(self, use: bool = True) -> ConfigBuilder
```

Include/exclude default configuration options.

#### `generate`

```python
def generate(self) -> tuple[str, dict[str, Any]]
```

Generate config content and return tuple of (config_content, kconfig_settings).

### Examples

```python
# Generate config with custom options
config_content, settings = (layout.export.config()
    .with_options(ZMK_COMBO_MAX_PRESSED_COMBOS=20)
    .generate())
```

---

## ZMKGenerator

Core implementation class for ZMK file content generation.

### Class: `ZMKGenerator`

```python
class ZMKGenerator:
    def __init__(
        self,
        configuration_provider: ConfigurationProvider | None = None,
        template_provider: TemplateProvider | None = None,
        logger: LayoutLogger | None = None,
    ) -> None
```

**Parameters:**
- `configuration_provider`: Provider for configuration data  
- `template_provider`: Provider for template processing
- `logger`: Logger for structured logging

### Core Generation Methods

#### `generate_layer_defines`

```python
def generate_layer_defines(
    self, 
    profile: KeyboardProfile, 
    layer_names: list[str]
) -> str
```

Generate #define statements for layers.

**Example Output:**
```c
#define DEFAULT 0
#define NAV     1
#define SYM     2
```

#### `generate_behaviors_dtsi`

```python
def generate_behaviors_dtsi(
    self, 
    profile: KeyboardProfile, 
    hold_taps_data: Sequence[HoldTapBehavior]
) -> str
```

Generate ZMK behaviors node string from hold-tap behavior models.

**Example Output:**
```c
behaviors {
    hm: homerow_mods {
        compatible = "zmk,behavior-hold-tap";
        label = "HOMEROW_MODS";
        #binding-cells = <2>;
        tapping-term-ms = <200>;
        quick-tap-ms = <150>;
        flavor = "tap-preferred";
        bindings = <&kp>, <&kp>;
    };
};
```

#### `generate_combos_dtsi`

```python
def generate_combos_dtsi(
    self,
    profile: KeyboardProfile,
    combos_data: Sequence[ComboBehavior],
    layer_names: list[str]
) -> str
```

Generate ZMK combos node string from combo behavior models.

**Example Output:**
```c
combos {
    compatible = "zmk,combos";
    
    combo_esc {
        timeout-ms = <30>;
        key-positions = <0 1>;
        bindings = <&kp ESC>;
        layers = <0 1>;
    };
};
```

#### `generate_macros_dtsi`

```python
def generate_macros_dtsi(
    self, 
    profile: KeyboardProfile, 
    macros_data: Sequence[MacroBehavior]
) -> str
```

Generate ZMK macros node string from macro behavior models.

**Example Output:**
```c
email: email {
    label = "EMAIL";
    compatible = "zmk,behavior-macro";
    #binding-cells = <0>;
    tap-ms = <30>;
    wait-ms = <30>;
    bindings = <&kp M>, <&kp Y>, <&kp AT>;
};
```

#### `generate_keymap_node`

```python
def generate_keymap_node(
    self,
    profile: KeyboardProfile,
    layer_names: list[str],
    layers_data: list[LayerBindings],
) -> str
```

Generate ZMK keymap node string from layer data.

**Example Output:**
```c
keymap {
    compatible = "zmk,keymap";
    
    layer_default {
        bindings = <
            &kp Q     &kp W     &kp E     &kp R     &kp T
            &kp A     &kp S     &kp D     &kp F     &kp G
            &kp Z     &kp X     &kp C     &kp V     &kp B
                      &mo 1     &kp SPACE &kp ENTER
        >;
    };
    
    layer_nav {
        bindings = <
            &kp ESC   &trans    &trans    &trans    &trans
            &kp LEFT  &kp DOWN  &kp UP    &kp RIGHT &trans
            &trans    &trans    &trans    &trans    &trans
                      &trans    &trans    &trans
        >;
    };
};
```

#### `generate_kconfig_conf`

```python
def generate_kconfig_conf(
    self,
    keymap_data: LayoutData,
    profile: KeyboardProfile,
) -> tuple[str, dict[str, int]]
```

Generate kconfig content and settings from keymap data.

**Returns:** Tuple of (kconfig_content, kconfig_settings)

---

## BehaviorFormatter

Formatter for ZMK behavior bindings with proper syntax handling.

### Class: `BehaviorFormatter`

```python
class BehaviorFormatter:
    def __init__(self) -> None
```

### Methods

#### `format_binding`

```python
def format_binding(self, binding: Any) -> str
```

Format a binding into proper ZMK syntax.

**Returns:** Formatted ZMK binding string like `&kp A`, `&mt LCTRL SPACE`

#### `set_behavior_reference_context`

```python
def set_behavior_reference_context(self, enabled: bool) -> None
```

Set whether formatting behavior references (for hold-tap bindings).

---

## BehaviorRegistry

Registry for tracking and validating behaviors.

### Class: `BehaviorRegistry`

```python
class BehaviorRegistry:
    def __init__(self) -> None
```

### Methods

#### `register_behavior`

```python
def register_behavior(self, behavior: Any) -> None
```

Register a behavior for tracking and validation.

#### `get_behavior`

```python
def get_behavior(self, code: str) -> Any | None
```

Get a registered behavior by code.

#### `is_registered`

```python
def is_registered(self, code: str) -> bool
```

Check if a behavior is registered.

---

## LayoutFormatter

Formatter for keyboard layout grids with profile-specific formatting.

### Class: `LayoutFormatter`

```python
class LayoutFormatter:
    def __init__(self) -> None
```

### Methods

#### `generate_layer_layout`

```python
def generate_layer_layout(
    self,
    layer_data: Any,
    profile: Any = None,
    base_indent: str = "            ",
    **kwargs: Any,
) -> str
```

Generate formatted layout grid for a layer's bindings.

**Parameters:**
- `layer_data`: Layer bindings or layer object with bindings
- `profile`: Optional keyboard profile for layout-specific formatting
- `base_indent`: Base indentation for grid lines

**Returns:** Formatted grid string with proper indentation and spacing

---

## Template Support

The system supports Jinja2 templates for custom keymap generation.

### Using Templates with KeymapBuilder

```python
# Use custom template
keymap = (layout.export.keymap()
    .with_template("custom_keymap.j2")
    .with_context(author="John Doe", build_date="2024-01-01")
    .generate())
```

### Template Context Variables

Available in templates:
- `keyboard`: Keyboard name
- `layer_names`: List of layer names
- `layers`: Processed layer data
- `keymap_node`: Generated keymap DTSI
- `user_behaviors_dtsi`: Hold-tap behaviors DTSI
- `combos_dtsi`: Combo definitions DTSI
- `user_macros_dtsi`: Macro definitions DTSI
- `resolved_includes`: Header includes
- Custom variables from `with_context()`

---

## Factory Functions

### `create_zmk_generator`

```python
def create_zmk_generator(
    configuration_provider: ConfigurationProvider | None = None,
    template_provider: TemplateProvider | None = None,
    logger: LayoutLogger | None = None,
) -> ZMKGenerator
```

Create a new ZMKGenerator instance with provider dependencies.

---

## Error Handling

The generators use structured error handling through the provider system.

**Common error scenarios:**
- Invalid layer names (must be valid C identifiers)
- Missing keyboard configuration
- Template rendering failures
- Invalid behavior definitions

---

## Integration with Layout Class

The generators integrate seamlessly with the Layout class through the ExportManager:

```python
layout = Layout.from_file("my_layout.json")

# Simple keymap export
keymap = layout.export.keymap().generate()

# Advanced configuration
keymap = (layout.export.keymap()
    .with_headers(True)
    .with_behaviors(True)
    .with_combos(False)
    .with_template("custom.j2")
    .generate())

# Config export
config, settings = layout.export.config().generate()
```

This fluent API provides a clean, chainable interface for all generation operations while maintaining the flexibility of the underlying ZMKGenerator implementation.