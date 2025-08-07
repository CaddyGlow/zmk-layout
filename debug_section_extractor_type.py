#!/usr/bin/env python3
"""
Debug script to check what type of behavior extractor is used in the section extractor.
"""

import sys
from pathlib import Path
import inspect

sys.path.append(str(Path(__file__).parent))

def debug_section_extractor_type():
    """Debug the actual type of behavior extractor in section extractor."""
    print("=== Debug Section Extractor Type ===\n")
    
    print(f"🔍 Checking section extractor behavior extractor...")
    try:
        from zmk_layout.parsers.keymap_processors import create_full_keymap_processor
        
        processor = create_full_keymap_processor()
        section_extractor = processor.section_extractor
        behavior_extractor = section_extractor.behavior_extractor
        
        print(f"   Processor type: {type(processor).__name__}")
        print(f"   Section extractor type: {type(section_extractor).__name__}")
        print(f"   Behavior extractor type: {type(behavior_extractor).__name__}")
        print(f"   Behavior extractor module: {behavior_extractor.__class__.__module__}")
        print(f"   Behavior extractor file: {inspect.getfile(behavior_extractor.__class__)}")
        
        # Check if it has the method
        if hasattr(behavior_extractor, 'extract_behaviors_as_models'):
            method = behavior_extractor.extract_behaviors_as_models
            print(f"   Method exists: {method}")
            print(f"   Method signature: {inspect.signature(method)}")
            
            # Try to get the method source
            try:
                source = inspect.getsource(method)
                print(f"   Method source (first 10 lines):")
                for i, line in enumerate(source.split('\n')[:10]):
                    print(f"     {i+1}: {line}")
            except Exception as e:
                print(f"   Could not get method source: {e}")
        else:
            print(f"   ❌ Method extract_behaviors_as_models not found")
        
        # Check if it's a different type
        print(f"\n🔍 Checking for alternative behavior extractor types...")
        
        # Check the section extractor source
        try:
            from zmk_layout.parsers.section_extractor import create_section_extractor
            
            direct_section_extractor = create_section_extractor()
            direct_behavior_extractor = direct_section_extractor.behavior_extractor
            
            print(f"   Direct section extractor type: {type(direct_section_extractor).__name__}")
            print(f"   Direct behavior extractor type: {type(direct_behavior_extractor).__name__}")
            print(f"   Same instance? {direct_behavior_extractor is behavior_extractor}")
            
            if hasattr(direct_behavior_extractor, 'extract_behaviors_as_models'):
                direct_method = direct_behavior_extractor.extract_behaviors_as_models
                print(f"   Direct method signature: {inspect.signature(direct_method)}")
        except Exception as e:
            print(f"   Error checking direct section extractor: {e}")
        
        # Test the actual method call that's failing
        print(f"\n🔍 Testing the actual failing call...")
        try:
            from zmk_layout.parsers.dt_parser import parse_dt_multiple_safe
            
            # Read test content
            keymap_file = Path("/tmp/glove80_fluent_output/glove80.keymap")
            keymap_content = keymap_file.read_text()
            
            roots, _ = parse_dt_multiple_safe(keymap_content)
            defines = {}
            
            # This is the exact call that's failing
            print("   Trying the exact failing call:")
            result = behavior_extractor.extract_behaviors_as_models(
                roots=roots, source_content=keymap_content, defines=defines
            )
            behavior_counts = {k: len(v) for k, v in result.items() if v}
            print(f"   ✅ Success! Behavior counts: {behavior_counts}")
            
        except Exception as e:
            print(f"   ❌ The exact call still fails: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_section_extractor_type()