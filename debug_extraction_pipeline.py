#!/usr/bin/env python3
"""
Debug script to trace the complete behavior extraction pipeline.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from zmk_layout.parsers.zmk_keymap_parser import ZMKKeymapParser, ParsingMode
from zmk_layout.parsers.keymap_processors import create_section_extractor
from zmk_layout.providers.factory import create_default_providers

def debug_extraction_pipeline():
    """Debug the complete behavior extraction pipeline step by step."""
    print("=== Debugging Extraction Pipeline ===\n")
    
    # Read the generated keymap
    keymap_file = Path("/tmp/glove80_fluent_output/glove80.keymap")
    keymap_content = keymap_file.read_text()
    
    print(f"✅ Loaded keymap ({len(keymap_content)} chars)")
    
    # Step 1: Parse AST
    print(f"\n🔍 Step 1: Parse AST")
    try:
        from zmk_layout.parsers.dt_parser import parse_dt_multiple_safe
        roots, parse_errors = parse_dt_multiple_safe(keymap_content)
        print(f"   AST roots: {len(roots)}")
        print(f"   Parse errors: {len(parse_errors)}")
    except Exception as e:
        print(f"   ❌ AST parsing failed: {e}")
        return
    
    # Step 2: Extract behaviors directly
    print(f"\n🔍 Step 2: Direct behavior extraction")
    try:
        section_extractor = create_section_extractor()
        behavior_models = section_extractor.behavior_extractor.extract_behaviors_as_models(
            roots, keymap_content, {}
        )
        print(f"   Behavior models keys: {list(behavior_models.keys())}")
        for key, value in behavior_models.items():
            if value and len(value) > 0:
                print(f"     {key}: {len(value)} items")
                # Show first item if it exists
                if hasattr(value[0], 'name'):
                    print(f"       First item: {value[0].name}")
                else:
                    print(f"       First item: {type(value[0])}")
            else:
                print(f"     {key}: empty or None")
    except Exception as e:
        print(f"   ❌ Direct extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Check what happens during full parsing
    print(f"\n🔍 Step 3: Full parsing with detailed inspection")
    try:
        providers = create_default_providers()
        parser = ZMKKeymapParser(
            configuration_provider=providers.configuration,
            logger=providers.logger
        )
        
        # Get the full keymap processor directly
        from zmk_layout.parsers.keymap_processors import create_full_keymap_processor
        full_processor = create_full_keymap_processor()
        
        # Create parsing context
        from zmk_layout.parsers.zmk_keymap_parser import ParsingContext
        context = ParsingContext(
            keymap_content=keymap_content,
            title="Debug Layout",
            keyboard_name="glove80",
            extraction_config={}
        )
        
        # Process with full processor
        layout_data = full_processor.process(context)
        
        if layout_data:
            print(f"   ✅ Layout data created")
            print(f"   hold_taps: {len(layout_data.hold_taps) if layout_data.hold_taps else 0}")
            print(f"   combos: {len(layout_data.combos) if layout_data.combos else 0}")
            print(f"   macros: {len(layout_data.macros) if layout_data.macros else 0}")
            print(f"   tap_dances: {len(layout_data.tap_dances) if layout_data.tap_dances else 0}")
            
            # Let's inspect the actual objects
            if layout_data.hold_taps:
                for i, ht in enumerate(layout_data.hold_taps[:2]):
                    print(f"     HT {i}: {ht}")
                    
            if layout_data.combos:
                for i, combo in enumerate(layout_data.combos[:2]):
                    print(f"     Combo {i}: {combo}")
        else:
            print(f"   ❌ No layout data returned")
            
        print(f"   Context errors: {len(context.errors)}")
        print(f"   Context warnings: {len(context.warnings)}")
        
    except Exception as e:
        print(f"   ❌ Full parsing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_extraction_pipeline()