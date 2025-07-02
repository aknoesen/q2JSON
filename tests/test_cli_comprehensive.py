"""
Comprehensive CLI testing for Q2JSON pipeline
"""

import sys
import os
import subprocess
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_cli_command(args, expect_success=True):
    """Run a CLI command and return result"""
    
    cmd = [sys.executable, "main.py"] + args
    
    # Change to parent directory to run main.py
    parent_dir = os.path.join(os.path.dirname(__file__), '..')
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=parent_dir)
    
    return {
        'returncode': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'success': result.returncode == 0 if expect_success else result.returncode != 0
    }


def test_cli_comprehensive():
    """Comprehensive CLI testing"""
    
    print("🧪 COMPREHENSIVE CLI TESTING")
    print("=" * 45)
    
    # Test data with contradiction
    test_data = {
        "questions": [{
            "correct_answer": "0.776",
            "feedback_correct": "Calculation gives V_T = 0.8116 V. Final answer: V_T = 0.776 V."
        }]
    }
    
    # Create temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json.dump(test_data, temp_file, indent=2)
        test_file_path = temp_file.name
    
    try:
        # Test 1: Help command
        print(f"\n🧪 Test 1: Help Command")
        result = run_cli_command(["--help"])
        
        if result['success'] and "Q2JSON Processing Pipeline" in result['stdout']:
            print(f"   ✅ PASS - Help displayed correctly")
        else:
            print(f"   ❌ FAIL - Help command failed")
            print(f"   Error: {result['stderr']}")
        
        # Test 2: Basic processing
        print(f"\n🧪 Test 2: Basic Processing")
        result = run_cli_command([test_file_path])
        
        if result['success']:
            print(f"   ✅ PASS - Basic processing succeeded")
            if "mathematical contradictions" in result['stdout']:
                print(f"   ✅ PASS - Math validation detected contradiction")
            else:
                print(f"   ⚠️ NOTE - Math validation output different than expected")
        else:
            print(f"   ❌ FAIL - Basic processing failed")
            print(f"   Return code: {result['returncode']}")
            print(f"   Error: {result['stderr']}")
        
        # Test 3: Quiet mode
        print(f"\n🧪 Test 3: Quiet Mode")
        result = run_cli_command([test_file_path, "-q"])
        
        if result['success']:
            print(f"   ✅ PASS - Quiet mode succeeded")
            output_lines = len(result['stdout'].strip().split('\n'))
            if output_lines <= 3:  # Should be minimal output
                print(f"   ✅ PASS - Output is minimal ({output_lines} lines)")
            else:
                print(f"   ⚠️ NOTE - Output longer than expected ({output_lines} lines)")
        else:
            print(f"   ❌ FAIL - Quiet mode failed")
            print(f"   Return code: {result['returncode']}")
        
        # Test 4: Skip math check
        print(f"\n🧪 Test 4: Skip Math Check")
        result = run_cli_command([test_file_path, "--no-math-check"])
        
        if result['success']:
            print(f"   ✅ PASS - No-math-check succeeded")
            if "SKIPPED" in result['stdout'] or "skipped" in result['stdout'].lower():
                print(f"   ✅ PASS - Math validation was skipped")
            else:
                print(f"   ⚠️ NOTE - Skip confirmation not found in output")
        else:
            print(f"   ❌ FAIL - No-math-check failed")
        
        # Test 5: Custom output file
        print(f"\n🧪 Test 5: Custom Output File")
        custom_output = os.path.join(tempfile.gettempdir(), "test_custom_output.json")
        
        result = run_cli_command([test_file_path, "-o", custom_output])
        
        if result['success']:
            print(f"   ✅ PASS - Custom output succeeded")
            
            # Check if file was created
            if os.path.exists(custom_output):
                print(f"   ✅ PASS - Output file created")
                
                # Verify file content
                try:
                    with open(custom_output, 'r', encoding='utf-8') as f:
                        output_data = json.load(f)
                    
                    if 'questions' in output_data:
                        print(f"   ✅ PASS - Output file contains valid JSON")
                    else:
                        print(f"   ❌ FAIL - Output file missing 'questions'")
                except Exception as e:
                    print(f"   ❌ FAIL - Output file not valid JSON: {e}")
                
                # Clean up
                try:
                    os.unlink(custom_output)
                except:
                    pass
            else:
                print(f"   ❌ FAIL - Output file not created at {custom_output}")
        else:
            print(f"   ❌ FAIL - Custom output failed")
            print(f"   Error: {result['stderr']}")
        
        # Test 6: Invalid input file
        print(f"\n🧪 Test 6: Invalid Input File")
        result = run_cli_command(["nonexistent_file.json"], expect_success=False)
        
        if not result['success']:
            print(f"   ✅ PASS - Properly handled invalid input file (exit code: {result['returncode']})")
        else:
            print(f"   ❌ FAIL - Should have failed with invalid input file")
        
        # Test 7: Real MOSFET file (if available)
        print(f"\n🧪 Test 7: Real MOSFET File")
        mosfet_file = "c:/Users/aknoesen/Downloads/MosfetCornerCasePhase2.json"
        
        if os.path.exists(mosfet_file):
            result = run_cli_command([mosfet_file, "-q"])
            
            if result['success']:
                print(f"   ✅ PASS - MOSFET file processed successfully")
                
                # Check if output file was created
                mosfet_path = Path(mosfet_file)
                expected_output = str(mosfet_path.parent / f"{mosfet_path.stem}_processed{mosfet_path.suffix}")
                
                if os.path.exists(expected_output):
                    print(f"   ✅ PASS - Output file created for MOSFET")
                    # Note: We won't delete this as it might be useful
                else:
                    print(f"   ⚠️ NOTE - Expected output file not found: {expected_output}")
            else:
                print(f"   ❌ FAIL - MOSFET file processing failed")
                print(f"   Error: {result['stderr']}")
        else:
            print(f"   ⏭️ SKIP - MOSFET file not available")
    
    finally:
        # Clean up test file
        try:
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)
        except:
            pass
    
    print(f"\n🎯 COMPREHENSIVE CLI TESTING COMPLETED")


def test_exit_codes():
    """Test exit codes for automation"""
    
    print(f"\n🧪 TESTING EXIT CODES FOR AUTOMATION")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Help command",
            "args": ["--help"],
            "expected_codes": [0],
            "description": "Should return 0 for help"
        },
        {
            "name": "Invalid file",
            "args": ["nonexistent.json"],
            "expected_codes": [1, 3],  # Could be 1 (file not found) or 3 (processing error)
            "description": "Should return non-zero for invalid file"
        }
    ]
    
    # Test with MOSFET file if available
    mosfet_file = "c:/Users/aknoesen/Downloads/MosfetCornerCasePhase2.json"
    if os.path.exists(mosfet_file):
        test_cases.extend([
            {
                "name": "Clean MOSFET file",
                "args": [mosfet_file, "-q"],
                "expected_codes": [0],
                "description": "Should return 0 for clean file"
            },
            {
                "name": "MOSFET without math check",
                "args": [mosfet_file, "--no-math-check", "-q"],
                "expected_codes": [0],
                "description": "Should return 0 when skipping math check"
            }
        ])
    
    for test_case in test_cases:
        print(f"\n   🧪 {test_case['name']}")
        
        result = run_cli_command(test_case['args'], expect_success=False)
        
        expected_codes = test_case['expected_codes']
        actual_code = result['returncode']
        
        print(f"   Expected codes: {expected_codes}")
        print(f"   Actual code: {actual_code}")
        
        if actual_code in expected_codes:
            print(f"   ✅ PASS - {test_case['description']}")
        else:
            print(f"   ❌ FAIL - Expected one of {expected_codes}, got {actual_code}")
            if result['stderr']:
                print(f"   Error output: {result['stderr'][:100]}...")
    
    print(f"\n🎯 EXIT CODE TESTING COMPLETED")


if __name__ == "__main__":
    test_cli_comprehensive()
    test_exit_codes()