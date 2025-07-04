#!/usr/bin/env python3
"""
Run all diagnostic tests for Stage 4 UI issue
"""

import subprocess
import sys
import os

def run_all_tests():
    """Run all diagnostic tests"""
    
    print("=" * 80)
    print("RUNNING ALL STAGE 4 UI DIAGNOSTIC TESTS")
    print("=" * 80)
    
    tests = [
        ("Quick Choice Test", "quick_choice_test.py"),
        ("Stage 4 UI Diagnostic", "diagnostic_stage4_ui.py"),
        ("Phase 2 Impact Test", "diagnostic_phase2_impact.py")
    ]
    
    results = {}
    
    for test_name, test_file in tests:
        print(f"\n{'='*60}")
        print(f"RUNNING: {test_name}")
        print(f"{'='*60}")
        
        if os.path.exists(test_file):
            try:
                result = subprocess.run([sys.executable, test_file], 
                                      capture_output=True, text=True, timeout=30)
                
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                
                results[test_name] = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
                
            except subprocess.TimeoutExpired:
                print(f"❌ Test {test_name} timed out")
                results[test_name] = "❌ TIMEOUT"
            except Exception as e:
                print(f"❌ Error running {test_name}: {e}")
                results[test_name] = "❌ ERROR"
        else:
            print(f"❌ Test file {test_file} not found")
            results[test_name] = "❌ NOT FOUND"
    
    # Summary
    print(f"\n{'='*60}")
    print("DIAGNOSTIC SUMMARY")
    print(f"{'='*60}")
    
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    print(f"\nNext Steps:")
    print(f"1. Check if choices exist in raw JSON (should be ✅)")
    print(f"2. Verify components can access choices (should be ✅)")
    print(f"3. Find where choices are lost in UI rendering (likely issue)")
    print(f"4. Add debug logging to stages/stage_3_human_review.py")

if __name__ == "__main__":
    run_all_tests()