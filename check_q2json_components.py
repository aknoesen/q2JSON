#!/usr/bin/env python3
"""
Check what Q2JSON components actually exist
"""

import os
import sys

def check_q2json_components():
    """Check which Q2JSON components exist"""
    
    print("=" * 60)
    print("CHECKING Q2JSON COMPONENTS")
    print("=" * 60)
    
    # Check modules directory
    modules_dir = "modules"
    if os.path.exists(modules_dir):
        print(f"✅ {modules_dir} directory exists")
        
        # List all Python files in modules
        py_files = [f for f in os.listdir(modules_dir) if f.endswith('.py')]
        print(f"\nPython files in {modules_dir}:")
        for f in sorted(py_files):
            print(f"  📄 {f}")
        
        # Check for specific Q2JSON components
        q2json_components = [
            'latex_processor.py',
            'q2json_latex_processor.py',
            'question_renderer.py',
            'q2json_question_renderer.py',
            'validation_manager.py',
            'q2json_validation_manager.py',
            'editor_framework.py',
            'q2json_editor_framework.py'
        ]
        
        print(f"\nChecking for Q2JSON components:")
        found_components = []
        for component in q2json_components:
            if component in py_files:
                print(f"  ✅ {component}")
                found_components.append(component)
            else:
                print(f"  ❌ {component}")
        
        print(f"\nFound {len(found_components)} Q2JSON components")
        
        # Check what we can actually import
        print(f"\nTesting imports:")
        sys.path.append('.')
        sys.path.append('modules')
        
        # Try different import variations
        import_tests = [
            ('latex_processor', 'Q2JSONLaTeXProcessor'),
            ('q2json_latex_processor', 'Q2JSONLaTeXProcessor'),
            ('question_renderer', 'Q2JSONQuestionRenderer'),
            ('q2json_question_renderer', 'Q2JSONQuestionRenderer'),
            ('json_processor', 'JSONProcessor'),
            ('mathematical_consistency_detector', 'MathematicalConsistencyDetector')
        ]
        
        working_imports = []
        for module, class_name in import_tests:
            try:
                exec(f"from modules.{module} import {class_name}")
                print(f"  ✅ from modules.{module} import {class_name}")
                working_imports.append((module, class_name))
            except ImportError as e:
                print(f"  ❌ from modules.{module} import {class_name} - {e}")
        
        print(f"\nWorking imports: {len(working_imports)}")
        
        return found_components, working_imports
        
    else:
        print(f"❌ {modules_dir} directory not found")
        return [], []

if __name__ == "__main__":
    found_components, working_imports = check_q2json_components()
    
    print(f"\n" + "=" * 60)
    print("SOLUTION RECOMMENDATIONS")
    print("=" * 60)
    
    if working_imports:
        print("✅ Some components can be imported")
        print("🔧 Update Stage 3 to use working imports:")
        for module, class_name in working_imports:
            print(f"   from modules.{module} import {class_name}")
    else:
        print("❌ No Q2JSON components can be imported")
        print("🔧 Need to:")
        print("   1. Check if Q2JSON components exist")
        print("   2. Create minimal Q2JSON components")
        print("   3. Use fallback editor in Stage 3")