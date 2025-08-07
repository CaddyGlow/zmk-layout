# Data Models API Reference

## Overview

The zmk-layout library uses Pydantic v2 models for data validation and serialization. All models inherit from `LayoutBaseModel` which provides consistent JSON serialization and validation.

## Model Hierarchy

```
LayoutBaseModel (base class)
├── LayoutMetadata        # Base metadata fields
│   └── LayoutData        # Complete layout model (extends LayoutMetadata)
├── LayoutLayer          # Layer definition
├── LayoutBinding        # Individual key binding
├── LayoutParam          # Parameter for behaviors (supports nesting)
├── HoldTapBehavior      # Hold-tap behavior
├── ComboBehavior        # Combo behavior
├── MacroBehavior        # Macro behavior
├── TapDanceBehavior     # Tap-dance behavior
├── StickyKeyBehavior    # Sticky-key behavior
├── CapsWordBehavior     # Caps-word behavior
├── ModMorphBehavior     # Mod-morph behavior
└── LayoutResult         # Operation results
```

## Import

```python
from zmk_layout.models import (
    LayoutData,
    LayoutLayer,
    LayoutBinding,
    LayoutParam,
    HoldTap,
    Combo,
    Macro,
    ValidationResult
)
```

---

## LayoutBaseModel

Base class for all models in the library.

### Class: `LayoutBaseModel`

```python
from pydantic import BaseModel, ConfigDict

class LayoutBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        json_encoders={
            Path: str
        }
    )
```

Provides:
- JSON serialization with aliases
- Type validation
- Custom encoders for complex types

---

## LayoutMetadata

Base metadata fields for layout configurations.

### Class: `LayoutMetadata`

```python
class LayoutMetadata(LayoutBaseModel):
    # Required fields
    keyboard: str
    title: str
    
    # Optional metadata
    firmware_api_version: str = Field(default="1", alias="firmware_api_version")
    locale: str = Field(default="en-US")
    uuid: str = Field(default="")
    parent_uuid: str = Field(default="", alias="parent_uuid")
    date: datetime = Field(default_factory=datetime.now)
    creator: str = Field(default="")
    notes: str = Field(default="")
    tags: list[str] = Field(default_factory=list)
    
    # Variables for substitution
    variables: dict[str, Any] = Field(default_factory=dict)
    
    # Configuration
    config_parameters: list[ConfigParameter] = Field(default_factory=list, alias="config_parameters")
    layer_names: list[str] = Field(default_factory=list, alias="layer_names")
    
    # Version tracking
    version: str = Field(default="1.0.0")
    base_version: str = Field(default="")
    base_layout: str = Field(default="")
```

**Fields:**
- `keyboard` (str): Keyboard identifier (required)
- `title` (str): Layout title (required)
- `firmware_api_version` (str): API version
- `locale` (str): Locale setting
- `uuid` (str): Unique identifier
- `parent_uuid` (str): Parent layout UUID
- `date` (datetime): Creation/modification date
- `creator` (str): Layout creator
- `notes` (str): Additional notes
- `tags` (list[str]): Tags for categorization
- `variables` (dict): Global template variables
- `config_parameters` (list[ConfigParameter]): Configuration parameters
- `layer_names` (list[str]): Layer names
- `version` (str): Layout version
- `base_version` (str): Base version reference
- `base_layout` (str): Base layout reference

---

## LayoutData

Top-level model representing a complete keyboard layout.

### Class: `LayoutData`

```python
class LayoutData(LayoutBaseModel):
    keyboard: str
    name: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    layers: list[LayoutLayer] = []
    combos: list[Combo] = []
    macros: list[Macro] = []
    hold_taps: list[HoldTap] = []
    behaviors: dict[str, Any] = {}
    metadata: dict[str, Any] = {}
```

**Fields:**
- `keyboard` (str): Keyboard identifier (e.g., "crkbd", "glove80")
- `name` (str): Layout name
- `description` (Optional[str]): Layout description
- `author` (Optional[str]): Layout author
- `version` (Optional[str]): Layout version
- `layers` (list[LayoutLayer]): List of layers
- `combos` (list[Combo]): Combo definitions
- `macros` (list[Macro]): Macro definitions
- `hold_taps` (list[HoldTap]): Hold-tap behavior definitions
- `behaviors` (dict): Additional behavior configurations
- `metadata` (dict): Additional metadata

**Example:**
```python
data = LayoutData(
    keyboard="crkbd",
    name="My Corne Layout",
    description="Optimized for programming",
    author="John Doe",
    version="1.0.0",
    layers=[
        LayoutLayer(name="default", bindings=[...])
    ]
)
```

### Methods

#### `add_layer`

```python
def add_layer(self, layer: LayoutLayer) -> None
```

Adds a layer to the layout.

#### `remove_layer`

```python
def remove_layer(self, name: str) -> None
```

Removes a layer by name.

#### `get_layer`

```python
def get_layer(self, name: str) -> Optional[LayoutLayer]
```

Gets a layer by name.

#### `validate_consistency`

```python
def validate_consistency(self) -> ValidationResult
```

Validates internal consistency of the layout data.

---

## LayoutLayer

Represents a single layer in the keyboard layout.

### Class: `LayoutLayer`

```python
class LayoutLayer(LayoutBaseModel):
    name: str
    bindings: list[LayoutBinding]
    description: Optional[str] = None
    enabled: bool = True
    metadata: dict[str, Any] = {}
```

**Fields:**
- `name` (str): Layer name (must be unique within layout)
- `bindings` (list[LayoutBinding]): List of key bindings
- `description` (Optional[str]): Layer description
- `enabled` (bool): Whether layer is enabled
- `metadata` (dict): Additional metadata

**Example:**
```python
layer = LayoutLayer(
    name="navigation",
    description="Navigation and arrow keys",
    bindings=[
        LayoutBinding.from_str("&kp UP"),
        LayoutBinding.from_str("&kp DOWN"),
        LayoutBinding.from_str("&kp LEFT"),
        LayoutBinding.from_str("&kp RIGHT")
    ]
)
```

### Methods

#### `set_binding`

```python
def set_binding(
    self,
    position: int,
    binding: Union[str, LayoutBinding]
) -> None
```

Sets a binding at a specific position.

#### `get_binding`

```python
def get_binding(self, position: int) -> Optional[LayoutBinding]
```

Gets a binding at a specific position.

#### `clear`

```python
def clear(self) -> None
```

Clears all bindings.

#### `pad_to`

```python
def pad_to(self, size: int, padding: str = "&trans") -> None
```

Pads the layer to a specific size.

---

## LayoutBinding

Represents a single key binding.

### Class: `LayoutBinding`

```python
class LayoutBinding(LayoutBaseModel):
    type: str
    value: Optional[str] = None
    params: list[LayoutParam] = []
    metadata: dict[str, Any] = {}
```

**Fields:**
- `type` (str): Binding type (e.g., "kp", "mo", "lt", "mt", "trans", "none")
- `value` (Optional[str]): Binding value (e.g., "A", "SPACE", "LSHIFT")
- `params` (list[LayoutParam]): Additional parameters
- `metadata` (dict): Additional metadata

**Example:**
```python
# Simple key press
binding = LayoutBinding(type="kp", value="A")

# Momentary layer
binding = LayoutBinding(type="mo", value="1")

# Hold-tap with parameters
binding = LayoutBinding(
    type="mt",
    params=[
        LayoutParam(name="hold", value="LSHIFT"),
        LayoutParam(name="tap", value="A")
    ]
)
```

### Class Methods

#### `from_str`

```python
@classmethod
def from_str(cls, binding_str: str) -> LayoutBinding
```

Parses a binding from ZMK syntax string.

**Parameters:**
- `binding_str` (str): ZMK binding string (e.g., "&kp A", "&mt LSHIFT A")

**Returns:** LayoutBinding instance

**Example:**
```python
# Simple bindings
binding = LayoutBinding.from_str("&kp A")
binding = LayoutBinding.from_str("&mo 1")
binding = LayoutBinding.from_str("&trans")

# Complex bindings
binding = LayoutBinding.from_str("&mt LSHIFT A")
binding = LayoutBinding.from_str("&lt 1 SPACE")
```

### Methods

#### `to_zmk`

```python
def to_zmk(self) -> str
```

Converts the binding to ZMK syntax string.

**Returns:** ZMK binding string

**Example:**
```python
binding = LayoutBinding(type="kp", value="A")
zmk_str = binding.to_zmk()  # Returns "&kp A"
```

#### `is_transparent`

```python
def is_transparent(self) -> bool
```

Checks if binding is transparent.

#### `is_none`

```python
def is_none(self) -> bool
```

Checks if binding is none/empty.

---

## LayoutParam

Represents a parameter for behaviors.

### Class: `LayoutParam`

```python
class LayoutParam(LayoutBaseModel):
    name: str
    value: Union[str, int, bool]
    metadata: dict[str, Any] = {}
```

**Fields:**
- `name` (str): Parameter name
- `value` (Union[str, int, bool]): Parameter value
- `metadata` (dict): Additional metadata

**Example:**
```python
param = LayoutParam(name="tapping_term_ms", value=200)
param = LayoutParam(name="flavor", value="tap-preferred")
```

---

## HoldTap

Represents a hold-tap behavior configuration.

### Class: `HoldTap`

```python
class HoldTap(LayoutBaseModel):
    name: str
    tap: str
    hold: str
    tapping_term_ms: int = 200
    flavor: str = "tap-preferred"
    quick_tap_ms: Optional[int] = None
    require_prior_idle_ms: Optional[int] = None
    metadata: dict[str, Any] = {}
```

**Fields:**
- `name` (str): Behavior name
- `tap` (str): Action on tap
- `hold` (str): Action on hold
- `tapping_term_ms` (int): Tapping term in milliseconds
- `flavor` (str): Behavior flavor ("tap-preferred", "hold-preferred", "balanced")
- `quick_tap_ms` (Optional[int]): Quick tap window
- `require_prior_idle_ms` (Optional[int]): Required idle time before activation
- `metadata` (dict): Additional metadata

**Example:**
```python
hold_tap = HoldTap(
    name="hm_shift",
    tap="&kp A",
    hold="&kp LSHIFT",
    tapping_term_ms=200,
    flavor="tap-preferred",
    quick_tap_ms=150
)
```

### Methods

#### `to_zmk_definition`

```python
def to_zmk_definition(self) -> str
```

Generates ZMK devicetree definition.

**Returns:** ZMK devicetree syntax string

---

## Combo

Represents a combo behavior configuration.

### Class: `Combo`

```python
class Combo(LayoutBaseModel):
    name: str
    keys: list[int]
    binding: str
    timeout_ms: int = 50
    layers: Optional[list[str]] = None
    require_prior_idle_ms: Optional[int] = None
    metadata: dict[str, Any] = {}
```

**Fields:**
- `name` (str): Combo name
- `keys` (list[int]): Key positions that trigger the combo
- `binding` (str): Action when combo is triggered
- `timeout_ms` (int): Timeout in milliseconds
- `layers` (Optional[list[str]]): Layers where combo is active (None = all layers)
- `require_prior_idle_ms` (Optional[int]): Required idle time
- `metadata` (dict): Additional metadata

**Example:**
```python
combo = Combo(
    name="copy_combo",
    keys=[10, 11],  # Positions for C and V
    binding="&kp LC(C)",
    timeout_ms=30,
    layers=["default", "nav"]
)
```

### Methods

#### `to_zmk_definition`

```python
def to_zmk_definition(self) -> str
```

Generates ZMK devicetree definition.

---

## Macro

Represents a macro behavior configuration.

### Class: `Macro`

```python
class Macro(LayoutBaseModel):
    name: str
    bindings: list[str]
    wait_ms: int = 0
    tap_ms: int = 0
    metadata: dict[str, Any] = {}
```

**Fields:**
- `name` (str): Macro name
- `bindings` (list[str]): Sequence of bindings to execute
- `wait_ms` (int): Wait time between bindings
- `tap_ms` (int): Tap duration
- `metadata` (dict): Additional metadata

**Example:**
```python
macro = Macro(
    name="email_macro",
    bindings=[
        "&kp M", "&kp Y", "&kp AT",
        "&kp E", "&kp M", "&kp A",
        "&kp I", "&kp L"
    ],
    wait_ms=30,
    tap_ms=30
)
```

### Methods

#### `to_zmk_definition`

```python
def to_zmk_definition(self) -> str
```

Generates ZMK devicetree definition.

---

## ValidationResult

Represents the result of layout validation.

### Class: `ValidationResult`

```python
class ValidationResult(LayoutBaseModel):
    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    metadata: dict[str, Any] = {}
```

**Fields:**
- `is_valid` (bool): Whether validation passed
- `errors` (list[str]): List of error messages
- `warnings` (list[str]): List of warning messages
- `info` (list[str]): List of informational messages
- `metadata` (dict): Additional validation metadata

**Example:**
```python
result = ValidationResult(
    is_valid=False,
    errors=["Layer 'default' not found"],
    warnings=["Combo 'test' has very short timeout"],
    info=["Validated 5 layers, 20 combos"]
)

if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")
```

### Methods

#### `add_error`

```python
def add_error(self, message: str) -> None
```

Adds an error message and sets is_valid to False.

#### `add_warning`

```python
def add_warning(self, message: str) -> None
```

Adds a warning message.

#### `add_info`

```python
def add_info(self, message: str) -> None
```

Adds an informational message.

#### `merge`

```python
def merge(self, other: ValidationResult) -> None
```

Merges another validation result into this one.

---

## Model Serialization

All models support JSON serialization with proper aliases:

```python
# Serialize to JSON
data = layout_data.model_dump_json(indent=2, exclude_none=True)

# Serialize to dict
data_dict = layout_data.model_dump(exclude_none=True)

# Load from JSON
layout_data = LayoutData.model_validate_json(json_string)

# Load from dict
layout_data = LayoutData.model_validate(data_dict)
```

## Model Validation

Pydantic provides automatic validation:

```python
from pydantic import ValidationError

try:
    layer = LayoutLayer(
        name="",  # Invalid: empty name
        bindings=[]
    )
except ValidationError as e:
    print(e.errors())
```

## Custom Validators

Models include custom validators for business logic:

```python
from pydantic import field_validator

class LayoutLayer(LayoutBaseModel):
    name: str
    
    @field_validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Layer name cannot be empty")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Layer name must be alphanumeric")
        return v
```

## Type Conversion

Models handle automatic type conversion:

```python
# String to LayoutBinding
layer = LayoutLayer(
    name="test",
    bindings=["&kp A", "&kp B"]  # Automatically converted to LayoutBinding
)

# Dict to model
data = {
    "keyboard": "crkbd",
    "name": "Test",
    "layers": [
        {"name": "default", "bindings": ["&kp A"]}
    ]
}
layout_data = LayoutData(**data)
```

---

## Additional Behavior Models

The library includes several additional behavior models that follow similar patterns:

### TapDanceBehavior
```python
class TapDanceBehavior(LayoutBaseModel):
    name: str
    description: str | None = ""
    tapping_term_ms: TemplateNumeric = Field(default=None, alias="tappingTermMs")
    bindings: list["LayoutBinding"] = Field(default_factory=list)  # 2-5 bindings
```

### StickyKeyBehavior
```python
class StickyKeyBehavior(LayoutBaseModel):
    name: str
    description: str | None = ""
    release_after_ms: TemplateNumeric = Field(default=None, alias="releaseAfterMs")
    quick_release: bool = Field(default=False, alias="quickRelease")
    lazy: bool = Field(default=False)
    ignore_modifiers: bool = Field(default=False, alias="ignoreModifiers")
    bindings: list["LayoutBinding"] = Field(default_factory=list)
```

### CapsWordBehavior
```python
class CapsWordBehavior(LayoutBaseModel):
    name: str
    description: str | None = ""
    continue_list: list[str] = Field(default_factory=list, alias="continueList")
    mods: int | None = Field(default=None)
```

### ModMorphBehavior
```python
class ModMorphBehavior(LayoutBaseModel):
    name: str
    description: str | None = ""
    mods: int
    bindings: list["LayoutBinding"] = Field(default_factory=list)  # Exactly 2 bindings
    keep_mods: int | None = Field(default=None, alias="keepMods")
```

### InputListener
```python
class InputListener(LayoutBaseModel):
    code: str
    input_processors: list[InputProcessor] = Field(default_factory=list, alias="inputProcessors")
    nodes: list[InputListenerNode] = Field(default_factory=list)
```

All behavior models include:
- Field validation with appropriate constraints
- Alias support for both camelCase and snake_case
- Template-aware numeric types for configuration values
- Automatic model rebuilding for forward references

## Best Practices

1. **Use class methods for parsing**: `LayoutBinding.from_str()` for ZMK strings
2. **Validate before export**: Always validate models before generating output
3. **Use type hints**: Helps with IDE support and validation
4. **Handle optional fields**: Use `Optional[]` for nullable fields
5. **Leverage Pydantic features**: Field validators, custom serializers, etc.
6. **Keep models immutable**: Use frozen=True for immutable models when appropriate
7. **Document field constraints**: Use Field() with description and constraints
8. **Use model_dump carefully**: Exclude None values when serializing
9. **Catch ValidationError**: Handle validation errors gracefully
10. **Test model validation**: Ensure validators work as expected