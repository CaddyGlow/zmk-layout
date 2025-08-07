#!/usr/bin/env python3
"""
Debug script to check the actual method signature of the behavior extractor.
"""

import sys
from pathlib import Path
import inspect

sys.path.append(str(Path(__file__).parent))

def debug_method_signature():
    """Debug the actual method signature being used."""
    print("=== Debug Method Signature ===\n")
    
    print(f"🔍 Checking UniversalBehaviorExtractor method signature...")
    try:
        from zmk_layout.parsers.ast_walker import UniversalBehaviorExtractor
        
        extractor = UniversalBehaviorExtractor()
        method = extractor.extract_behaviors_as_models
        
        print(f"   Method: {method}")
        print(f"   Method signature: {inspect.signature(method)}")
        
        # Get the source code of the method
        try:
            source = inspect.getsource(method)
            print(f"   Method source (first 10 lines):")
            for i, line in enumerate(source.split('\n')[:10]):
                print(f"     {i+1}: {line}")
        except Exception as e:
            print(f"   Could not get source: {e}")
        
        # Check where the class is imported from
        print(f"   Class module: {UniversalBehaviorExtractor.__module__}")
        print(f"   Class file: {inspect.getfile(UniversalBehaviorExtractor)}")
        
        # Try to call it with different parameter combinations
        print(f"\n🔍 Testing method calls...")
        
        from zmk_layout.parsers.dt_parser import parse_dt_multiple_safe
        
        # Read test content
        keymap_file = Path("/tmp/glove80_fluent_output/glove80.keymap")
        keymap_content = keymap_file.read_text()
        
        roots, _ = parse_dt_multiple_safe(keymap_content)
        
        # Try different parameter combinations
        try:
            print("   Trying: method(roots)")
            result = method(roots)
            print(f"   Success with 1 param: {len(result)} behavior types")
        except Exception as e:
            print(f"   Failed with 1 param: {e}")
        
        try:
            print("   Trying: method(roots, keymap_content)")
            result = method(roots, keymap_content)
            print(f"   Success with 2 params: {len(result)} behavior types")
        except Exception as e:
            print(f"   Failed with 2 params: {e}")
        
        try:
            print("   Trying: method(roots, keymap_content, {})")
            result = method(roots, keymap_content, {})
            print(f"   Success with 3 params: {len(result)} behavior types")
        except Exception as e:
            print(f"   Failed with 3 params: {e}")
        
        try:
            print("   Trying: method(roots=roots, source_content=keymap_content, defines={})")
            result = method(roots=roots, source_content=keymap_content, defines={})
            print(f"   Success with named params: {len(result)} behavior types")
        except Exception as e:
            print(f"   Failed with named params: {e}")
        
    except Exception as e:
        print(f"   ❌ Error importing/inspecting: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_method_signature()