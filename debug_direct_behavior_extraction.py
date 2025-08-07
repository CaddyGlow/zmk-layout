#!/usr/bin/env python3
"""
Debug script to test behavior extraction directly from AST nodes.
This will help us understand if the issue is in the extraction logic or elsewhere.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def debug_direct_behavior_extraction():
    """Test behavior extraction directly from AST nodes."""
    print("=== Debug Direct Behavior Extraction ===\n")
    
    # Read the generated keymap
    keymap_file = Path("/tmp/glove80_fluent_output/glove80.keymap")
    keymap_content = keymap_file.read_text()
    
    print(f"✅ Loaded keymap ({len(keymap_content)} chars)")
    
    # Parse AST with detailed error reporting
    print(f"\n🔍 Parsing AST...")
    try:
        from zmk_layout.parsers.dt_parser import parse_dt_multiple_safe
        roots, parse_errors = parse_dt_multiple_safe(keymap_content)
        
        print(f"   AST roots: {len(roots)}")
        print(f"   Parse errors: {len(parse_errors)}")
        
        if parse_errors:
            print(f"\n❌ Parse errors prevent behavior extraction:")
            for i, error in enumerate(parse_errors[:3]):  # First 3 errors
                print(f"   Error {i}: {error}")
            return
            
        # Now test direct behavior extraction
        print(f"\n🔍 Testing direct UniversalBehaviorExtractor...")
        from zmk_layout.parsers.ast_walker import UniversalBehaviorExtractor
        
        extractor = UniversalBehaviorExtractor()
        behavior_nodes = extractor.extract_all_behaviors_multiple(roots)
        
        print(f"   Extracted behaviors:")
        for behavior_type, nodes in behavior_nodes.items():
            if nodes:
                print(f"     {behavior_type}: {len(nodes)}")
                # Show first few node names
                for i, node in enumerate(nodes[:3]):
                    print(f"       Node {i}: {node.name if hasattr(node, 'name') else 'unnamed'}")
        
        # Test with individual extractors
        print(f"\n🔍 Testing individual extractors...")
        
        # Test HoldTapExtractor
        from zmk_layout.parsers.ast_walker import HoldTapExtractor
        hold_tap_extractor = HoldTapExtractor()
        
        for root in roots:
            hold_taps = hold_tap_extractor.extract_hold_taps(root)
            if hold_taps:
                print(f"   HoldTapExtractor found {len(hold_taps)} hold-taps in root")
                for ht in hold_taps[:3]:
                    print(f"     Hold-tap: {ht.name}")
        
        # Test MacroExtractor
        from zmk_layout.parsers.ast_walker import MacroExtractor
        macro_extractor = MacroExtractor()
        
        for root in roots:
            macros = macro_extractor.extract_macros(root)
            if macros:
                print(f"   MacroExtractor found {len(macros)} macros in root")
                for macro in macros[:3]:
                    print(f"     Macro: {macro.name}")
        
        # Test ComboExtractor  
        from zmk_layout.parsers.ast_walker import ComboExtractor
        combo_extractor = ComboExtractor()
        
        for root in roots:
            combos = combo_extractor.extract_combos(root)
            if combos:
                print(f"   ComboExtractor found {len(combos)} combos in root")
                for combo in combos[:3]:
                    print(f"     Combo: {combo.name}")
        
        # Manual inspection of AST for behavior nodes
        print(f"\n🔍 Manual inspection of AST for behavior-related nodes...")
        
        from zmk_layout.parsers.ast_walker import DTMultiWalker
        multi_walker = DTMultiWalker(roots)
        
        # Look for nodes with compatible properties
        compatible_nodes = multi_walker.find_properties_by_name("compatible")
        behavior_compatible_nodes = []
        
        for node, prop in compatible_nodes:
            if prop.value and isinstance(prop.value.value, str):
                compatible_value = prop.value.value
                if "zmk,behavior" in compatible_value:
                    behavior_compatible_nodes.append((node, compatible_value))
        
        print(f"   Found {len(behavior_compatible_nodes)} nodes with behavior compatible:")
        for i, (node, compatible) in enumerate(behavior_compatible_nodes[:10]):  # First 10
            print(f"     Node {i}: {node.name} - {compatible}")
        
        # Look for behavior sections
        behaviors_sections = multi_walker.find_nodes_by_name("behaviors")
        print(f"\n   Found {len(behaviors_sections)} 'behaviors' sections:")
        for i, section in enumerate(behaviors_sections):
            print(f"     Section {i}: {len(section.children)} children")
            for child_name, child in list(section.children.items())[:5]:  # First 5
                compatible_prop = child.get_property("compatible")
                compatible_str = ""
                if compatible_prop and compatible_prop.value:
                    compatible_str = f" ({compatible_prop.value.value})"
                print(f"       Child: {child_name}{compatible_str}")
        
        # Look for macro sections
        macros_sections = multi_walker.find_nodes_by_name("macros")
        print(f"\n   Found {len(macros_sections)} 'macros' sections:")
        for i, section in enumerate(macros_sections):
            print(f"     Section {i}: {len(section.children)} children")
            for child_name, child in list(section.children.items())[:5]:  # First 5
                compatible_prop = child.get_property("compatible")
                compatible_str = ""
                if compatible_prop and compatible_prop.value:
                    compatible_str = f" ({compatible_prop.value.value})"
                print(f"       Child: {child_name}{compatible_str}")
        
        # Look for combo sections
        combos_sections = multi_walker.find_nodes_by_name("combos")
        print(f"\n   Found {len(combos_sections)} 'combos' sections:")
        for i, section in enumerate(combos_sections):
            print(f"     Section {i}: {len(section.children)} children")
            for child_name, child in list(section.children.items())[:5]:  # First 5
                key_positions_prop = child.get_property("key-positions")
                bindings_prop = child.get_property("bindings")
                props_str = f"key-positions={key_positions_prop is not None}, bindings={bindings_prop is not None}"
                print(f"       Child: {child_name} ({props_str})")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_direct_behavior_extraction()