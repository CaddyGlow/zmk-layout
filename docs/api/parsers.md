# Parsers API Reference

## Overview

The parsing system handles complex ZMK keymap files, including devicetree syntax, C preprocessor directives, templates, and comments. The parser architecture is modular and extensible.

## Parser Architecture

```
ZMKKeymapParser (main coordinator)
├── DTParser (recursive descent parser for devicetree)
├── DTWalker/DTMultiWalker (AST traversal)
├── BehaviorExtractors (extract specific behavior types)
│   ├── BehaviorExtractor
│   ├── MacroExtractor
│   ├── HoldTapExtractor
│   ├── ComboExtractor
│   └── UniversalBehaviorExtractor
└── KeymapProcessors (transform raw data to models)
    ├── BaseKeymapProcessor
    ├── FullKeymapProcessor
    └── TemplateAwareProcessor
```

## Import

```python
from zmk_layout.parsers import (
    ZMKKeymapParser,
    DTParser,
    DTParseError,
    DTComment,
    DTConditional,
    DTNode,
    DTProperty,
    DTValue,
    DTValueType,
)
```

---

## ZMKKeymapParser

Main parser that coordinates the parsing process.

### Class: `ZMKKeymapParser`

```python
class ZMKKeymapParser:
    def __init__(
        self,
        configuration_provider: Optional[ConfigurationProvider] = None,
        logger: Optional[LayoutLogger] = None,
        processors: Optional[dict[ParsingMode, ProcessorProtocol]] = None,
    )
```

**Parameters:**
- `configuration_provider` (Optional[ConfigurationProvider]): Configuration provider for profiles
- `logger` (Optional[LayoutLogger]): Logger for structured logging
- `processors` (Optional[dict[ParsingMode, ProcessorProtocol]]): Dictionary of parsing mode to processor instances

### Methods

#### `parse_keymap`

```python
def parse_keymap(
    self,
    keymap_content: str,
    mode: ParsingMode = ParsingMode.TEMPLATE_AWARE,
    profile: Optional[KeyboardProfile] = None,
    method: ParsingMethod = ParsingMethod.AST,
    title: str = "unknown",
) -> KeymapParseResult
```

Parses ZMK keymap content to JSON layout.

**Parameters:**
- `keymap_content` (str): String content of the keymap
- `mode` (ParsingMode): Parsing mode (full or template-aware)
- `profile` (Optional[KeyboardProfile]): Keyboard profile (optional)
- `method` (ParsingMethod): Parsing method (always AST now)
- `title` (str): Title for the layout (optional)

**Returns:** `KeymapParseResult` with layout data or errors

**Example:**
```python
parser = ZMKKeymapParser()
result = parser.parse_keymap(keymap_content, ParsingMode.FULL)
if result.success:
    layout_data = result.layout_data
```

### Enums

#### `ParsingMode`

```python
class ParsingMode(str, Enum):
    FULL = "full"
    TEMPLATE_AWARE = "template"
```

Keymap parsing modes:
- `FULL`: Parse complete standalone keymap files
- `TEMPLATE_AWARE`: Use keyboard profile templates to extract only user data

#### `ParsingMethod`

```python
class ParsingMethod(str, Enum):
    AST = "ast"  # AST-based parsing
    REGEX = "regex"  # Legacy regex-based parsing
```

#### `KeymapParseResult`

```python
class KeymapParseResult(LayoutBaseModel):
    success: bool
    layout_data: LayoutData | None = None
    errors: list[str] = []
    warnings: list[str] = []
    parsing_mode: ParsingMode
    parsing_method: ParsingMethod = ParsingMethod.AST
    extracted_sections: dict[str, object] = {}
```

Result of keymap parsing operation with detailed status information.

---

## DTParser

Parses devicetree syntax using Lark grammar.

### Class: `DTParser`

```python
class DTParser:
    def __init__(
        self,
        tokens: list[Token],
        logger: Optional[LayoutLogger] = None
    )
```

**Parameters:**
- `tokens` (list[Token]): List of tokens from tokenizer
- `logger` (Optional[LayoutLogger]): Logger for structured logging

### Methods

#### `parse`

```python
def parse(self) -> DTNode
```

Parses tokens into device tree AST.

**Returns:** Root device tree node

**Raises:** `DTParseError` if parsing fails

#### `parse_multiple`

```python
def parse_multiple(self) -> list[DTNode]
```

Parses tokens into multiple device tree ASTs.

**Returns:** List of root device tree nodes

**Raises:** `DTParseError` if parsing fails

### Tokenization

The parser uses a tokenizer-based approach with these token types:

```python
class TokenType(Enum):
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    REFERENCE = "REFERENCE"  # &name
    LBRACE = "LBRACE"        # {
    RBRACE = "RBRACE"        # }
    SEMICOLON = "SEMICOLON"  # ;
    EQUALS = "EQUALS"        # =
    COMMA = "COMMA"          # ,
    ANGLE_OPEN = "ANGLE_OPEN"   # <
    ANGLE_CLOSE = "ANGLE_CLOSE" # >
    PREPROCESSOR = "PREPROCESSOR"
    COMMENT = "COMMENT"
    # ... and more
```

---

## DTWalker and DTMultiWalker

Traverses device tree AST to find nodes and properties.

### Class: `DTWalker`

```python
class DTWalker:
    def __init__(self, root: DTNode, logger: Optional[LayoutLogger] = None)
```

**Parameters:**
- `root` (DTNode): Root node to walk
- `logger` (Optional[LayoutLogger]): Logger for structured logging

### Class: `DTMultiWalker`

```python
class DTMultiWalker:
    def __init__(self, roots: list[DTNode])
```

**Parameters:**
- `roots` (list[DTNode]): List of root nodes to walk

### Methods

#### `find_nodes`

```python
def find_nodes(self, predicate: Callable[[DTNode], bool]) -> list[DTNode]
```

Finds all nodes matching predicate.

**Parameters:**
- `predicate` (Callable): Function to test nodes

**Returns:** List of matching nodes

#### `find_nodes_by_compatible`

```python
def find_nodes_by_compatible(self, compatible: str) -> list[DTNode]
```

Finds nodes with specific compatible string.

#### `find_nodes_by_name`

```python
def find_nodes_by_name(self, name: str) -> list[DTNode]
```

Finds nodes with specific name.

#### `find_properties`

```python
def find_properties(
    self, predicate: Callable[[DTProperty], bool]
) -> list[tuple[DTNode, DTProperty]]
```

Finds all properties matching predicate.

**Returns:** List of (node, property) tuples

## Behavior Extractors

Specialized extractors for different behavior types:

### `BehaviorExtractor`

```python
class BehaviorExtractor(DTVisitor):
    def __init__(self)
```

Extracts behavior definitions from device tree AST using the visitor pattern.

### `MacroExtractor`

```python
class MacroExtractor:
    def extract_macros(self, root: DTNode) -> list[DTNode]
```

Extracts macro definitions from macros sections.

### `HoldTapExtractor`

```python
class HoldTapExtractor:
    def extract_hold_taps(self, root: DTNode) -> list[DTNode]
```

Extracts hold-tap definitions from behaviors sections.

### `ComboExtractor`

```python
class ComboExtractor:
    def __init__(self, logger: Optional[LayoutLogger] = None)
    def extract_combos(self, root: DTNode) -> list[DTNode]
```

Extracts combo definitions from combos sections.

### `UniversalBehaviorExtractor`

```python
class UniversalBehaviorExtractor:
    def __init__(self, logger: Optional[LayoutLogger] = None)
    def extract_all_behaviors(self, root: DTNode) -> dict[str, list[DTNode]]
    def extract_behaviors_as_models(
        self,
        roots: list[DTNode],
        source_content: str = "",
        defines: Optional[dict[str, str]] = None,
    ) -> dict[str, list[Any]]
```

Universal extractor that finds all behavior types and converts them to models.

---

## KeymapProcessors

Transform raw parsed data into model instances.

### BaseKeymapProcessor

Base class for keymap processors with common functionality.

```python
class BaseKeymapProcessor:
    def __init__(
        self,
        logger: Optional[LayoutLogger] = None,
        section_extractor: Optional[SectionExtractorProtocol] = None,
    )
    
    def process(self, context: ParsingContext) -> LayoutData | None
```

### FullKeymapProcessor

Processes complete standalone keymap files without template awareness.

```python
class FullKeymapProcessor(BaseKeymapProcessor):
    def process(self, context: ParsingContext) -> LayoutData | None
```

### TemplateAwareProcessor

Uses keyboard profile templates to extract only user-defined data.

```python
class TemplateAwareProcessor(BaseKeymapProcessor):
    def process(self, context: ParsingContext) -> LayoutData | None
```

---

## Parsing Complex Structures

### Nested Behaviors

The parser handles complex nested behaviors:

```python
# Parse complex binding
binding_str = "&mt LSHIFT LC(LA(DEL))"
binding = LayoutBinding.from_str(binding_str)

# Results in:
# LayoutBinding(
#     type="mt",
#     params=[
#         LayoutParam(name="hold", value="LSHIFT"),
#         LayoutParam(name="tap", value="LC(LA(DEL))")
#     ]
# )
```

### Preprocessor Directives

Handles C preprocessor directives:

```python
content = """
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

#define DEFAULT 0
#define NAV     1

keymap {
    compatible = "zmk,keymap";
    
    default_layer {
        bindings = <
            &kp Q  &kp W  &kp E
            &mo NAV &kp SPACE &trans
        >;
    };
};
"""

parser = ZMKKeymapParser()
data = parser.parse(content)
```

### Template Processing

Supports template syntax:

```python
content = """
{% set layer_count = 4 %}

keymap {
    compatible = "zmk,keymap";
    
    {% for i in range(layer_count) %}
    layer_{{ i }} {
        bindings = <{{ bindings[i] | join(" ") }}>;
    };
    {% endfor %}
};
"""

parser = ZMKKeymapParser(providers=providers_with_jinja2)
data = parser.parse(content)
```

---

## Error Handling

### DTParseError

Main exception for device tree parsing errors.

```python
class DTParseError(Exception):
    def __init__(
        self,
        message: str,
        line: int = 0,
        column: int = 0,
        context: str = ""
    )
```

**Fields:**
- `message`: Error message
- `line`: Line number where error occurred
- `column`: Column number where error occurred
- `context`: Context string around error location

**Example:**
```python
try:
    root = parser.parse()
except DTParseError as e:
    print(f"Parse error at line {e.line}, column {e.column}: {e.message}")
```

### Error Recovery

The parser attempts to recover from certain errors and provides detailed error information:

```python
from zmk_layout.parsers import parse_dt_safe

# Safe parsing with error collection
root, errors = parse_dt_safe(content)

if errors:
    for error in errors:
        print(f"Parse error: {error.message} at line {error.line}")
else:
    print("Parsing successful")
```

---

## Custom Parsing

### Extending the Parser

Create custom parsers by extending base classes:

```python
class CustomKeymapProcessor(BaseKeymapProcessor):
    def process(self, context: ParsingContext) -> LayoutData | None:
        # Custom processing logic
        layout_data = self._create_base_layout_data(context)
        
        # Add custom processing here
        self._process_custom_sections(context, layout_data)
        
        return layout_data

# Use custom processor
processors = {
    ParsingMode.FULL: CustomKeymapProcessor(),
    ParsingMode.TEMPLATE_AWARE: TemplateAwareProcessor()
}
parser = ZMKKeymapParser(processors=processors)
```

### Custom Extractors

Add custom behavior extractors:

```python
class CustomBehaviorExtractor:
    def extract_custom_behaviors(self, root: DTNode) -> list[DTNode]:
        walker = DTWalker(root)
        return walker.find_nodes_by_compatible("custom,behavior")

# Create universal extractor with custom patterns
extractor = UniversalBehaviorExtractor()
extractor.behavior_patterns["custom"] = ["custom,behavior"]
```

---

## Performance Optimization

### Factory Functions

Convenience functions for creating parser instances:

```python
from zmk_layout.parsers import (
    create_zmk_keymap_parser,
    create_zmk_keymap_parser_from_profile
)

# Create basic parser
parser = create_zmk_keymap_parser()

# Create parser configured for specific profile
parser = create_zmk_keymap_parser_from_profile(profile)
```

### Convenience Functions

Utility functions for common parsing operations:

```python
from zmk_layout.parsers import (
    parse_dt,
    parse_dt_safe,
    parse_dt_multiple,
    parse_dt_multiple_safe,
    parse_dt_lark,
    parse_dt_lark_safe,
)

# Parse single device tree
root = parse_dt(content)

# Parse with error handling
root, errors = parse_dt_safe(content)

# Parse multiple device trees
roots = parse_dt_multiple(content)

# Parse multiple with error handling
roots, errors = parse_dt_multiple_safe(content)
```

---

## Validation

### Device Tree AST Nodes

#### DTNode

```python
class DTNode:
    def __init__(
        self,
        name: str = "",
        label: str = "",
        unit_address: str = "",
        line: int = 0,
        column: int = 0
    )
```

Represents a device tree node with properties, children, and metadata.

#### DTProperty

```python
@dataclass
class DTProperty:
    name: str
    value: DTValue | None = None
    line: int = 0
    column: int = 0
    comments: list[str] = field(default_factory=list)
```

#### DTValue

```python
@dataclass
class DTValue:
    type: DTValueType
    value: Any
    raw: str = ""
```

With factory methods: `string()`, `integer()`, `array()`, `reference()`, `boolean()`

### AST Node Types

#### DTComment

```python
@dataclass
class DTComment:
    text: str
    line: int = 0
    column: int = 0
    is_block: bool = False  # True for /* */, False for //
```

#### DTConditional

```python
@dataclass
class DTConditional:
    directive: str  # ifdef, ifndef, else, endif
    condition: str = ""
    line: int = 0
    column: int = 0
```

#### DTValueType

```python
class DTValueType(Enum):
    STRING = "string"
    INTEGER = "integer"
    ARRAY = "array"
    REFERENCE = "reference"
    BOOLEAN = "boolean"
```

---

## Testing Parsers

### Unit Testing

```python
import pytest
from zmk_layout.parsers import ZMKKeymapParser, DTParseError, ParsingMode

def test_parse_simple_keymap():
    parser = ZMKKeymapParser()
    content = """
    keymap {
        compatible = "zmk,keymap";
        default_layer {
            bindings = <&kp Q &kp W>;
        };
    };
    """
    
    result = parser.parse_keymap(content, mode=ParsingMode.FULL)
    assert result.success
    assert result.layout_data is not None
    assert len(result.layout_data.layers) == 2  # Q and W

def test_parse_invalid_syntax():
    from zmk_layout.parsers import parse_dt_safe
    
    root, errors = parse_dt_safe("invalid { syntax")
    
    assert len(errors) > 0
    assert isinstance(errors[0], DTParseError)
```

### Fuzzing

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_parser_doesnt_crash(content):
    from zmk_layout.parsers import parse_dt_safe
    
    try:
        root, errors = parse_dt_safe(content)
        # Should not crash, but may have errors
    except DTParseError:
        # Expected for invalid input
        pass
    except Exception as e:
        # Parser should handle errors gracefully
        pytest.fail(f"Unexpected exception: {e}")
```

---

## Best Practices

1. **Choose appropriate parsing mode**: Use `FULL` for complete keymaps, `TEMPLATE_AWARE` for profile-based extraction
2. **Handle DTParseError gracefully**: Provide user-friendly error messages
3. **Use safe parsing functions**: Use `parse_dt_safe()` for error collection
4. **Process results properly**: Check `KeymapParseResult.success` before using data
5. **Test with real keymaps**: Use actual ZMK keymap files for testing
6. **Use structured logging**: Pass logger instances for better debugging
7. **Preserve comments and metadata**: AST nodes include comment information
8. **Use appropriate processor**: Full vs TemplateAware based on use case
9. **Handle multiple roots**: Use `parse_dt_multiple()` for complex files
10. **Leverage behavior extractors**: Use `UniversalBehaviorExtractor` for comprehensive extraction