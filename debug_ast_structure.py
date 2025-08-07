#!/usr/bin/env python3
"""
Debug script to examine AST structure and identify parsing issues.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def debug_ast_structure():
    """Debug AST structure to understand parsing issues."""
    print("=== Debugging AST Structure ===\n")
    
    # Read the generated keymap
    keymap_file = Path("/tmp/glove80_fluent_output/glove80.keymap")
    keymap_content = keymap_file.read_text()
    
    print(f"✅ Loaded keymap ({len(keymap_content)} chars)")
    
    # Parse AST with detailed error reporting
    print(f"\n🔍 Parsing AST with detailed error reporting...")
    try:
        from zmk_layout.parsers.dt_parser import parse_dt_multiple_safe
        roots, parse_errors = parse_dt_multiple_safe(keymap_content)
        
        print(f"   AST roots: {len(roots)}")
        print(f"   Parse errors: {len(parse_errors)}")
        
        # Show all parse errors in detail
        print(f"\n📋 Parse errors (all {len(parse_errors)}):")
        for i, error in enumerate(parse_errors):
            print(f"   Error {i}: {error}")
        
        # Examine AST structure
        print(f"\n📋 AST structure:")
        for i, root in enumerate(roots):
            print(f"   Root {i}:")
            print(f"     Type: {type(root)}")
            
            if hasattr(root, 'name'):
                print(f"     Name: {root.name}")
            if hasattr(root, 'children') and root.children:
                print(f"     Children: {len(root.children)}")
                
                # Look for behavior-related nodes
                behavior_children = []
                for j, child in enumerate(root.children):
                    child_name = getattr(child, 'name', str(child))
                    child_type = type(child).__name__
                    print(f"       Child {j}: {child_name} ({child_type})")
                    
                    # Check for behavior keywords
                    child_str = str(child_name).lower()
                    if any(keyword in child_str for keyword in ['behavior', 'hold-tap', 'combo', 'macro', 'tap-dance']):
                        behavior_children.append((j, child))
                        print(f"         *** BEHAVIOR NODE ***")
                
                if behavior_children:
                    print(f"     Found {len(behavior_children)} behavior-related children")
                    
                    # Examine behavior nodes in detail
                    for idx, (child_idx, behavior_child) in enumerate(behavior_children):
                        print(f"       Behavior {idx} (child {child_idx}):")
                        if hasattr(behavior_child, 'children'):
                            print(f"         Sub-children: {len(behavior_child.children) if behavior_child.children else 0}")
                            if behavior_child.children:
                                for k, subchild in enumerate(behavior_child.children[:5]):  # First 5
                                    subchild_name = getattr(subchild, 'name', str(subchild))
                                    print(f"           Subchild {k}: {subchild_name}")
        
        # Look for problematic lines in the content
        print(f"\n🔍 Examining problematic lines...")
        lines = keymap_content.split('\n')
        
        # Find the ZMK_TD_LAYER line that's causing issues
        for i, line in enumerate(lines, 1):
            if 'ZMK_TD_LAYER' in line:
                print(f"   Line {i}: {line.strip()}")
                print(f"     This line is causing parse errors")
                
                # Show context
                start = max(0, i-3)
                end = min(len(lines), i+3)
                print(f"     Context:")
                for ctx_i in range(start, end):
                    marker = ">>>" if ctx_i == i-1 else "   "
                    print(f"     {marker} {ctx_i+1}: {lines[ctx_i]}")
        
        # Let's also check if we can find behavior definitions manually
        print(f"\n🔍 Manual behavior detection in content...")
        in_behaviors_section = False
        behavior_count = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if 'behaviors {' in stripped:
                in_behaviors_section = True
                print(f"   Found behaviors section at line {i}")
                continue
                
            if in_behaviors_section:
                if stripped == '}' or stripped == '};':
                    in_behaviors_section = False
                    continue
                    
                # Look for behavior definitions
                if ':' in stripped and any(word in stripped for word in ['hold-tap', 'tap-dance', 'macro']):
                    behavior_count += 1
                    print(f"   Behavior {behavior_count} at line {i}: {stripped}")
        
        print(f"   Total behaviors found manually: {behavior_count}")
        
    except Exception as e:
        print(f"   ❌ AST parsing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ast_structure()