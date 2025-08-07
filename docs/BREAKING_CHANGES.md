# Breaking Changes - ZMK Layout Library Integration

## Overview

This document outlines all breaking changes when migrating from glovebox's internal layout system to the standalone zmk-layout library. Most changes are related to import paths and model inheritance, with the API remaining largely compatible.

## Version Compatibility

| Glovebox Version | ZMK-Layout Version | Status |
|-----------------|-------------------|---------|
| < 2.0.0 | N/A | Use internal layout system |
| 2.0.0 - 2.x | 0.1.0+ | Transition period (both supported) |
| 3.0.0+ | 0.1.0+ | zmk-layout required |

## Import Path Changes

### Before (Glovebox Internal)
```python
from glovebox.layout.models import LayoutData, LayoutBinding
from glovebox.layout.service import LayoutService
from glovebox.layout.parsers import ZMKKeymapParser
from glovebox.layout.generators import ZMKGenerator
from glovebox.layout.utils import validate_binding
```

### After (ZMK-Layout Library)
```python
from zmk_layout.models import LayoutData, LayoutBinding
from zmk_layout import Layout  # New fluent API
from zmk_layout.parsers import ZMKKeymapParser
from zmk_layout.generators import ZMKGenerator
from zmk_layout.utils import validate_binding
```

## Model Changes

### Base Model Inheritance

#### Before
```python
from glovebox.models.base import GloveboxBaseModel

class LayoutData(GloveboxBaseModel):
    # Model definition
```

#### After
```python
from zmk_layout.models.base import LayoutBaseModel

class LayoutData(LayoutBaseModel):
    # Model definition
```

### Impact
- Models now inherit from `LayoutBaseModel` instead of `GloveboxBaseModel`
- Serialization methods remain the same (`to_dict()`, `to_json_string()`)
- No changes to field definitions or validation

## API Changes

### Layout Creation

#### Before (Imperative)
```python
layout = Layout()
layout.keyboard = "crkbd"
layout.name = "My Layout"
layout.add_layer("base")
```

#### After (Fluent - Recommended)
```python
layout = Layout.create_empty("crkbd", "My Layout")
layout = layout.layers.add("base").parent()
```

#### Compatibility
The old imperative API is supported through a compatibility wrapper during the transition period.

### Service Integration

#### Before
```python
from glovebox.layout.service import LayoutService

service = LayoutService(profile_service, file_adapter)
result = service.compile(layout_data)
```

#### After
```python
from zmk_layout import Layout
from glovebox.adapters.zmk_layout_providers import create_glovebox_providers

providers = create_glovebox_providers()
layout = Layout.from_dict(layout_data, providers=providers)
result = layout.generate_keymap()
```

## Provider Pattern

### New Requirement
The zmk-layout library requires provider implementations for external dependencies:

```python
from zmk_layout.providers import LayoutProviders

providers = LayoutProviders(
    configuration=config_provider,  # NEW: Required
    template=template_provider,     # NEW: Required
    logger=logger_provider,         # NEW: Required
    # NOTE: FileProvider removed - file I/O delegated to consuming app
)
```

### Migration Path
Glovebox must implement these providers to wrap existing services. See [Provider Implementation Guide](./providers_guide.md) for details.

## Major Architecture Change: File Operations Removed

**Impact**: HIGH - All file I/O operations have been removed from the library core

The zmk-layout library now operates purely on strings and dictionaries, delegating all file operations to the consuming application. This provides better separation of concerns and makes the library more flexible.

### Removed Methods
- `Layout.from_file(file_path)` → Use `Layout.from_dict()` or `Layout.from_string()`
- `Layout.save(file_path)` → Use `layout.to_dict()` or `layout.to_keymap()` + application file I/O
- `Layout.from_keymap(file_path)` → Use `Layout.from_string(content)`
- All `FileProvider` protocol and implementations

### Migration Pattern
```python
# OLD: File operations in library
layout = Layout.from_file("input.json")
layout = layout.layers.add("gaming").parent()
layout.save("output.json")

# NEW: File I/O in application, pure data operations in library
import json
from pathlib import Path

# Load
data = json.loads(Path("input.json").read_text())
layout = Layout.from_dict(data)

# Manipulate (unchanged)
layout = layout.layers.add("gaming").parent()

# Save
Path("output.json").write_text(json.dumps(layout.to_dict()))
# Or save as keymap
Path("output.keymap").write_text(layout.to_keymap())
```

## Removed Features

### 1. Direct Profile Coupling
- **Before**: Layout models directly accessed `KeyboardProfile`
- **After**: Profile data accessed through `ConfigurationProvider`
- **Migration**: Implement `GloveboxConfigurationProvider`

### 2. Service-Specific Methods
- **Before**: `LayoutService.compile_with_profile()`
- **After**: Use providers to inject profile configuration
- **Migration**: Set profile in provider before creating layout

### 3. Internal Utilities
Some internal utilities are no longer exposed:
- `glovebox.layout.internal.*` - Use public API instead
- `glovebox.layout.private.*` - Implement in glovebox if needed

## Deprecated Features

These features are deprecated and will be removed in future versions:

### 1. Imperative API Methods (Deprecated in 0.1.0, removed in 1.0.0)
```python
# Deprecated
layout.add_layer("name")
layout.set_binding(layer, position, binding)
layout.remove_layer("name")

# Use instead
layout = layout.layers.add("name").parent()
layout = layout.layers.get(layer).set(position, binding).parent()
layout = layout.layers.remove("name").parent()
```

### 2. Direct Model Manipulation (Deprecated in 0.1.0)
```python
# Deprecated
layout.layers[0].bindings[0] = "&kp A"

# Use instead
layout = layout.layers.get(0).set(0, "&kp A").parent()
```

### 3. Legacy File Methods (Deprecated in 0.1.0)
```python
# Deprecated
layout.load_from_file(path)
layout.save_to_file(path)

# Use instead
layout = Layout.from_file(path)
layout = layout.save(path)
```

## Behavioral Changes

### 1. Immutability
- **Before**: Layout objects were mutable
- **After**: Fluent API returns new instances (immutable pattern)
- **Impact**: Must capture returned values

```python
# Won't work - original unchanged
layout.with_name("New Name")
print(layout.name)  # Still old name

# Correct - capture new instance
layout = layout.with_name("New Name")
print(layout.name)  # New name
```

### 2. Validation Timing
- **Before**: Validation on save
- **After**: Explicit validation or on terminal operations
- **Impact**: Call `.validate()` explicitly when needed

### 3. Error Messages
- **Before**: Generic error messages
- **After**: Detailed errors with suggestions
- **Impact**: Better debugging, may need to update error handling

## Performance Considerations

### 1. Caching
- **New**: Built-in LRU caching for expensive operations
- **Configuration**: Set cache size via providers
- **Impact**: Better performance for repeated operations

### 2. Lazy Evaluation
- **New**: Operations deferred until terminal methods
- **Impact**: Chain multiple operations efficiently

### 3. Memory Usage
- **Change**: Immutable pattern may use more memory temporarily
- **Mitigation**: Old instances garbage collected quickly

## Migration Checklist

### Phase 1: Preparation
- [ ] Review this document with team
- [ ] Identify all files using layout system
- [ ] Plan migration schedule

### Phase 2: Provider Implementation
- [ ] Implement `ConfigurationProvider`
- [ ] Implement `TemplateProvider`
- [ ] Implement `LayoutLogger`
- [ ] Implement `FileProvider`
- [ ] Test provider validation

### Phase 3: Code Migration
- [ ] Update import statements
- [ ] Replace service calls with zmk-layout API
- [ ] Update model inheritance if extending
- [ ] Add provider configuration

### Phase 4: Testing
- [ ] Run existing tests
- [ ] Add migration tests
- [ ] Performance validation
- [ ] User acceptance testing

### Phase 5: Cleanup
- [ ] Remove deprecated code usage
- [ ] Update documentation
- [ ] Remove compatibility wrappers (after grace period)

## Rollback Plan

If issues arise, use feature flags to control usage:

```python
# In glovebox configuration
USE_ZMK_LAYOUT = os.getenv("USE_ZMK_LAYOUT", "false") == "true"

if USE_ZMK_LAYOUT:
    from zmk_layout import Layout
    # Use zmk-layout
else:
    from glovebox.layout import Layout
    # Use legacy implementation
```

## Timeline

### Transition Period (Glovebox 2.x)
- Both APIs supported
- Deprecation warnings for old API
- Compatibility wrappers available

### Migration Deadline (Glovebox 3.0)
- Legacy API removed
- zmk-layout required
- Compatibility wrappers removed

## Support

### Getting Help
- GitHub Issues: [zmk-layout/issues](https://github.com/CaddyGlow/zmk-layout/issues)
- Migration Support: [Glovebox Integration Guide](./glovebox_integration.md)
- API Documentation: [API Reference](./api/api_reference.md)

### Reporting Issues
When reporting migration issues, include:
1. Glovebox version
2. zmk-layout version
3. Error messages
4. Code snippet showing the issue
5. Migration phase (preparation, implementation, testing)

## FAQ

### Q: Can I use both APIs simultaneously?
**A:** Yes, during the transition period (Glovebox 2.x), both APIs are supported. Use the compatibility wrapper to gradually migrate.

### Q: Will my existing layouts break?
**A:** No, the data format remains the same. Only the code interfacing with layouts needs updating.

### Q: How long is the transition period?
**A:** Glovebox 2.x will support both APIs for at least 6 months after zmk-layout 0.1.0 release.

### Q: Can I extend the new models?
**A:** Yes, inherit from `LayoutBaseModel` and follow the same patterns as before.

### Q: What about custom validators?
**A:** Custom validators can be added via the provider pattern or validation pipeline.

## Summary

The migration to zmk-layout brings:
- **Better API**: Fluent, chainable interface
- **Clean Architecture**: Provider pattern for dependencies
- **Improved Testing**: Easier to mock and test
- **Performance**: Built-in caching and optimization
- **Ecosystem**: Standalone library benefits entire ZMK community

Most breaking changes are mechanical (import paths, method names) rather than fundamental. The transition period allows gradual migration with full backward compatibility support.
