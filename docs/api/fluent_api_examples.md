# ZMK Layout Fluent API - Complete Examples

## Table of Contents

1. [Quick Start Examples](#quick-start-examples)
2. [Real-World Keyboard Layouts](#real-world-keyboard-layouts)
3. [Advanced Behavior Patterns](#advanced-behavior-patterns)
4. [Pipeline Examples](#pipeline-examples)
5. [Error Handling Patterns](#error-handling-patterns)
6. [Performance Optimization](#performance-optimization)

## Quick Start Examples

### Example 1: Basic Corne (CRKBD) Layout

```python
from zmk_layout import Layout, Binding

# Create a complete Corne layout with home row mods
layout = (Layout
    .create_empty("crkbd", "Corne with Home Row Mods")
    .with_author("Your Name")
    .with_description("Colemak-DH with home row modifiers")

    # Define behaviors first
    .behaviors
        .add_hold_tap("hm",
            hold="&kp",
            tap="&kp",
            tapping_term_ms=200,
            quick_tap_ms=150,
            flavor="tap-preferred")
        .add_hold_tap("lt",
            hold="&mo",
            tap="&kp",
            tapping_term_ms=200)
    .parent

    # Base layer (Colemak-DH)
    .layers.add("base")
        .set_range(0, 42, [
            # Left side
            "&kp TAB",    "&kp Q",     "&kp W",     "&kp F",     "&kp P",     "&kp B",
            "&kp ESC",    "&hm LGUI A","&hm LALT R","&hm LCTRL S","&hm LSHIFT T","&kp G",
            "&kp LSHIFT", "&kp Z",     "&kp X",     "&kp C",     "&kp D",     "&kp V",
            # Left thumb cluster
                                       "&kp LGUI",  "&mo 1",     "&kp SPACE",

            # Right side
            "&kp J",      "&kp L",     "&kp U",     "&kp Y",     "&kp SEMI",  "&kp BSPC",
            "&kp M",      "&hm RSHIFT N","&hm RCTRL E","&hm RALT I","&hm RGUI O","&kp SQT",
            "&kp K",      "&kp H",     "&kp COMMA", "&kp DOT",   "&kp SLASH", "&kp RSHIFT",
            # Right thumb cluster
            "&kp RET",    "&mo 2",     "&kp RALT"
        ])
    .parent

    # Navigation layer
    .layers.add("nav")
        .set_range(0, 42, [
            # Left side
            "&trans",     "&kp N1",    "&kp N2",    "&kp N3",    "&kp N4",    "&kp N5",
            "&trans",     "&kp LEFT",  "&kp DOWN",  "&kp UP",    "&kp RIGHT", "&kp PG_UP",
            "&trans",     "&kp HOME",  "&kp END",   "&kp DEL",   "&kp BSPC",  "&kp PG_DN",
            # Left thumb
                                       "&trans",    "&trans",    "&trans",

            # Right side
            "&kp N6",     "&kp N7",    "&kp N8",    "&kp N9",    "&kp N0",    "&trans",
            "&kp MINUS",  "&kp EQUAL", "&kp LBKT",  "&kp RBKT",  "&kp BSLH",  "&trans",
            "&kp UNDER",  "&kp PLUS",  "&kp LBRC",  "&kp RBRC",  "&kp PIPE",  "&trans",
            # Right thumb
            "&trans",     "&trans",    "&trans"
        ])
    .parent

    # Symbol layer
    .layers.add("sym")
        .set_range(0, 42, [
            # Left side
            "&trans",     "&kp EXCL",  "&kp AT",    "&kp HASH",  "&kp DOLLAR","&kp PERCENT",
            "&trans",     "&kp GRAVE", "&kp TILDE", "&kp UNDER", "&kp MINUS", "&kp STAR",
            "&trans",     "&kp LT",    "&kp GT",    "&kp QMARK", "&kp COLON", "&kp SEMI",
            # Left thumb
                                       "&trans",    "&trans",    "&trans",

            # Right side
            "&kp CARET",  "&kp AMPS",  "&kp STAR",  "&kp LPAR",  "&kp RPAR",  "&trans",
            "&kp EQUAL",  "&kp PLUS",  "&kp LBKT",  "&kp RBKT",  "&kp BSLH",  "&trans",
            "&kp PIPE",   "&kp SLASH", "&kp LBRC",  "&kp RBRC",  "&kp DOT",   "&trans",
            # Right thumb
            "&trans",     "&trans",    "&trans"
        ])
    .parent

    .save("crkbd_colemak_dh.json"))
```

### Example 2: Sofle Layout with Advanced Features

```python
from zmk_layout import Layout

# Sofle with combos, macros, and tap dances
layout = (Layout
    .create_empty("sofle", "Sofle Advanced")

    # Add combos for common bigrams
    .behaviors
        .add_combo("combo_the",
            keys=[16, 17],  # T + H positions
            bindings=["&kp T", "&kp H", "&kp E"],
            timeout_ms=30,
            layers=["base"])
        .add_combo("combo_and",
            keys=[27, 28],  # A + N positions
            bindings=["&kp A", "&kp N", "&kp D"],
            timeout_ms=30,
            layers=["base"])

        # Tap dance for quotes
        .add_tap_dance("td_quotes",
            bindings=["&kp SQT", "&kp DQT", "&kp GRAVE"])

        # Macro for email signature
        .add_macro("email_sig",
            bindings=[
                "&kp B", "&kp E", "&kp S", "&kp T",
                "&kp SPACE",
                "&kp R", "&kp E", "&kp G", "&kp A", "&kp R", "&kp D", "&kp S",
                "&kp COMMA", "&kp RET",
                "&kp Y", "&kp O", "&kp U", "&kp R",
                "&kp SPACE",
                "&kp N", "&kp A", "&kp M", "&kp E"
            ],
            wait_ms=30,
            tap_ms=30)
    .parent

    # Configure layers with advanced bindings
    .layers.add("base")
        # ... layer configuration
    .parent

    .validate()
    .save("sofle_advanced.json"))
```

## Real-World Keyboard Layouts

### Example 3: Split 3x6 Keyboard with Multiple Layouts

```python
from zmk_layout import Layout, Binding

def create_multi_layout_keyboard():
    """Create a keyboard supporting QWERTY, Colemak, and Dvorak"""

    base_layout = (Layout
        .create_empty("splitkb_aurora_sweep", "Multi-Layout Sweep")
        .with_metadata({
            "version": "2.0",
            "layouts_supported": ["qwerty", "colemak", "dvorak"],
            "default_layout": "colemak"
        }))

    # Add layout-specific layers
    layouts = {
        "qwerty": ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
        "colemak": ["q", "w", "f", "p", "g", "j", "l", "u", "y", "semicolon"],
        "dvorak": ["quote", "comma", "period", "p", "y", "f", "g", "c", "r", "l"]
    }

    for layout_name, keys in layouts.items():
        layer_bindings = [f"&kp {key.upper()}" for key in keys]
        # Pad to full layer size
        layer_bindings.extend(["&trans"] * (36 - len(layer_bindings)))

        base_layout = (base_layout.layers
            .add(f"{layout_name}_base", bindings=layer_bindings)
            .parent)

    # Add shared layers
    base_layout = (base_layout
        .layers.add("numbers")
            .set_range(0, 10, [f"&kp N{i}" for i in range(10)])
            .pad_to(36, "&trans")
        .parent
        .layers.add("symbols")
            # Add symbol bindings
        .parent
        .layers.add("navigation")
            # Add navigation bindings
        .parent)

    return base_layout

# Create and save
multi_layout = create_multi_layout_keyboard()
multi_layout.save("multi_layout_sweep.json")
```

### Example 4: Ergodox with Complex Layer System

```python
from zmk_layout import Layout

def create_ergodox_layout():
    """Create an Ergodox layout with 7 layers and complex behaviors"""

    layout = (Layout
        .create_empty("ergodox", "Professional Ergodox")
        .with_description("Ergodox layout optimized for programming and typing"))

    # Define layer tap behaviors for each layer
    for i in range(1, 7):
        layout = (layout.behaviors
            .add_hold_tap(f"lt{i}",
                hold=f"&mo {i}",
                tap="&kp",
                tapping_term_ms=200 - (i * 10))  # Faster for higher layers
            .parent)

    # Layer structure:
    # 0: Base (Colemak)
    # 1: Symbols
    # 2: Numbers
    # 3: Function keys
    # 4: Media
    # 5: Gaming
    # 6: System

    layers = [
        ("base", generate_colemak_bindings()),
        ("symbols", generate_symbol_bindings()),
        ("numbers", generate_number_bindings()),
        ("function", generate_function_bindings()),
        ("media", generate_media_bindings()),
        ("gaming", generate_gaming_bindings()),
        ("system", generate_system_bindings())
    ]

    for layer_name, bindings in layers:
        layout = (layout.layers
            .add(layer_name, bindings=bindings)
            .parent)

    # Add advanced features
    layout = (layout
        # One-shot modifiers
        .behaviors
            .add_sticky_key("sk_shift", "&kp LSHIFT", release_after_ms=1000)
            .add_sticky_key("sk_ctrl", "&kp LCTRL", release_after_ms=1000)
        .parent

        # Leader key sequences
        .behaviors
            .add_macro("leader_vim_save",
                bindings=["&kp ESC", "&kp COLON", "&kp W", "&kp RET"])
            .add_macro("leader_vim_quit",
                bindings=["&kp ESC", "&kp COLON", "&kp Q", "&kp RET"])
        .parent)

    return layout

def generate_colemak_bindings():
    """Generate Colemak bindings for Ergodox (76 keys)"""
    # Implementation details...
    return ["&kp Q", "&kp W", "&kp F", "&kp P", "&kp G"] + ["&trans"] * 71

# Similar functions for other binding sets...
```

## Advanced Behavior Patterns

### Example 5: Conditional Behaviors

```python
from zmk_layout import Layout, ConditionalBuilder

# Create conditional behaviors based on layer state
layout = (Layout
    .create_empty("crkbd", "Conditional Behaviors")

    # Define conditional hold-tap based on active layer
    .behaviors
        .add_conditional("smart_shift",
            condition="layer_active(gaming)",
            then_binding="&kp LCTRL",  # Ctrl in gaming
            else_binding="&kp LSHIFT")  # Shift otherwise
    .parent

    # Adaptive tap dance that changes based on layer
    .behaviors
        .add_adaptive_tap_dance("adaptive_td",
            layer_bindings={
                "base": ["&kp SQT", "&kp DQT"],
                "code": ["&kp LBKT", "&kp RBKT", "&kp LBRC", "&kp RBRC"],
                "markdown": ["&kp STAR", "&kp STAR STAR", "&kp UNDER UNDER"]
            })
    .parent)
```

### Example 6: Custom Modifier Behaviors

```python
from zmk_layout import Layout

# Create custom modifier combinations
layout = (Layout
    .create_empty("crkbd", "Custom Modifiers")

    .behaviors
        # Hyper key (all modifiers)
        .add_behavior("hyper",
            type="modifier",
            mods=["LGUI", "LALT", "LCTRL", "LSHIFT"])

        # Meh key (Ctrl+Alt+Shift)
        .add_behavior("meh",
            type="modifier",
            mods=["LCTRL", "LALT", "LSHIFT"])

        # Custom navigation modifier
        .add_hold_tap("nav_mod",
            hold="&mo NAV",
            tap="&sk LCTRL",
            tapping_term_ms=150,
            flavor="hold-preferred")
    .parent)
```

## Pipeline Examples

### Example 7: Complete Processing Pipeline

```python
from zmk_layout import ProcessingPipeline, ValidationPipeline, GeneratorPipeline

def process_keymap_file(input_file: str, output_dir: str):
    """Complete pipeline from DTSI to generated files"""

    # Step 1: Parse and process
    processed = (ProcessingPipeline()
        .from_dtsi(input_file)
        .parse()
        .extract_layers()
        .extract_behaviors()
        .normalize_bindings()
        .optimize_redundant_behaviors()
        .transform(lambda node:
            node.replace("&trans", "&none") if node.layer == "gaming" else node)
        .build())

    # Step 2: Validate
    validation = (ValidationPipeline()
        .for_layout(processed)
        .check_binding_syntax()
        .check_layer_consistency()
        .check_behavior_references()
        .check_key_coverage(min_coverage=0.8)
        .validate())

    if not validation.is_valid:
        print("Validation errors:")
        for error in validation.errors:
            print(f"  - {error}")
        return None

    # Step 3: Generate output files
    result = (GeneratorPipeline()
        .from_layout(processed)
        .with_metadata({
            "generated_at": datetime.now().isoformat(),
            "source_file": input_file,
            "validation_passed": True
        })
        .generate_keymap()
        .generate_behaviors()
        .generate_combos()
        .generate_documentation()
        .write_to(output_dir))

    return result

# Usage
result = process_keymap_file("keymap.dtsi", "output/")
print(f"Generated {len(result.files)} files")
```

### Example 8: Custom Transformation Pipeline

```python
from zmk_layout import Layout, TransformationPipeline

class QMKToZMKConverter:
    """Convert QMK keymaps to ZMK format"""

    def convert(self, qmk_file: str) -> Layout:
        return (TransformationPipeline()
            .from_qmk(qmk_file)
            .map_keycodes(self.qmk_to_zmk_mapping())
            .convert_layers()
            .convert_macros()
            .convert_tap_dances()
            .add_zmk_specific_features()
            .validate()
            .to_layout())

    def qmk_to_zmk_mapping(self):
        return {
            "KC_A": "&kp A",
            "KC_LGUI": "&kp LGUI",
            "LT(1, KC_SPC)": "&lt 1 SPACE",
            "MT(MOD_LSFT, KC_A)": "&hm LSHIFT A",
            # ... more mappings
        }

# Usage
converter = QMKToZMKConverter()
zmk_layout = converter.convert("qmk_keymap.c")
zmk_layout.save("converted_keymap.json")
```

## Error Handling Patterns

### Example 9: Robust File Processing

```python
from zmk_layout import Layout, LayoutError
import logging

logger = logging.getLogger(__name__)

def safe_layout_processing(file_path: str) -> Layout | None:
    """Process layout with comprehensive error handling"""

    try:
        # Try primary processing path
        layout = (Layout
            .from_file(file_path)
            .validate()
            .normalize())

    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}, creating default")
        layout = Layout.create_empty("crkbd", "Default")

    except LayoutError as e:
        logger.error(f"Layout error: {e}")

        # Try recovery
        if e.recoverable:
            layout = (Layout
                .from_file(file_path)
                .fix_common_issues()
                .validate_lenient())
        else:
            return None

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

    finally:
        # Always save a backup
        if layout:
            layout.save(f"{file_path}.backup")

    return layout
```

### Example 10: Pipeline with Fallbacks

```python
from zmk_layout import GeneratorPipeline, Template

def generate_with_fallbacks(layout: Layout) -> dict:
    """Generate files with multiple fallback strategies"""

    pipeline = (GeneratorPipeline()
        .from_layout(layout)
        .with_error_handler(lambda e: logger.error(f"Generation error: {e}")))

    # Try custom template first
    try:
        result = pipeline.with_template("custom.dtsi.j2").generate()
    except Template.NotFoundError:
        # Fall back to default template
        try:
            result = pipeline.with_template("default.dtsi.j2").generate()
        except:
            # Final fallback: basic generation
            result = pipeline.generate_basic()

    return result
```

## Performance Optimization

### Example 11: Batch Processing with Caching

```python
from zmk_layout import Layout, ProviderBuilder
import time

def batch_process_layouts(files: list[str]):
    """Process multiple layouts efficiently"""

    # Configure with caching
    providers = (ProviderBuilder()
        .enable_caching(size=1024)
        .enable_performance_tracking()
        .build())

    results = []
    start_time = time.time()

    # Process in batch with shared cache
    for file_path in files:
        layout = (Layout
            .with_providers(providers)
            .from_file(file_path)
            .cache_key(file_path)  # Enable result caching
            .validate_cached()  # Use cached validation if available
            .optimize_cached())  # Use cached optimization

        results.append(layout)

    elapsed = time.time() - start_time
    print(f"Processed {len(files)} layouts in {elapsed:.2f}s")
    print(f"Cache hit rate: {providers.cache_stats.hit_rate:.1%}")

    return results
```

### Example 12: Lazy Evaluation Pattern

```python
from zmk_layout import Layout, LazyPipeline

def create_lazy_pipeline(layout: Layout):
    """Create pipeline with deferred execution"""

    # Build pipeline without executing
    pipeline = (LazyPipeline()
        .from_layout(layout)
        .add_step(lambda l: l.normalize())
        .add_step(lambda l: l.optimize())
        .add_step(lambda l: l.validate())
        .add_conditional(
            condition=lambda l: len(l.layers) > 5,
            step=lambda l: l.compress())
        .add_parallel([
            lambda l: l.generate_keymap(),
            lambda l: l.generate_behaviors(),
            lambda l: l.generate_documentation()
        ]))

    # Pipeline not executed yet
    print(f"Pipeline has {len(pipeline.steps)} steps")

    # Execute when needed
    if user_confirms():
        result = pipeline.execute()
        return result

    return None
```

### Example 13: Streaming Processing

```python
from zmk_layout import StreamingProcessor

def process_large_keymap(file_path: str):
    """Process large keymaps in streaming fashion"""

    processor = (StreamingProcessor()
        .from_file(file_path)
        .chunk_size(100)  # Process 100 bindings at a time
        .on_chunk(lambda chunk: validate_chunk(chunk))
        .on_progress(lambda p: print(f"Progress: {p:.1%}"))
        .parallel_chunks(4))  # Process 4 chunks in parallel

    # Stream processing
    for result in processor.stream():
        # Handle each chunk result
        if result.has_errors:
            print(f"Errors in chunk: {result.errors}")

    return processor.finalize()
```

## Complete Application Example

### Example 14: CLI Application with Fluent API

```python
import typer
from zmk_layout import Layout, GeneratorPipeline, ValidationPipeline
from pathlib import Path

app = typer.Typer()

@app.command()
def create(
    keyboard: str,
    name: str,
    output: Path = Path("layout.json"),
    validate: bool = True
):
    """Create a new keyboard layout"""

    layout = (Layout
        .create_empty(keyboard, name)
        .with_author(get_git_author())
        .with_metadata({
            "created_with": "zmk-layout-cli",
            "version": "1.0.0"
        }))

    if validate:
        validation = (ValidationPipeline()
            .for_layout(layout)
            .validate())

        if not validation.is_valid:
            typer.echo("Validation failed:", err=True)
            for error in validation.errors:
                typer.echo(f"  - {error}", err=True)
            raise typer.Exit(1)

    layout.save(output)
    typer.echo(f"Created layout: {output}")

@app.command()
def convert(
    input_file: Path,
    output_dir: Path = Path("output"),
    format: str = "zmk"
):
    """Convert layout to different format"""

    layout = Layout.from_file(input_file)

    pipeline = (GeneratorPipeline()
        .from_layout(layout)
        .with_format(format))

    if format == "zmk":
        pipeline = (pipeline
            .generate_keymap()
            .generate_behaviors()
            .generate_combos())
    elif format == "qmk":
        pipeline = pipeline.generate_qmk()
    elif format == "via":
        pipeline = pipeline.generate_via()

    result = pipeline.write_to(output_dir)
    typer.echo(f"Generated {len(result.files)} files in {output_dir}")

@app.command()
def validate(input_file: Path, strict: bool = False):
    """Validate a layout file"""

    layout = Layout.from_file(input_file)

    validation = (ValidationPipeline()
        .for_layout(layout)
        .with_level("strict" if strict else "normal")
        .check_all()
        .validate())

    if validation.is_valid:
        typer.echo("✓ Layout is valid")
    else:
        typer.echo("✗ Layout has issues:", err=True)
        for error in validation.errors:
            typer.echo(f"  ERROR: {error}", err=True)
        for warning in validation.warnings:
            typer.echo(f"  WARNING: {warning}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
```

This comprehensive documentation and examples should provide users with everything they need to effectively use the fluent API in the ZMK Layout Library!
