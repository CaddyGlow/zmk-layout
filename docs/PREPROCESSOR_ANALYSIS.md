# ZMK Layout Library - Preprocessor Analysis

## Executive Summary

This document analyzes the current state and future options for handling C preprocessor directives in the ZMK layout library's parsing system. The analysis covers the gap between current capabilities and full preprocessor support, evaluates different implementation approaches, and provides recommendations for moving forward.

## Current State Analysis

### Existing Capabilities

#### 1. Variable Definitions (`#define`)
- **Status**: ✅ Partially Implemented
- **Current Behavior**:
  - Extracted from AST into `context.defines` dictionary
  - Simple key-value substitution supported
  - Passed through the parsing pipeline
  - Resolved when tokens match define names

```python
# Current implementation in keymap_processors.py
def _extract_defines_from_ast(self, roots: list[DTNode]) -> dict[str, str]:
    defines = {}
    for root in roots:
        for conditional in root.conditionals:
            if conditional.directive == "define":
                parts = conditional.condition.split(None, 1)
                if len(parts) >= 2:
                    defines[parts[0]] = parts[1]
    return defines
```

#### 2. Conditional Directives
- **Status**: ⚠️ Recognized but Not Evaluated
- **Current Behavior**:
  - Recognized as TokenType.PREPROCESSOR tokens
  - Stored in DTNode.conditionals list
  - Preserved as comments
  - NOT used for conditional compilation

```python
# Current structure in ast_nodes.py
@dataclass
class DTConditional:
    directive: str  # ifdef, ifndef, else, endif
    condition: str = ""
    line: int = 0
    column: int = 0
```

### Critical Gaps

1. **No Conditional Compilation Evaluation**
   ```c
   #ifdef CONFIG_ZMK_SPLIT
       // Content is always parsed, never conditionally excluded
   #endif
   ```

2. **No Expression Evaluation**
   ```c
   #define BASE_LAYER 0
   #define LOWER_LAYER (BASE_LAYER + 1)  // Not evaluated, stored as literal
   ```

3. **No Nested Variable Resolution**
   ```c
   #define KEY_A A
   #define KEY_B KEY_A  // Won't resolve to 'A'
   ```

4. **No Include Processing**
   ```c
   #include <dt-bindings/zmk/keys.h>  // Recognized but not processed
   ```

## Implementation Options Analysis

### Option 1: Enhanced Variable Resolution (Minimal)

**Scope**: Extend current system with better variable handling

**Features**:
- Multi-level define resolution
- Simple arithmetic expressions
- Basic function-like macros

**Effort**: 3-5 days

**Pros**:
- Minimal changes to existing code
- Maintains current architecture
- Quick to implement

**Cons**:
- Still no conditional compilation
- Limited macro support
- Won't handle complex keymaps

### Option 2: Limited Preprocessor (Pragmatic)

**Scope**: ZMK-specific preprocessor features only

**Features**:
- Simple `#define` substitution
- Basic `#ifdef`/`#ifndef` evaluation
- Include file support (limited)
- Simple expression evaluation

**Effort**: 1-2 weeks

**Implementation Approach**:
```python
class LimitedPreprocessor:
    def __init__(self):
        self.defines = {}
        self.active_conditions = []
    
    def process(self, content: str) -> str:
        # Two-pass system:
        # 1. Extract all defines and includes
        # 2. Evaluate conditions and apply substitutions
        pass
```

**Pros**:
- Covers 90% of ZMK use cases
- Maintainable codebase
- No external dependencies

**Cons**:
- Not fully C-compliant
- Complex macros unsupported
- Edge cases may fail

### Option 3: Full C Preprocessor (Complete)

**Scope**: Complete C preprocessor implementation

**Features**:
- All C preprocessor directives
- Full macro system (object-like, function-like, variadic)
- Complete expression evaluation
- Token pasting and stringification
- Include system with paths

**Effort**: 9-14 weeks

**Components Required**:
1. Enhanced Tokenizer (2-3 days)
2. Macro System (3-5 days)
3. Expression Evaluator (2-3 days)
4. Conditional Compilation (2-3 days)
5. Include System (2-3 days)
6. Built-in Macros (1 day)
7. Pragma Handling (1-2 days)

**Pros**:
- Full C compliance
- Handles any valid preprocessor code
- Future-proof

**Cons**:
- Massive implementation effort
- High maintenance burden
- Overkill for ZMK keymaps
- Complex edge cases

### Option 4: External Preprocessor Integration (pcpp)

**Scope**: Use existing Python C preprocessor library

**Three Integration Approaches**:

#### 4.1 Full Preprocessing Before Parsing
```python
def parse_with_full_preprocessing(content: str):
    cpp = Preprocessor()
    cpp.parse(content)
    preprocessed = cpp.write()
    return parse_dt_multiple(preprocessed)
```

#### 4.2 Hybrid Preprocessing (Recommended)
```python
class HybridPreprocessor:
    def process(self, content: str):
        # Extract directives
        # Process with pcpp
        # Apply selectively
        # Preserve structure
        pass
```

#### 4.3 On-Demand During Parsing
```python
class PreprocessingParser:
    def parse_value(self, value: str):
        if self.contains_macro(value):
            return self.cpp.expand_macros(value)
        return value
```

**Effort**: 3-5 days for integration

**Pros**:
- Battle-tested implementation
- Full C compliance
- Quick to integrate
- Maintained by others

**Cons**:
- External dependency
- May strip comments
- Line number mapping issues
- Less control over behavior

## Recommendation

### Immediate Term (1 week)
Implement **Enhanced Variable Resolution** to improve current functionality:
- Multi-level define resolution
- Simple arithmetic in defines
- Better error reporting

### Short Term (2-3 weeks)
Add **Limited Preprocessor** features:
- Basic `#ifdef`/`#ifndef` evaluation
- Simple conditional compilation
- Include file support for common headers

### Long Term (Optional)
Integrate **pcpp with Hybrid Approach** if users need:
- Complex macro systems
- Full C preprocessor compliance
- Advanced conditional compilation

### Why This Approach?

1. **Incremental Value**: Each phase delivers immediate improvements
2. **Risk Mitigation**: Can stop at any phase if sufficient
3. **Maintainability**: Keeps codebase manageable
4. **User-Focused**: Based on actual ZMK keymap needs

## Implementation Roadmap

### Phase 1: Enhanced Variable Resolution
```python
class EnhancedDefineResolver:
    def __init__(self, defines: dict):
        self.defines = defines
        self.resolved_cache = {}
    
    def resolve(self, token: str, depth=0) -> str:
        # Recursive resolution with cycle detection
        if depth > 10:
            return token
        
        if token in self.resolved_cache:
            return self.resolved_cache[token]
        
        value = self.defines.get(token, token)
        if value != token and value in self.defines:
            value = self.resolve(value, depth + 1)
        
        self.resolved_cache[token] = value
        return value
    
    def evaluate_simple_expr(self, expr: str) -> str:
        # Handle basic arithmetic: +, -, *, /, ()
        # Example: (BASE_LAYER + 1) where BASE_LAYER = 0
        pass
```

### Phase 2: Conditional Evaluation
```python
class ConditionalEvaluator:
    def __init__(self, defines: dict):
        self.defines = defines
        self.condition_stack = []
        self.skip_depth = 0
    
    def process_directive(self, directive: str, condition: str):
        if directive == "ifdef":
            is_defined = condition in self.defines
            self.condition_stack.append(is_defined)
            if not is_defined:
                self.skip_depth += 1
        elif directive == "ifndef":
            is_defined = condition not in self.defines
            self.condition_stack.append(is_defined)
            if not is_defined:
                self.skip_depth += 1
        elif directive == "else":
            # Flip current condition
            pass
        elif directive == "endif":
            # Pop condition stack
            pass
    
    def should_include_content(self) -> bool:
        return self.skip_depth == 0
```

### Phase 3: Hybrid pcpp Integration
```python
class ZMKHybridPreprocessor:
    """
    Selective preprocessing that preserves structure
    while leveraging pcpp for complex operations.
    """
    
    def __init__(self):
        self.cpp = Preprocessor()
        self.preserve_structure = True
    
    def preprocess_for_parsing(self, content: str) -> tuple[str, dict]:
        # 1. Extract preprocessing directives
        directives = self.extract_directives(content)
        
        # 2. Process includes and complex defines with pcpp
        self.process_includes(directives['includes'])
        resolved_defines = self.process_defines(directives['defines'])
        
        # 3. Apply conditional compilation
        processed = self.apply_conditionals(content, resolved_defines)
        
        # 4. Return processed content with define context
        return processed, resolved_defines
    
    def extract_directives(self, content: str) -> dict:
        """Extract all preprocessing directives while preserving content"""
        pass
    
    def apply_conditionals(self, content: str, defines: dict) -> str:
        """
        Apply conditional compilation while preserving excluded
        content as comments for debugging/reference.
        """
        pass
```

## Testing Strategy

### Unit Tests Required

```python
# Basic Variable Resolution
def test_simple_define_substitution()
def test_nested_define_resolution()
def test_circular_define_detection()
def test_arithmetic_expression_evaluation()

# Conditional Compilation
def test_ifdef_inclusion()
def test_ifndef_exclusion()
def test_nested_conditionals()
def test_else_clause_handling()

# Integration Tests
def test_real_zmk_keymap_processing()
def test_template_preservation()
def test_error_handling_and_recovery()

# Regression Tests
def test_existing_keymap_compatibility()
def test_performance_benchmarks()
```

### Test Coverage Goals
- 90% code coverage for preprocessor modules
- 100% coverage for critical paths (define resolution, conditionals)
- Real-world keymap test suite
- Performance regression tests

## Performance Considerations

### Current Performance
- Parse time for typical keymap: ~50-100ms
- Memory usage: ~10-20MB

### Target Performance
- With enhanced resolution: <150ms parse time
- With limited preprocessor: <200ms parse time
- With pcpp integration: <300ms parse time
- Memory usage: <50MB

### Optimization Strategies
1. Cache resolved defines
2. Lazy evaluation of conditionals
3. Incremental preprocessing
4. Parallel processing for includes

## Risk Analysis

### Technical Risks
1. **Complexity Creep**: Preprocessor grows beyond intended scope
   - Mitigation: Strict feature boundaries, phased implementation

2. **Performance Degradation**: Preprocessing slows parsing significantly
   - Mitigation: Benchmarking, caching, optimization passes

3. **Compatibility Issues**: Changes break existing keymaps
   - Mitigation: Comprehensive test suite, backward compatibility mode

### Project Risks
1. **Scope Creep**: Full C preprocessor becomes "required"
   - Mitigation: Clear documentation of limitations, user education

2. **Maintenance Burden**: Complex preprocessor hard to maintain
   - Mitigation: Start simple, use external libraries where possible

## Conclusion

The ZMK layout library can significantly improve its preprocessor handling through a phased approach:

1. **Immediate**: Enhance current define resolution (1 week)
2. **Short-term**: Add basic conditional compilation (2-3 weeks)
3. **Long-term**: Consider pcpp integration for full compliance (optional)

This approach balances user needs with implementation complexity, providing value at each phase while avoiding the pitfall of building an overly complex system that's hard to maintain.

The recommended hybrid approach with selective preprocessing preserves the template-friendly structure of the current system while adding the preprocessor capabilities users need for real-world ZMK keymaps.

## Appendix: Decision Matrix

| Feature | Current | Enhanced | Limited | Full | pcpp |
|---------|---------|----------|---------|------|------|
| Simple defines | ✅ | ✅ | ✅ | ✅ | ✅ |
| Nested defines | ❌ | ✅ | ✅ | ✅ | ✅ |
| Arithmetic | ❌ | ⚠️ | ✅ | ✅ | ✅ |
| ifdef/ifndef | ❌ | ❌ | ✅ | ✅ | ✅ |
| Complex macros | ❌ | ❌ | ❌ | ✅ | ✅ |
| Includes | ❌ | ❌ | ⚠️ | ✅ | ✅ |
| **Effort (weeks)** | 0 | 1 | 2-3 | 9-14 | 1 |
| **Maintenance** | Low | Low | Medium | High | Low |
| **Dependencies** | None | None | None | None | pcpp |

Legend: ✅ Full support, ⚠️ Partial support, ❌ No support