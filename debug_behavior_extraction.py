#!/usr/bin/env python3
"""
Debug script to trace behavior extraction during parsing.
This will help us understand why behaviors aren't being found in the round-trip test.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from zmk_layout.parsers.zmk_keymap_parser import ZMKKeymapParser, ParsingMode
from zmk_layout.providers.factory import create_default_providers

def debug_behavior_extraction():
    """Debug behavior extraction from generated keymap."""
    print("=== Debugging Behavior Extraction ===\n")
    
    # Read the generated keymap
    keymap_file = Path("/tmp/glove80_fluent_output/glove80.keymap")
    if not keymap_file.exists():
        print(f"❌ Keymap file not found: {keymap_file}")
        return
    
    keymap_content = keymap_file.read_text()
    print(f"✅ Loaded keymap file: {keymap_file}")
    print(f"   Content length: {len(keymap_content)} characters")
    print(f"   Lines: {keymap_content.count(chr(10))}")
    print()
    
    # Create parser with debug logging
    providers = create_default_providers()
    parser = ZMKKeymapParser(
        configuration_provider=providers.configuration,
        logger=providers.logger
    )
    
    print("🔍 Parsing keymap with FULL mode...")
    
    # Parse with full mode
    parse_result = parser.parse_keymap(
        keymap_content, 
        title="Debug Glove80 Layout",
        mode=ParsingMode.FULL
    )
    
    print(f"✅ Parse result success: {parse_result.success}")
    print(f"   Parsing mode: {parse_result.parsing_mode}")
    print(f"   Errors: {len(parse_result.errors)}")
    print(f"   Warnings: {len(parse_result.warnings)}")
    
    if parse_result.errors:
        print("❌ Errors:")
        for error in parse_result.errors:
            print(f"   - {error}")
    
    if parse_result.warnings:
        print("⚠️  Warnings:")
        for warning in parse_result.warnings:
            print(f"   - {warning}")
    
    if not parse_result.layout_data:
        print("❌ No layout data returned")
        return
    
    layout_data = parse_result.layout_data
    print(f"\n✅ Layout data extracted:")
    print(f"   Keyboard: {layout_data.keyboard}")
    print(f"   Title: {layout_data.title}")
    print(f"   Layers: {len(layout_data.layers) if layout_data.layers else 0}")
    print(f"   Layer names: {layout_data.layer_names}")
    
    # Check behaviors
    behaviors_found = []
    if hasattr(layout_data, 'behaviors') and layout_data.behaviors:
        for behavior in layout_data.behaviors:
            behaviors_found.append(behavior.name)
    
    print(f"   Behaviors found: {len(behaviors_found)}")
    if behaviors_found:
        print(f"   Behavior names: {behaviors_found}")
    else:
        print("   ❌ No behaviors found!")
    
    # Check combos
    combos_found = []
    if hasattr(layout_data, 'combos') and layout_data.combos:
        for combo in layout_data.combos:
            combos_found.append(combo.name)
    
    print(f"   Combos found: {len(combos_found)}")
    if combos_found:
        print(f"   Combo names: {combos_found}")
    else:
        print("   ❌ No combos found!")
    
    # Let's manually check what's in the keymap content
    print(f"\n🔍 Manual content analysis:")
    
    # Look for behavior sections
    behavior_sections = []
    lines = keymap_content.split('\n')
    in_behavior_section = False
    current_behavior = []
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Look for behavior definitions
        if 'behaviors {' in stripped:
            in_behavior_section = True
            print(f"   Found behaviors section at line {i}: {stripped}")
            continue
            
        if in_behavior_section:
            if stripped.startswith('}'):
                in_behavior_section = False
                if current_behavior:
                    behavior_sections.append('\n'.join(current_behavior))
                    current_behavior = []
            else:
                current_behavior.append(line)
        
        # Look for individual behavior definitions
        if any(pattern in stripped for pattern in ['hold-tap', 'tap-dance', 'macro']):
            print(f"   Found behavior pattern at line {i}: {stripped}")
            
        # Look for combo section
        if 'combos {' in stripped:
            print(f"   Found combos section at line {i}: {stripped}")
    
    print(f"   Total behavior sections found: {len(behavior_sections)}")
    
    # Let's also check if the AST parsing is working
    print(f"\n🔍 Debugging AST parsing...")
    
    try:
        from zmk_layout.parsers.dt_parser import parse_dt_multiple_safe
        roots, parse_errors = parse_dt_multiple_safe(keymap_content)
        
        print(f"   AST roots parsed: {len(roots)}")
        print(f"   Parse errors: {len(parse_errors)}")
        
        if parse_errors:
            for error in parse_errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
        
        # Check what's in the AST
        for i, root in enumerate(roots[:3]):  # Check first 3 roots
            print(f"   Root {i}: type={root.name if hasattr(root, 'name') else type(root)}")
            if hasattr(root, 'children') and root.children:
                print(f"     Children: {len(root.children)}")
                for j, child in enumerate(root.children[:5]):  # First 5 children
                    child_name = child.name if hasattr(child, 'name') else str(child)
                    print(f"       Child {j}: {child_name}")
                    
    except Exception as e:
        print(f"   ❌ AST parsing failed: {e}")
    
    print(f"\n🔍 Let's also check the behavior extractor directly...")
    
    try:
        from zmk_layout.parsers.keymap_processors import create_section_extractor
        section_extractor = create_section_extractor()
        
        if hasattr(section_extractor, 'behavior_extractor'):
            print(f"   Section extractor created successfully")
            print(f"   Has behavior_extractor: {hasattr(section_extractor, 'behavior_extractor')}")
            
            # Try to extract behaviors directly
            if roots:
                behavior_models = section_extractor.behavior_extractor.extract_behaviors_as_models(
                    roots, keymap_content, {}
                )
                print(f"   Direct behavior extraction returned: {len(behavior_models)} behaviors")
                if behavior_models:
                    print(f"   Behavior keys: {list(behavior_models.keys())}")
            
    except Exception as e:
        print(f"   ❌ Direct behavior extraction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_behavior_extraction()