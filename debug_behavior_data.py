#!/usr/bin/env python3
"""
Debug script to inspect the actual behavior data in parsed layout.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from zmk_layout import Layout

def debug_behavior_data():
    """Debug the actual behavior data in parsed layout."""
    print("=== Debugging Behavior Data ===\n")
    
    # Read the generated keymap
    keymap_file = Path("/tmp/glove80_fluent_output/glove80.keymap")
    if not keymap_file.exists():
        print(f"❌ Keymap file not found: {keymap_file}")
        return
    
    keymap_content = keymap_file.read_text()
    print(f"✅ Loading keymap from: {keymap_file}")
    
    # Create layout from string (this calls the parser internally)
    loaded_layout = Layout.from_string(keymap_content, title="Debug Layout")
    
    print(f"✅ Layout loaded successfully")
    
    # Access the internal data directly
    data = loaded_layout._data
    
    print(f"\n🔍 Direct data inspection:")
    print(f"   data.hold_taps: {data.hold_taps}")
    print(f"   data.combos: {data.combos}")  
    print(f"   data.macros: {data.macros}")
    print(f"   data.tap_dances: {data.tap_dances}")
    
    if data.hold_taps:
        print(f"   Hold taps count: {len(data.hold_taps)}")
        for i, ht in enumerate(data.hold_taps[:3]):  # First 3
            print(f"     HT {i}: {ht.name} - {ht}")
    else:
        print(f"   ❌ No hold_taps in data")
    
    if data.combos:
        print(f"   Combos count: {len(data.combos)}")
        for i, combo in enumerate(data.combos[:3]):  # First 3
            print(f"     Combo {i}: {combo.name} - {combo}")
    else:
        print(f"   ❌ No combos in data")
    
    if data.macros:
        print(f"   Macros count: {len(data.macros)}")
        for i, macro in enumerate(data.macros[:3]):  # First 3
            print(f"     Macro {i}: {macro.name} - {macro}")
    else:
        print(f"   ❌ No macros in data")
    
    if data.tap_dances:
        print(f"   Tap dances count: {len(data.tap_dances)}")
        for i, td in enumerate(data.tap_dances[:3]):  # First 3
            print(f"     TD {i}: {td.name} - {td}")
    else:
        print(f"   ❌ No tap_dances in data")
    
    # Check behavior manager
    behavior_manager = loaded_layout._behaviors
    print(f"\n🔍 Behavior manager inspection:")
    print(f"   hold_tap_count: {behavior_manager.hold_tap_count}")
    print(f"   combo_count: {behavior_manager.combo_count}")
    print(f"   macro_count: {behavior_manager.macro_count}")
    print(f"   tap_dance_count: {behavior_manager.tap_dance_count}")
    print(f"   total_count: {behavior_manager.total_count}")
    
    # Check statistics
    stats = loaded_layout.get_statistics()
    print(f"\n🔍 Statistics:")
    print(f"   total_behaviors: {stats['total_behaviors']}")
    print(f"   behavior_counts: {stats['behavior_counts']}")
    
    return loaded_layout

if __name__ == "__main__":
    debug_behavior_data()