#!/usr/bin/env python3
"""
Debug script to trace the parsing pipeline step by step to find where behaviors are lost.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def debug_parsing_pipeline():
    """Debug the parsing pipeline step by step."""
    print("=== Debug Parsing Pipeline ===\n")
    
    # Read the generated keymap
    keymap_file = Path("/tmp/glove80_fluent_output/glove80.keymap")
    keymap_content = keymap_file.read_text()
    
    print(f"✅ Loaded keymap ({len(keymap_content)} chars)")
    
    # Test each step of the pipeline manually
    print(f"\n🔍 Step 1: Test AST parsing...")
    try:
        from zmk_layout.parsers.dt_parser import parse_dt_multiple_safe
        roots, parse_errors = parse_dt_multiple_safe(keymap_content)
        
        print(f"   AST roots: {len(roots)}")
        print(f"   Parse errors: {len(parse_errors)}")
        
        if parse_errors:
            print("   Parse errors prevent further processing:")
            for error in parse_errors[:3]:
                print(f"     - {error}")
            return
        
    except Exception as e:
        print(f"   ❌ AST parsing failed: {e}")
        return
    
    print(f"\n🔍 Step 2: Test direct behavior extraction...")
    try:
        from zmk_layout.parsers.ast_walker import UniversalBehaviorExtractor
        
        extractor = UniversalBehaviorExtractor()
        behavior_nodes = extractor.extract_all_behaviors_multiple(roots)
        
        node_counts = {k: len(v) for k, v in behavior_nodes.items() if v}
        print(f"   Direct behavior node extraction: {node_counts}")
        
        total_nodes = sum(len(nodes) for nodes in behavior_nodes.values())
        print(f"   Total behavior nodes found: {total_nodes}")
        
        if total_nodes == 0:
            print("   ❌ No behaviors extracted at node level - AST issue")
            return
            
    except Exception as e:
        print(f"   ❌ Behavior extraction failed: {e}")
        return
    
    print(f"\n🔍 Step 3: Test behavior model conversion...")
    try:
        # Test the model conversion that should happen in the pipeline
        behavior_models = extractor.extract_behaviors_as_models(
            roots=roots,
            source_content=keymap_content,
            defines={}
        )
        
        model_counts = {k: len(v) for k, v in behavior_models.items() if v}
        print(f"   Behavior model conversion: {model_counts}")
        
        total_models = sum(len(models) for models in behavior_models.values())
        print(f"   Total behavior models created: {total_models}")
        
        if total_models == 0:
            print("   ❌ No behaviors converted to models - conversion issue")
        else:
            print("   ✅ Behavior model conversion working")
            
    except Exception as e:
        print(f"   ❌ Behavior model conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n🔍 Step 4: Test section extractor...")
    try:
        from zmk_layout.parsers.section_extractor import create_section_extractor
        
        section_extractor = create_section_extractor()
        
        # Test if the section extractor's behavior_extractor works
        section_behavior_models = section_extractor.behavior_extractor.extract_behaviors_as_models(
            roots=roots,
            source_content=keymap_content,
            defines={}
        )
        
        section_model_counts = {k: len(v) for k, v in section_behavior_models.items() if v}
        print(f"   Section extractor behavior models: {section_model_counts}")
        
        total_section_models = sum(len(models) for models in section_behavior_models.values())
        print(f"   Total section behavior models: {total_section_models}")
        
    except Exception as e:
        print(f"   ❌ Section extractor test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🔍 Step 5: Test full keymap processor...")
    try:
        from zmk_layout.parsers.keymap_processors import create_full_keymap_processor
        from zmk_layout.parsers.parsing_models import ParsingContext
        
        processor = create_full_keymap_processor()
        
        # Create parsing context
        context = ParsingContext(
            keymap_content=keymap_content,
            title="Debug Test",
            keyboard_name="glove80"
        )
        
        print(f"   Created processor and context")
        
        # Process the context
        layout_data = processor.process(context)
        
        if layout_data:
            print(f"   ✅ Processor created layout_data successfully")
            print(f"   Layers: {len(layout_data.layers) if layout_data.layers else 0}")
            print(f"   Hold-taps: {len(layout_data.hold_taps) if layout_data.hold_taps else 0}")
            print(f"   Macros: {len(layout_data.macros) if layout_data.macros else 0}")
            print(f"   Combos: {len(layout_data.combos) if layout_data.combos else 0}")
            print(f"   Tap-dances: {len(layout_data.tap_dances) if layout_data.tap_dances else 0}")
            
            behavior_total = (
                len(layout_data.hold_taps or []) +
                len(layout_data.macros or []) +
                len(layout_data.combos or []) +
                len(layout_data.tap_dances or [])
            )
            
            if behavior_total == 0:
                print(f"   ❌ No behaviors in final layout_data - pipeline issue")
            else:
                print(f"   ✅ Behaviors found in final layout_data: {behavior_total}")
        else:
            print(f"   ❌ Processor returned None")
            
    except Exception as e:
        print(f"   ❌ Processor test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_parsing_pipeline()