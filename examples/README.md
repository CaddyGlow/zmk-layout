# ZMK Layout Examples

This directory contains example scripts and files demonstrating the ZMK Layout library functionality using the **data-only API approach**.

## Data-Only API Approach

The zmk-layout library now uses a data-only API where the Layout class operates purely on dictionaries, providing clean separation of concerns:

- **Layout operations**: Work with dictionaries, not files directly  
- **File I/O**: Handled externally using `pathlib.Path`
- **JSON operations**: Use dedicated utilities from `zmk_layout.utils.json_operations`
- **Parsing**: Work with string content, produce LayoutData objects
- **Generation**: Produce string output, not files

### Key API Changes

| Old API | New Data-Only API |
|---------|------------------|
| `Layout.from_file(path)` | `Layout.from_dict(data)` |
| `Layout.save(path)` | `Layout.to_dict()` + `Path.write_text()` |
| Direct file operations | External file handling with `pathlib.Path` |
| Built-in JSON handling | `json_operations` utilities |

### Benefits

- **Better testability**: Mock data instead of files
- **Cleaner separation**: Layout logic vs I/O operations  
- **More flexible**: Easy integration into data pipelines
- **Safer**: No accidental file modifications

## Example Files

## Core Examples

### `data_only_usage.py` - **NEW**

Comprehensive demonstration of the new data-only API patterns:
- Loading/saving with `Path.read_text()`/`write_text()`
- Using `Layout.from_dict()` and `Layout.to_dict()`
- Working with JSON utilities
- Parser and generator string-based operations
- Complete roundtrip examples
- Best practices summary

### `basic_usage.py`

Core fluent API functionality updated for data-only approach:
- Layout creation and manipulation
- Layer and behavior management
- Data-only save/load operations

### `advanced_operations.py`

Advanced features with data-only patterns:
- Complex behaviors and layer manipulation
- Error handling and validation
- File integrity checks using data operations

### `simple_demo.py`

Quick demonstration of the fluent API with external file handling.

## Roundtrip Demo

The `roundtrip_demo.py` script demonstrates complete roundtrip transformations between JSON and keymap formats using the Factory layout files.

### Usage

```bash
# Run the roundtrip demonstration
uv run python examples/roundtrip_demo.py

# Or run directly if you have Python with dependencies installed
python examples/roundtrip_demo.py
```

### What it does

1. **JSON → Keymap**: Loads `Factory.json`, converts to keymap format, saves as `generated_from_json.keymap`
2. **Keymap → JSON**: Loads `Factory.keymap`, converts to JSON format, saves as `generated_from_keymap.json`  
3. **Full Roundtrip**: Performs complete cycle (JSON → Keymap → JSON) with validation

### Output Files

All generated files are saved to `examples/output/`:

- `generated_from_json.keymap` - Keymap generated from Factory.json
- `generated_from_keymap.json` - JSON generated from Factory.keymap
- `roundtrip_intermediate.keymap` - Intermediate keymap in full roundtrip test
- `roundtrip_final.json` - Final JSON after complete roundtrip

### Input Files

The script uses these example layouts in `examples/layouts/`:

- `Factory.json` - Factory layout in JSON format (Glove80)
- `Factory.keymap` - Factory layout in ZMK keymap format (Glove80)

### Features Demonstrated

- **Provider Pattern**: Uses Glove80ConfigurationProvider for keyboard-specific features
- **Parsing Modes**: Demonstrates FULL parsing mode for reliability
- **Data Validation**: Validates roundtrip integrity including layer counts, key counts, and Glove80-specific behaviors
- **Error Handling**: Comprehensive error handling and fallback mechanisms
- **File Management**: Proper temporary file handling and output organization
- **Data-Only Operations**: Shows parser string input/output patterns

## Data-Only API Examples

### Basic Pattern

```python
from pathlib import Path
from zmk_layout import Layout
from zmk_layout.utils.json_operations import serialize_json_data, parse_json_data

# Load from file
file_content = Path("layout.json").read_text()
layout_dict = parse_json_data(file_content)
layout = Layout.from_dict(layout_dict)

# Modify layout
layout.layers.add("gaming").set(0, "&kp W")

# Save to file  
layout_data = layout.to_dict()
json_content = serialize_json_data(layout_data, indent=2)
Path("modified_layout.json").write_text(json_content)
```

### Parser Pattern

```python
from zmk_layout.parsers.zmk_keymap_parser import ZMKKeymapParser

# Parse keymap content
parser = ZMKKeymapParser(configuration_provider=providers.configuration)
parse_result = parser.parse_keymap(keymap_file_path)  
layout_data = parse_result.layout_data

# Convert to Layout
layout_dict = layout_data.model_dump(by_alias=True)
layout = Layout.from_dict(layout_dict)
```

### Generator Pattern

```python
from zmk_layout.generators.zmk_generator import ZMKGenerator

# Generate keymap string
generator = ZMKGenerator(providers=providers)
layout_data = layout.data
keymap_content = generator.generate_keymap_node(
    profile, layout_data.layer_names, layout_data.layers
)

# Save to file
Path("output.keymap").write_text(keymap_content)
```

## Running Examples

```bash
# Run the comprehensive data-only demo (recommended starting point)
uv run python examples/data_only_usage.py

# Run specific examples
uv run python examples/basic_usage.py
uv run python examples/advanced_operations.py
uv run python examples/real_world_example.py

# Run roundtrip demonstration
uv run python examples/roundtrip_demo.py
```

### Requirements

This example requires the zmk-layout library and its dependencies. If the complete Glove80 profile is not available, it will use fallback configurations to still demonstrate the core functionality.

## Migration Guide

To update existing code to the data-only API:

1. **Replace file operations**:
   ```python
   # Old
   layout = Layout.from_file("layout.json")
   layout.save("output.json")
   
   # New
   content = Path("layout.json").read_text()
   data = parse_json_data(content)
   layout = Layout.from_dict(data)
   
   output_data = layout.to_dict()
   json_content = serialize_json_data(output_data)
   Path("output.json").write_text(json_content)
   ```

2. **Use JSON utilities for robust handling**:
   ```python
   from zmk_layout.utils.json_operations import (
       parse_json_data, serialize_json_data,
       parse_layout_data, serialize_layout_data
   )
   ```

3. **Handle parsers and generators with strings**:
   - Parsers work with file paths but return data objects
   - Generators produce string content for external saving
   - Assemble generated components manually

See `data_only_usage.py` for comprehensive migration examples.