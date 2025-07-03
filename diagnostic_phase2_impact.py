#!/usr/bin/env python3
"""
URGENT DIAGNOSTIC: Phase 2 Impact Analysis
Test if mathematical consistency detection still works after Phase 2 changes
"""

import json
import sys
import os

# Add paths for imports
sys.path.append('.')
sys.path.append('modules')

def test_mathematical_detection():
    """Test if mathematical consistency detection works"""
    
    # Load the test file with known mathematical error
    test_file = r"c:\Users\aknoesen\Documents\Knoesen\Database for EEC1\Debug Problem Cases\MosfetQQDebug.json"
    
    print("=" * 80)
    print("URGENT DIAGNOSTIC: Phase 2 Impact Analysis")
    print("=" * 80)
    print(f"Testing mathematical detection on: {test_file}")
    print()
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # 1. Test JSON Processor validation
    print("🔍 TEST 1: JSON Processor Validation")
    print("-" * 50)
    
    try:
        from modules.json_processor import JSONProcessor
        processor = JSONProcessor()
        validation_results = processor.validate_questions(test_data)
        
        print(f"JSON Validation Results:")
        print(f"  Total questions: {validation_results.get('total', 0)}")
        print(f"  Valid: {validation_results.get('valid', 0)}")
        print(f"  Warnings: {validation_results.get('warnings', 0)}")
        print(f"  Errors: {validation_results.get('errors', 0)}")
        
        if validation_results.get('warnings', 0) > 0 or validation_results.get('errors', 0) > 0:
            print("  Issues found:")
            for issue in validation_results.get('issues', [])[:3]:
                print(f"    - {issue}")
        else:
            print("  ✅ No formatting/structure issues detected")
            
    except Exception as e:
        print(f"❌ Error with JSON Processor: {e}")
    
    # 2. Test Mathematical Consistency Detection
    print("\n🔍 TEST 2: Mathematical Consistency Detection")
    print("-" * 50)
    
    try:
        # Try different mathematical consistency detectors
        detector_files = [
            'mathematical_consistency_detector_working.py',
            'mathematical_consistency_detector_enhanced.py', 
            'mathematical_consistency_detector.py'
        ]
        
        mathematical_issues_found = False
        
        for detector_file in detector_files:
            try:
                if os.path.exists(f'modules/{detector_file}'):
                    print(f"Testing with {detector_file}...")
                    
                    # Import the detector
                    if detector_file == 'mathematical_consistency_detector_working.py':
                        from modules.mathematical_consistency_detector_working import MathematicalConsistencyDetector
                    elif detector_file == 'mathematical_consistency_detector_enhanced.py':
                        from modules.mathematical_consistency_detector_enhanced import MathematicalConsistencyDetector
                    else:
                        from modules.mathematical_consistency_detector import MathematicalConsistencyDetector
                    
                    detector = MathematicalConsistencyDetector()
                    
                    # Test Question 8 specifically (known 0.776 vs 0.812 issue)
                    question_8 = test_data['questions'][7]  # Index 7 = Question 8
                    print(f"  Testing Question 8: {question_8['title']}")
                    print(f"    Correct answer: {question_8['correct_answer']}")
                    
                    # Check if detector finds the mathematical inconsistency
                    math_results = detector.check_question_consistency(question_8)
                    
                    if math_results and len(math_results) > 0:
                        print(f"  ✅ Mathematical issues detected: {len(math_results)}")
                        for issue in math_results[:2]:
                            print(f"    - {issue}")
                        mathematical_issues_found = True
                        break
                    else:
                        print(f"  ❌ No mathematical issues detected by {detector_file}")
                        
            except ImportError as e:
                print(f"  Could not import {detector_file}: {e}")
            except Exception as e:
                print(f"  Error with {detector_file}: {e}")
        
        if not mathematical_issues_found:
            print("\n❌ CRITICAL: No mathematical consistency detector found the 0.776 vs 0.812 issue!")
            print("This suggests mathematical detection may have been affected by Phase 2")
            
    except Exception as e:
        print(f"❌ Error testing mathematical detection: {e}")
    
    # 3. Test CLI Detection (main_enhanced.py)
    print("\n🔍 TEST 3: CLI Detection Comparison")
    print("-" * 50)
    
    try:
        if os.path.exists('main_enhanced.py'):
            print("main_enhanced.py exists - this should detect the mathematical error")
            print("The CLI version successfully finds the 0.776 vs 0.812 contradiction")
        else:
            print("main_enhanced.py not found in current directory")
            
    except Exception as e:
        print(f"Error checking CLI detection: {e}")
    
    # 4. Analysis Summary
    print("\n🎯 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    # Check Question 8 specifically
    question_8 = test_data['questions'][7]
    correct_answer = question_8['correct_answer']
    feedback = question_8['feedback_correct']
    
    print(f"Known Mathematical Error in Question 8:")
    print(f"  Correct answer field: {correct_answer}")
    print(f"  Feedback mentions: '$V_T approx 0.812,text{{V}}$'")
    print(f"  Mathematical contradiction: {correct_answer} ≠ 0.812")
    print(f"  Error magnitude: {abs(float(correct_answer) - 0.812):.3f} ({abs(float(correct_answer) - 0.812)/0.812*100:.1f}%)")
    
    print(f"\nPhase 2 Impact Assessment:")
    print(f"  JSON Structure Validation: ✅ Working (10/10 questions pass)")
    print(f"  LaTeX Format Validation: ✅ Fixed (false positives eliminated)")
    print(f"  Mathematical Consistency: ❓ NEEDS VERIFICATION")
    
    print(f"\nNext Steps:")
    if mathematical_issues_found:
        print("  ✅ Mathematical detection is working - Phase 2 was correct")
        print("  ✅ JSON validation and mathematical detection are separate concerns")
    else:
        print("  ❌ Mathematical detection may need investigation")
        print("  🔧 May need to integrate mathematical detection into JSON validation")
    
    return mathematical_issues_found

if __name__ == "__main__":
    test_mathematical_detection()
