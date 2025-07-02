"""
Inspect the mathematical consistency detector to understand its methods
"""

import sys
import os
import json
sys.path.insert(0, 'modules')
from mathematical_consistency_detector_working import MathematicalConsistencyDetectorWorking

def inspect_detector():
    """Inspect the detector's methods and attributes"""
    
    print("🔍 INSPECTING MATHEMATICAL CONSISTENCY DETECTOR")
    print("=" * 60)
    
    detector = MathematicalConsistencyDetectorWorking()
    
    print("Available methods and attributes:")
    methods = [method for method in dir(detector) if not method.startswith('__')]
    
    for method in sorted(methods):
        attr = getattr(detector, method)
        if callable(attr):
            print(f"  📝 Method: {method}()")
        else:
            print(f"  📊 Attribute: {method} = {attr}")
    
    print(f"\nDetector class documentation:")
    print(f"  {detector.__class__.__doc__}")
    
    # Test with a simple case to see what's happening
    print(f"\n🧪 Testing with Simple Data:")
    
    simple_data = {
        "questions": [{
            "correct_answer": "0.776",
            "feedback_correct": "Final answer: V_T = 0.812 V."
        }]
    }
    
    print(f"  Input: declared=0.776, feedback contains V_T = 0.812")
    
    contradictions = detector.detect_contradictions(simple_data)
    stats = detector.get_summary_stats()
    
    print(f"  Result: {len(contradictions)} contradictions found")
    print(f"  Stats: {stats}")
    
    if hasattr(detector, 'contradictions_found'):
        print(f"  Internal contradictions: {len(detector.contradictions_found)}")
    
    # Check if there are any threshold settings
    print(f"\n🔧 Checking Internal Settings:")
    for attr in ['threshold', 'min_difference', 'tolerance', 'sensitivity']:
        if hasattr(detector, attr):
            print(f"  {attr}: {getattr(detector, attr)}")
    
    # Now test with real data if available
    print(f"\n🧪 Testing with Real Data (custom_output.json):")
    try:
        with open('custom_output.json', 'r', encoding='utf-8') as f:
            real_data = json.load(f)
        
        print(f"  Loaded {len(real_data['questions'])} questions from real data")
        
        # Reset detector
        detector.contradictions_found = []
        detector.processing_stats = {'questions_analyzed': 0, 'values_extracted': 0, 'contradictions_found': 0}
        
        real_contradictions = detector.detect_contradictions(real_data)
        real_stats = detector.get_summary_stats()
        
        print(f"  Real data result: {len(real_contradictions)} contradictions found")
        print(f"  Real data stats: {real_stats}")
        
        if real_contradictions:
            print(f"\n  📋 Real Contradictions Found:")
            for i, contradiction in enumerate(real_contradictions):
                print(f"    {i+1}. Question {contradiction.question_index + 1}: {contradiction.answer} vs {contradiction.values_found} ({contradiction.percentage_difference:.1f}%)")
        else:
            print(f"\n  ❓ No contradictions found in real data")
            print(f"  Let's examine the complete feedback content:")
            
            if real_data['questions']:
                q1 = real_data['questions'][0]
                print(f"    Question 1 declared answer: {q1.get('correct_answer', 'N/A')}")
                print(f"\n    📄 COMPLETE FEEDBACK CONTENT:")
                print(f"    {'-'*80}")
                feedback = q1.get('feedback_correct', 'N/A')
                print(f"    {feedback}")
                print(f"    {'-'*80}")
                
                # Manual inspection - let's see what values are actually there
                print(f"\n    🔍 MANUAL VALUE SEARCH IN FEEDBACK:")
                print(f"      Looking for obvious values like 0.812, 0.776, etc...")
                
                # Search for specific values manually
                import re
                
                # Look for decimal values
                decimal_pattern = r'\b\d+\.\d+\b'
                all_decimals = re.findall(decimal_pattern, feedback)
                print(f"      All decimal values found: {all_decimals}")
                
                # Look for specific patterns that might contain our target values
                specific_patterns = [
                    r'approx\s*(\d+\.\d+)',
                    r'V_T\s*[≈=]\s*(\d+\.\d+)',

                    r'(\d+\.\d+)\s*text\{V\}',
                    r'(\d+\.\d+),text\{V\}'
                ]
                
                for pattern in specific_patterns:
                    matches = re.findall(pattern, feedback)
                    if matches:
                        print(f"      Pattern '{pattern}' found: {matches}")
                
                # Test value extraction on first question
                if hasattr(detector, '_extract_meaningful_values'):
                    try:
                        values = detector._extract_meaningful_values(feedback)
                        print(f"\n    🔍 ALL VALUES EXTRACTED FROM FEEDBACK:")
                        if values:
                            for i, (value, context) in enumerate(values):
                                print(f"      {i+1}. Value: {value}")
                                print(f"         Context: {context}")
                                print()
                        else:
                            print(f"      No values extracted!")
                        
                        # Check if any extracted values would trigger contradictions
                        declared = float(q1.get('correct_answer', '0'))
                        print(f"    🎯 CONTRADICTION ANALYSIS:")
                        print(f"      Declared answer: {declared}")
                        print(f"      Common intermediates: {detector.common_intermediates}")
                        print(f"      Tolerance threshold: {detector.tolerance_threshold * 100}%")
                        print()
                        
                        for value, context in values:
                            try:
                                val_float = float(value)
                                percentage_diff = abs((val_float - declared) / declared * 100)
                                
                                # Check if it's in common intermediates
                                is_intermediate = val_float in detector.common_intermediates
                                above_threshold = percentage_diff > (detector.tolerance_threshold * 100)
                                
                                print(f"      🔢 Found value: {val_float}")
                                print(f"         Difference from declared: {percentage_diff:.2f}%")
                                print(f"         Above threshold (>{detector.tolerance_threshold*100}%): {above_threshold}")
                                print(f"         Is common intermediate: {is_intermediate}")
                                print(f"         ➡️ Would detect contradiction: {above_threshold and not is_intermediate}")
                                print()
                                
                            except ValueError:
                                print(f"      ❌ Invalid value: '{value}' (not a number)")
                                print()
                        
                        # Test if we manually add a contradictory value
                        print(f"    🧪 SIMULATION - What if feedback contained contradictory value:")
                        test_feedback = feedback + " Therefore, the final answer is V_T = 0.812 V."
                        print(f"      Adding to feedback: 'Therefore, the final answer is V_T = 0.812 V.'")
                        
                        # Reset detector and test
                        detector.contradictions_found = []
                        detector.processing_stats = {'questions_analyzed': 0, 'values_extracted': 0, 'contradictions_found': 0}
                        
                        test_data = {
                            "questions": [{
                                "correct_answer": "0.776",
                                "feedback_correct": test_feedback
                            }]
                        }
                        
                        test_contradictions = detector.detect_contradictions(test_data)
                        print(f"      Result with added value: {len(test_contradictions)} contradictions found")
                        
                        if test_contradictions:
                            c = test_contradictions[0]
                            print(f"      🎯 Contradiction detected: {c.answer} vs {c.values_found} ({c.percentage_difference:.1f}%)")
                        
                    except Exception as e:
                        print(f"    ❌ Error extracting values: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Let's also check all questions
                print(f"\n    🔍 CHECKING ALL QUESTIONS IN FILE:")
                for i, question in enumerate(real_data['questions']):
                    print(f"      Question {i+1}:")
                    print(f"        Declared answer: {question.get('correct_answer', 'N/A')}")
                    feedback_preview = question.get('feedback_correct', 'N/A')
                    if len(feedback_preview) > 100:
                        feedback_preview = feedback_preview[:100] + "..."
                    print(f"        Feedback preview: {feedback_preview}")
                    print()
        
    except FileNotFoundError:
        print(f"  ❌ custom_output.json not found - create it first or use a different file")
    except Exception as e:
        print(f"  ❌ Error testing real data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_detector()