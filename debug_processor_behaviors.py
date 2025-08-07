#!/usr/bin/env python3
"""
Debug script to trace behavior extraction in the keymap processor.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def debug_processor_behaviors():
    """Debug behavior extraction in the keymap processor."""
    print("=== Debug Processor Behavior Extraction ===\n")
    
    # Read the generated keymap
    keymap_file = Path("/tmp/glove80_fluent_output/glove80.keymap")
    keymap_content = keymap_file.read_text()
    
    print(f"✅ Loaded keymap ({len(keymap_content)} chars)")
    
    print(f"\n🔍 Testing processor behavior extraction pipeline...")
    try:
        from zmk_layout.parsers.keymap_processors import create_full_keymap_processor
        from zmk_layout.parsers.parsing_models import ParsingContext
        
        # Create processor
        processor = create_full_keymap_processor()
        print(f"   ✅ Created processor: {type(processor).__name__}")
        print(f"   Section extractor: {type(processor.section_extractor).__name__}")
        print(f"   Behavior extractor: {type(processor.section_extractor.behavior_extractor).__name__}")
        
        # Create context
        context = ParsingContext(
            keymap_content=keymap_content,
            title="Debug Test",
            keyboard_name="glove80"
        )
        
        # Let's manually trace through the process steps
        print(f"\n🔍 Step 1: Transform behavior references...")
        transformed_content = processor._transform_behavior_references_to_definitions(keymap_content)
        print(f"   Transformation completed: {len(transformed_content)} chars")
        
        print(f"\n🔍 Step 2: Parse AST...")
        from zmk_layout.parsers.dt_parser import parse_dt_multiple_safe
        roots, parse_errors = parse_dt_multiple_safe(transformed_content)
        print(f"   AST roots: {len(roots)}, errors: {len(parse_errors)}")
        
        if parse_errors:
            print(f"   Parse errors:")
            for error in parse_errors[:3]:
                print(f"     - {error}")
        
        print(f"\n🔍 Step 3: Extract defines...")
        defines = processor._extract_defines_from_ast(roots)
        print(f"   Defines extracted: {len(defines)}")
        
        print(f"\n🔍 Step 4: Extract behaviors and metadata...")
        try:
            behaviors_dict = processor._extract_behaviors_and_metadata(
                roots, transformed_content, defines
            )
            print(f"   Behaviors dict keys: {list(behaviors_dict.keys())}")
            
            behavior_counts = {k: len(v) for k, v in behaviors_dict.items() if v}
            print(f"   Behavior counts: {behavior_counts}")
            
            total_behaviors = sum(len(v) for v in behaviors_dict.values() if v)
            print(f"   Total behaviors extracted: {total_behaviors}")
            
            if total_behaviors == 0:
                print(f"   ❌ No behaviors extracted in processor pipeline!")
                
                # Debug the section extractor directly
                print(f"\n🔍 Step 4a: Debug section extractor directly...")
                try:
                    # Try calling the behavior extractor directly with correct parameters
                    behavior_models = processor.section_extractor.behavior_extractor.extract_behaviors_as_models(
                        roots=roots,
                        source_content=transformed_content,
                        defines=defines
                    )
                    
                    direct_counts = {k: len(v) for k, v in behavior_models.items() if v}
                    print(f"   Direct behavior extraction: {direct_counts}")
                    
                    if sum(len(v) for v in behavior_models.values()) == 0:
                        print(f"   ❌ Even direct extraction returns 0 - extractor issue")
                    else:
                        print(f"   ✅ Direct extraction works - pipeline bug")
                        
                except Exception as e:
                    print(f"   ❌ Direct extraction failed: {e}")
                    
                    # Try without source_content
                    try:
                        print(f"   Trying without source_content parameter...")
                        behavior_models = processor.section_extractor.behavior_extractor.extract_behaviors_as_models(
                            roots=roots,
                            defines=defines
                        )
                        
                        direct_counts = {k: len(v) for k, v in behavior_models.items() if v}
                        print(f"   Direct behavior extraction (no source_content): {direct_counts}")
                        
                    except Exception as e2:
                        print(f"   ❌ Direct extraction without source_content failed: {e2}")
            
        except Exception as e:
            print(f"   ❌ Behavior extraction failed: {e}")
            import traceback
            traceback.print_exc()
            
        print(f"\n🔍 Step 5: Create layout data and populate...")
        try:
            layout_data = processor._create_base_layout_data(context)
            print(f"   Base layout data created: {layout_data.keyboard}")
            
            # If we got behaviors, populate them
            if 'behaviors_dict' in locals() and behaviors_dict:
                processor._populate_behaviors_in_layout(layout_data, behaviors_dict)
                print(f"   Behaviors populated in layout data")
                
                final_behavior_count = (
                    len(layout_data.hold_taps or []) +
                    len(layout_data.macros or []) +
                    len(layout_data.combos or []) +
                    len(layout_data.tap_dances or [])
                )
                print(f"   Final behavior count in layout_data: {final_behavior_count}")
                
            else:
                print(f"   No behaviors to populate")
                
        except Exception as e:
            print(f"   ❌ Layout data creation/population failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"   ❌ Processor test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_processor_behaviors()