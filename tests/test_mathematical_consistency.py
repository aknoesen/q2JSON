"""
Test Mathematical Consistency Detector with MosfetCornerCasePhase2.json
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from modules.mathematical_consistency_detector import MathematicalConsistencyDetector
from modules.json_processor import JSONProcessor


def test_mosfet_corner_case():
    """Test the specific contradictions in MosfetCornerCasePhase2.json"""
    
    print("=== Mathematical Consistency Analysis ===")
    print("Testing MosfetCornerCasePhase2.json for calculation contradictions\n")
    
    # Load the test data
    test_file_path = "../MosfetCornerCasePhase2.json"
    
    try:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            # Remove comments for valid JSON parsing
            content = f.read()
            content = '\n'.join(line for line in content.split('\n') if not line.strip().startswith('//'))
            test_data = json.loads(content)
    except FileNotFoundError:
        test_file_path = "c:/Users/aknoesen/Downloads/MosfetCornerCasePhase2.json"
        try:
            with open(test_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                content = '\n'.join(line for line in content.split('\n') if not line.strip().startswith('//'))
                test_data = json.loads(content)
        except FileNotFoundError:
            print("❌ Could not find MosfetCornerCasePhase2.json")
            print("Please ensure the file is in the correct location")
            return False
    
    print(f"✅ Loaded test data with {len(test_data.get('questions', []))} questions\n")
    
    # Initialize the detector
    detector = MathematicalConsistencyDetector(tolerance_threshold=0.05)  # 5% threshold
    
    # Detect contradictions
    contradictions = detector.detect_contradictions(test_data)
    
    # Display results
    print(f"🔍 Analysis Results:")
    print(f"   Contradictions found: {len(contradictions)}")
    
    if contradictions:
        print(f"\n📊 Summary Statistics:")
        stats = detector.get_summary_stats()
        print(f"   Total contradictions: {stats['total']}")
        print(f"   Questions affected: {stats['questions_affected']}")
        print(f"   Average difference: {stats['avg_difference']:.1f}%")
        print(f"   Maximum difference: {stats['max_difference']:.1f}%")
        print(f"   By severity: {stats['by_severity']}")
        
        print(f"\n📋 Detailed Report:")
        print(detector.generate_report())
        
        # Test specific known contradiction
        print(f"\n🎯 Specific Contradiction Analysis:")
        print("Looking for the 0.8116V vs 0.812V vs 0.776V contradiction...")
        
        found_target_contradiction = False
        for contradiction in contradictions:
            if (contradiction.question_index == 0 and  # First question
                any(abs(v - 0.776) < 0.001 or abs(v - 0.8116) < 0.001 or abs(v - 0.812) < 0.001 
                    for v in contradiction.values_found)):
                found_target_contradiction = True
                print(f"✅ Found target contradiction!")
                print(f"   Values: {contradiction.values_found}")
                print(f"   Difference: {contradiction.percentage_difference:.1f}%")
                print(f"   Severity: {contradiction.severity}")
                break
        
        if not found_target_contradiction:
            print("❓ Target contradiction not detected - may need pattern refinement")
        
    else:
        print("✅ No contradictions detected")
    
    return len(contradictions) > 0


def test_integration_with_json_processor():
    """Test integration with existing JSON processor"""
    
    print("\n" + "="*60)
    print("=== Integration Test with JSON Processor ===\n")
    
    # Load test data
    test_file_path = "c:/Users/aknoesen/Downloads/MosfetCornerCasePhase2.json"
    
    try:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            raw_json = f.read()
    except FileNotFoundError:
        print("❌ Could not find test file for integration test")
        return False
    
    # Create JSON processor instance
    processor = JSONProcessor()
    
    # Import and apply the integration
    from modules.validation_enhancements import integrate_enhanced_validation
    integrate_enhanced_validation(processor)
    
    # Process the JSON (this will now include math consistency checking)
    success, data, messages = processor.process_raw_json(raw_json)
    
    print(f"Processing result: {success}")
    print(f"Messages: {messages}")
    
    # Check if mathematical contradictions were detected
    if hasattr(processor, 'get_mathematical_consistency_report'):
        math_report = processor.get_mathematical_consistency_report()
        print(f"\n📊 Mathematical Consistency Report:")
        print(math_report)
        
        # Check if contradictions were detected
        if "No mathematical contradictions detected" in math_report:
            print("✅ Integration working, but no contradictions detected")
        else:
            print("🚨 Integration working and contradictions detected!")
            return True
    else:
        print("❌ Integration failed - method not added")
        return False
    
    return False


def test_individual_patterns():
    """Test individual contradiction patterns"""
    
    print("\n" + "="*60)
    print("=== Individual Pattern Testing ===\n")
    
    detector = MathematicalConsistencyDetector()
    
    # Test cases that should trigger contradictions
    test_cases = [
        {
            "name": "Multiple final answers in feedback",
            "content": "The answer is 0.8116V. Rounding gives 0.812V. Final answer: 0.776V.",
            "expected_contradiction": True
        },
        {
            "name": "Consistent rounding (should NOT trigger)",
            "content": "The answer is 0.815V. Rounding gives 0.82V.",
            "expected_contradiction": False
        },
        {
            "name": "Scientific calculation with contradiction",
            "content": "Calculate: 0.5 + 0.4(1.673 - 0.894) = 0.8116V but final answer is 0.776V",
            "expected_contradiction": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Test {i}: {test_case['name']}")
        
        # Create mock question data
        mock_data = {
            "questions": [{
                "feedback_correct": test_case["content"],
                "correct_answer": "0.776"
            }]
        }
        
        contradictions = detector.detect_contradictions(mock_data)
        
        has_contradiction = len(contradictions) > 0
        
        if has_contradiction == test_case["expected_contradiction"]:
            print(f"   ✅ PASS - Expected: {test_case['expected_contradiction']}, Got: {has_contradiction}")
        else:
            print(f"   ❌ FAIL - Expected: {test_case['expected_contradiction']}, Got: {has_contradiction}")
        
        if contradictions:
            print(f"   📊 Found {len(contradictions)} contradictions")
            for contradiction in contradictions:
                print(f"      Values: {contradiction.values_found}")
                print(f"      Difference: {contradiction.percentage_difference:.1f}%")
        
        print()


if __name__ == "__main__":
    print("Mathematical Consistency Detector Test Suite")
    print("=" * 60)
    
    # Run all tests
    test1_result = test_mosfet_corner_case()
    test2_result = test_integration_with_json_processor()
    test_individual_patterns()
    
    print("\n" + "="*60)
    print("=== Test Summary ===")
    print(f"MosfetCornerCase test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Integration test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result or test2_result:
        print("\n🎉 Mathematical contradiction detection is working!")
    else:
        print("\n🔧 May need to refine detection patterns")