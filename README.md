# ZMK Layout Library

A standalone Python library for manipulating ZMK keyboard layouts with a modern fluent API. Extracted from the [glovebox](https://github.com/CaddyGlow/zmk-glovebox) project to enable ecosystem growth while maintaining full backward compatibility.

## Project Status

**Current Version:** 0.1.0 (Pre-release)  
**Status:** Ready for GitHub publication, preparing for PyPI release  
**Integration:** Ready for glovebox integration following [ZMK_LAYOUT_EXTRACTION_PLAN.md](https://github.com/CaddyGlow/zmk-glovebox/blob/main/ZMK_LAYOUT_EXTRACTION_PLAN.md)

### Implementation Progress
- **Phase 1:** Provider Interface Pattern - Complete
- **Phase 2:** Model Independence - Complete  
- **Phase 3:** Library Extraction - Complete
- **Phase 4:** Fluent API Implementation - Complete
- **Phase 5:** Glovebox Integration & Ecosystem Launch - In Progress

## Features

- **Fluent API**: Intuitive, chainable interface for layout operations
- **Type Safety**: Comprehensive type hints with mypy strict mode support
- **Provider Pattern**: Clean abstraction allows integration with any keyboard framework
- **Optional Dependencies**: Core functionality with optional templating, display, and parsing features
- **High Performance**: <1 second for all operations, minimal memory footprint
- **Comprehensive**: Full ZMK layout support including behaviors, combos, macros, and more
- **Round-trip Support**: Parse → Modify → Save with perfect fidelity

## Quick Start

```python
from zmk_layout import Layout

# Load and modify a layout
layout = Layout("keyboard.keymap")
layout.layers.add("gaming")
layout.layers.get("gaming").set(0, "&kp W").set(1, "&kp A").set(2, "&kp S").set(3, "&kp D")
layout.save("modified.keymap")

# Fluent interface for complex operations
(layout.layers
    .add("nav")
    .get("nav")
    .set_range(0, 4, ["&kp UP", "&kp DOWN", "&kp LEFT", "&kp RIGHT"])
    .copy_from("default"))

# Add behaviors
layout.behaviors.add_hold_tap("ht_balanced", tap="&kp A", hold="&kp LCTRL")
layout.behaviors.add_combo("copy", keys=[0, 1], binding="&kp LC(C)")
layout.behaviors.add_macro("hello", sequence=["&kp H", "&kp E", "&kp L", "&kp L", "&kp O"])
```

## Installation

### From PyPI (Coming Soon)
```bash
# Core library
pip install zmk-layout

# With all optional features
pip install zmk-layout[full]

# Specific feature sets
pip install zmk-layout[templating]  # Jinja2 template support
pip install zmk-layout[display]     # Rich display formatting
pip install zmk-layout[parsing]     # Lark parser for devicetree files
```

### Development Installation
```bash
# Clone the repository
git clone https://github.com/CaddyGlow/zmk-layout.git
cd zmk-layout

# Install with development dependencies using uv
uv sync --all-extras --dev

# Or use make
make install

# Run all checks (ruff, mypy, tests)
make check

# Auto-fix and format code
make fix

# Run tests only
make test

# Build packages
make build

# Clean build artifacts
make clean
```

## API Examples

### Basic Layout Operations
```python
from zmk_layout import Layout

# Create empty layout
layout = Layout.create_empty(size=36)

# Load from file
layout = Layout.from_keymap("keyboard.keymap")
layout = Layout.from_json("layout.json")

# Layer management
layout.layers.add("symbols", position=1)
layout.layers.remove("gaming")
layout.layers.move("nav", position=0)
layout.layers.reorder(["default", "nav", "symbols"])

# Query layers
gaming_layers = layout.find_layers(lambda name: "gaming" in name)
all_layers = layout.layers.list()
```

### Advanced Features
```python
# Context manager with auto-save
with Layout("keyboard.keymap") as layout:
    layout.layers.add("test")
    # Automatically saves on exit

# Batch operations
layout.batch_operation([
    lambda l: l.layers.add("layer1"),
    lambda l: l.layers.add("layer2"),
    lambda l: l.behaviors.add_macro("test", ["&kp T"])
])

# Statistics and analysis
stats = layout.get_statistics()
print(f"Layers: {stats['layer_count']}")
print(f"Behaviors: {stats['behavior_count']}")

# Validation
layout.validate()  # Raises exception if invalid
```

### Provider Pattern
```python
from zmk_layout import Layout
from zmk_layout.providers import LayoutProviders

# Custom provider implementation
class MyConfigProvider:
    def get_behavior_definitions(self):
        return [...]
    
    def get_validation_rules(self):
        return {...}

# Use custom providers
providers = LayoutProviders(
    configuration=MyConfigProvider(),
    template=MyTemplateProvider(),
    logger=MyLogger(),
    file=MyFileAdapter()
)

layout = Layout("keyboard.keymap", providers=providers)
```

## Architecture

The library uses a clean, modular architecture:

```
zmk_layout/
├── core/           # Core layout classes and fluent API
├── models/         # Pydantic models for layout data
├── parsers/        # Keymap and devicetree parsing
├── generators/     # ZMK code generation
├── providers/      # Provider interfaces for external dependencies
└── utils/          # Utilities and helpers
```

### Key Design Patterns
- **Provider Pattern**: Abstracts external dependencies for maximum flexibility
- **Fluent Interface**: Chainable methods for intuitive API usage
- **Strategy Pattern**: Pluggable parsing and generation strategies
- **Factory Pattern**: Consistent object creation throughout

## Testing

Comprehensive test coverage with 200+ tests:

```bash
# Run all tests with coverage
make test

# Run all checks (ruff, mypy, tests)
make check

# Run specific test categories
pytest tests/core/ -v        # Core functionality tests
pytest tests/fluent/ -v      # Fluent API tests
pytest tests/parsers/ -v     # Parser tests
pytest tests/models/ -v      # Model tests
```

## Performance

All operations complete in <1 second with minimal memory footprint:

- Layout loading: ~50ms
- Layer operations: <1ms each
- Full compilation: ~100ms  
- Memory usage: <10MB for typical layouts

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Ensure quality gates pass:
   ```bash
   make fix    # Auto-fix and format code
   make check  # Run all checks (must pass)
   ```
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style
- We use `ruff` for formatting and linting
- Type hints are required (mypy strict mode)
- Tests are required for new features
- Documentation updates for API changes

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Extracted from the [glovebox](https://github.com/CaddyGlow/zmk-glovebox) project
- Built for the [ZMK firmware](https://zmk.dev) ecosystem
- Inspired by modern Python library design patterns

## Links

- [GitHub Repository](https://github.com/CaddyGlow/zmk-layout)
- [Documentation](https://zmk-layout.readthedocs.io) (Coming Soon)
- [PyPI Package](https://pypi.org/project/zmk-layout/) (Coming Soon)
- [Glovebox Integration Plan](https://github.com/CaddyGlow/zmk-glovebox/blob/main/ZMK_LAYOUT_EXTRACTION_PLAN.md)

---

**Note:** This library is in active development. While the API is stable, minor changes may occur before the 1.0 release.