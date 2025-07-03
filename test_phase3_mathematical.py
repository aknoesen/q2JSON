#!/usr/bin/env python3
"""
Phase 3 Mathematical Consistency Test
Specifically test the 0.776 vs 0.812 detection in Question 8
"""

import json
import sys
import os

# Add paths for imports
sys.path.append('.')
sys.path.append('modules')

def test_mathematical_detection_phase3():
    """Test Phase 3 mathematical consistency detection"""
    
    # Load the test file with known mathematical error
    test_file = r"c:\Users\aknoesen\Documents\Knoesen\Database for EEC1\Debug Problem Cases\MosfetQQDebug.json"
    
    print("=" * 80)
    print("PHASE 3 MATHEMATICAL CONSISTENCY TEST")
    print("=" * 80)
    print(f"Target: Detect 0.776 vs 0.812 contradiction in Question 8")
    print()
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # Test the JSONProcessor with Phase 3 integration
    print("🔍 Testing Phase 3 Integration")
    print("-" * 50)
    
    try:
        from modules.json_processor import JSONProcessor
        processor = JSONProcessor()
        
        # Get Question 8 specifically (known contradiction)
        question_8 = test_data['questions'][7]  # Index 7 = Question 8
        print(f"Question 8: {question_8['title']}")
        print(f"Declared answer: {question_8['correct_answer']}")
        print(f"Feedback snippet: {question_8['feedback_correct'][:100]}...")
        print()
        
        # Run full validation
        validation_results = processor.validate_questions(test_data)
        
        print(f"Full Validation Results:")
        print(f"  Total questions: {validation_results.get('total', 0)}")
        print(f"  Valid: {validation_results.get('valid', 0)}")
        print(f"  Warnings: {validation_results.get('warnings', 0)}")
        print(f"  Errors: {validation_results.get('errors', 0)}")
        
        # Check for mathematical issues specifically
        if validation_results.get('mathematical_issues'):
            print(f"\n✅ Mathematical issues detected: {len(validation_results['mathematical_issues'])}")
            for issue in validation_results['mathematical_issues']:
                print(f"  - {issue}")
        else:
            print(f"\n❌ No mathematical issues detected")
            print("This means the 0.776 vs 0.812 contradiction was NOT found")
        
        # Check Question 8 analysis specifically
        if validation_results.get('question_analysis'):
            q8_analysis = validation_results['question_analysis'][7]  # Question 8
            print(f"\nQuestion 8 Analysis:")
            print(f"  Status: {q8_analysis['status']}")
            print(f"  Issues: {q8_analysis.get('issues', [])}")
            print(f"  Mathematical issues: {q8_analysis.get('mathematical_issues', [])}")
        
        # Manual test of mathematical detection function
        print(f"\n🔧 Manual Mathematical Detection Test")
        print("-" * 50)
        
        if hasattr(processor, '_check_mathematical_consistency_single'):
            math_result = processor._check_mathematical_consistency_single(question_8)
            print(f"Direct mathematical check result: {math_result}")
        else:
            print("❌ _check_mathematical_consistency_single method not found")
            
        return validation_results
        
    except Exception as e:
        print(f"❌ Error in Phase 3 test: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_mathematical_detection_phase3()
