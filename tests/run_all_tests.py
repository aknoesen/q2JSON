#!/usr/bin/env python3
"""
Test Runner for q2JSON Comprehensive Acid Test
Location: tests/run_all_tests.py

Runs all tests including the comprehensive acid test framework.
"""

import sys
import os
from pathlib import Path
import subprocess

def run_acid_test():
    """Run the comprehensive acid test."""
    
    print("🧪 q2JSON Test Suite - Comprehensive Acid Test")
    print("=" * 50)
    
    current_dir = Path(__file__).parent
    
    # Check if acid test framework exists
    acid_test_file = current_dir / "test_acid_comprehensive.py"
    
    if not acid_test_file.exists():
        print(f"❌ Acid test framework not found: {acid_test_file}")
        print("Please ensure test_acid_comprehensive.py is in the tests directory")
        return 1
        
    print(f"📁 Running from: {current_dir}")
    print(f"🔧 Acid Test File: {acid_test_file.name}")
    
    try:
        # Run the comprehensive acid test
        print("\n🚀 Starting Comprehensive Acid Test...")
        result = subprocess.run([sys.executable, str(acid_test_file)], 
                              cwd=current_dir, 
                              capture_output=False)
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running acid test: {e}")
        return 1

def run_existing_tests():
    """Run existing test files."""
    
    current_dir = Path(__file__).parent
    test_files = [
        "test_edge_cases_and_llm_behaviors.py",
        "test_json_processor.py"
    ]
    
    print("\n🧪 Running Existing Test Suite...")
    print("=" * 40)
    
    results = {}
    
    for test_file in test_files:
        test_path = current_dir / test_file
        if test_path.exists():
            print(f"\n▶️  Running: {test_file}")
            try:
                result = subprocess.run([sys.executable, str(test_path)], 
                                      cwd=current_dir,
                                      capture_output=True,
                                      text=True)
                
                results[test_file] = result.returncode
                
                if result.returncode == 0:
                    print(f"✅ {test_file}: PASSED")
                else:
                    print(f"❌ {test_file}: FAILED")
                    if result.stdout:
                        print(f"Output: {result.stdout[-200:]}")  # Last 200 chars
                    if result.stderr:
                        print(f"Error: {result.stderr[-200:]}")
                        
            except Exception as e:
                print(f"❌ Error running {test_file}: {e}")
                results[test_file] = 1
        else:
            print(f"⚠️  {test_file}: Not found")
            
    return results

def main():
    """Main test runner function."""
    
    print("🧪 q2JSON Comprehensive Test Suite")
    print("=" * 40)
    
    # Run existing tests first
    existing_results = run_existing_tests()
    
    # Run comprehensive acid test
    acid_result = run_acid_test()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUITE SUMMARY")
    print("="*60)
    
    # Existing tests summary
    if existing_results:
        print("\n📋 Existing Tests:")
        for test_name, result in existing_results.items():
            status = "✅ PASSED" if result == 0 else "❌ FAILED"
            print(f"   {test_name}: {status}")
            
    # Acid test summary
    print(f"\n🧪 Comprehensive Acid Test:")
    acid_status = "✅ PASSED" if acid_result == 0 else "❌ FAILED" 
    print(f"   test_acid_comprehensive.py: {acid_status}")
    
    # Overall result
    all_passed = acid_result == 0 and all(r == 0 for r in existing_results.values())
    
    print(f"\n🏆 OVERALL RESULT:")
    if all_passed:
        print("✅ ALL TESTS PASSED - PRODUCTION READY!")
        return_code = 0
    else:
        print("❌ SOME TESTS FAILED - REVIEW REQUIRED")
        return_code = 1
        
    print("="*60)
    return return_code

if __name__ == "__main__":
    sys.exit(main())