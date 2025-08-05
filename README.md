# ZMK Layout Library

A standalone Python library for manipulating ZMK keyboard layouts with a modern fluent API.

## Features

- **Fluent API**: Intuitive, chainable interface for layout operations
- **Type Safety**: Comprehensive type hints and runtime validation  
- **Provider Pattern**: Clean abstraction of external dependencies
- **Optional Dependencies**: Graceful degradation when features unavailable
- **Comprehensive**: Full ZMK layout support including behaviors, combos, macros

## Quick Start

```python
from zmk_layout import Layout

# Load and modify a layout
l = Layout("myfile.keymap")
l.layers.add("newlayer")
l.layers.get("newlayer").set(0, "&kp D")
l.save("mylayout.json")
```

## Installation

```bash
pip install zmk-layout

# With optional dependencies
pip install zmk-layout[full]
```

## Documentation

See the [documentation](https://zmk-layout.readthedocs.io) for detailed usage examples and API reference.

## License

MIT License - see LICENSE file for details.