#!/usr/bin/env python3
"""
Debug script to test the full round-trip behavior extraction pipeline.
This tests the actual parsing pipeline that would be used by the round-trip tests.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def debug_roundtrip_behavior_extraction():
    """Test the full parsing pipeline for behavior extraction."""
    print("=== Debug Round-Trip Behavior Extraction ===\n")
    
    # Read the generated keymap
    keymap_file = Path("/tmp/glove80_fluent_output/glove80.keymap")
    keymap_content = keymap_file.read_text()
    
    print(f"✅ Loaded keymap ({len(keymap_content)} chars)")
    
    # Test the full parsing pipeline as used by round-trip tests
    print(f"\n🔍 Testing ZMK keymap parser with FULL mode...")
    
    try:
        from zmk_layout.parsers.zmk_keymap_parser import ZMKKeymapParser, ParsingMode
        
        # Create parser instance
        parser = ZMKKeymapParser()
        
        # Parse using FULL mode (same as round-trip tests)
        result = parser.parse_keymap(
            keymap_content=keymap_content,
            mode=ParsingMode.FULL,
            title="Round-trip Test",
            profile=None  # No profile for round-trip
        )
        
        print(f"   Parse successful: {result.success}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Warnings: {len(result.warnings)}")
        
        if result.errors:
            print("   Parse errors:")
            for error in result.errors[:3]:  # First 3
                print(f"     - {error}")
        
        if result.warnings:
            print("   Parse warnings:")
            for warning in result.warnings[:3]:  # First 3
                print(f"     - {warning}")
        
        if not result.layout_data:
            print("   ❌ No layout data returned")
            return
        
        layout_data = result.layout_data
        print(f"   Layout data created successfully")
        
        # Check behavior fields
        print(f"\n📋 Checking behavior data in layout:")
        print(f"   Layers: {len(layout_data.layers) if layout_data.layers else 0}")
        print(f"   Layer names: {len(layout_data.layer_names) if layout_data.layer_names else 0}")
        print(f"   Hold-taps: {len(layout_data.hold_taps) if layout_data.hold_taps else 0}")
        print(f"   Macros: {len(layout_data.macros) if layout_data.macros else 0}")
        print(f"   Combos: {len(layout_data.combos) if layout_data.combos else 0}")
        print(f"   Tap-dances: {len(layout_data.tap_dances) if layout_data.tap_dances else 0}")
        
        # Show specific behaviors if found
        if layout_data.hold_taps:
            print(f"\n   Hold-tap details:")
            for i, ht in enumerate(layout_data.hold_taps[:5]):  # First 5
                print(f"     {i}: {ht.name if hasattr(ht, 'name') else 'unnamed'}")
        
        if layout_data.macros:
            print(f"\n   Macro details:")
            for i, macro in enumerate(layout_data.macros[:5]):  # First 5
                print(f"     {i}: {macro.name if hasattr(macro, 'name') else 'unnamed'}")
                
        if layout_data.combos:
            print(f"\n   Combo details:")
            for i, combo in enumerate(layout_data.combos[:5]):  # First 5
                print(f"     {i}: {combo.name if hasattr(combo, 'name') else 'unnamed'}")
                
        if layout_data.tap_dances:
            print(f"\n   Tap-dance details:")
            for i, td in enumerate(layout_data.tap_dances[:5]):  # First 5
                print(f"     {i}: {td.name if hasattr(td, 'name') else 'unnamed'}")
        
        # Test the behavior manager
        print(f"\n🔍 Testing behavior manager...")
        from zmk_layout.core.managers import BehaviorManager
        
        behavior_manager = BehaviorManager(layout_data)
        print(f"   Total behavior count: {behavior_manager.total_count}")
        print(f"   Hold-tap count: {behavior_manager.hold_tap_count}")
        print(f"   Macro count: {behavior_manager.macro_count}")
        print(f"   Combo count: {behavior_manager.combo_count}")
        print(f"   Tap-dance count: {behavior_manager.tap_dance_count}")
        
        # Final summary
        behavior_counts = (
            len(layout_data.hold_taps or []) +
            len(layout_data.macros or []) +
            len(layout_data.combos or []) +
            len(layout_data.tap_dances or [])
        )
        print(f"\n✅ Round-trip behavior extraction summary:")
        print(f"   Total behaviors in layout_data: {behavior_counts}")
        print(f"   Expected behaviors from AST test: 24 (11 hold-taps + 5 macros + 3 combos + 5 tap-dances)")
        
        if behavior_counts > 0:
            print(f"   🎉 SUCCESS: Behavior extraction is working in the parsing pipeline!")
        else:
            print(f"   ❌ ISSUE: No behaviors extracted by the parsing pipeline")
            
            # Debug what went wrong
            print(f"\n🔍 Debugging missing behaviors...")
            
            # Check if AST parsing worked
            from zmk_layout.parsers.dt_parser import parse_dt_multiple_safe
            roots, parse_errors = parse_dt_multiple_safe(keymap_content)
            print(f"   Direct AST parsing: {len(roots)} roots, {len(parse_errors)} errors")
            
            if roots:
                from zmk_layout.parsers.ast_walker import UniversalBehaviorExtractor
                extractor = UniversalBehaviorExtractor()
                behavior_nodes = extractor.extract_all_behaviors_multiple(roots)
                
                direct_count = sum(len(nodes) for nodes in behavior_nodes.values())
                print(f"   Direct behavior extraction: {direct_count} behaviors")
                
                if direct_count > 0 and behavior_counts == 0:
                    print("   🔍 AST extraction works but pipeline doesn't - conversion issue")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_roundtrip_behavior_extraction()