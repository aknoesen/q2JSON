"""
Test enhanced intermediate filtering that preserves final answers
"""

import sys
import os
import json
import re
sys.path.insert(0, 'modules')
from mathematical_consistency_detector_working import MathematicalConsistencyDetectorWorking

def test_enhanced_filtering():
    """Test enhanced filtering approach"""
    
    print("🔧 TESTING ENHANCED INTERMEDIATE FILTERING")
    print("=" * 55)
    
    # Load the real data
    with open('custom_output.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    detector = MathematicalConsistencyDetectorWorking()
    
    # Enhanced approach: Modify the detector's _is_obvious_intermediate method
    # to be more selective about filtering final answer contexts
    
    print("🔍 Analysis of Question 1 Feedback:")
    q1 = data['questions'][0]
    feedback = q1['feedback_correct']
    
    # Look for final answer patterns specifically
    final_patterns = [
        r'Final answer:\s*V_T\s*=\s*(\d+\.\d+)',
        r'V_T\s*≈\s*(\d+\.\d+)',
        r'V_T\s*approx\s*(\d+\.\d+)',
        r'V_T\s*=\s*(\d+\.\d+)\s*V',
        r'≈\s*(\d+\.\d+)\s*V',
        r'approx\s*(\d+\.\d+)\s*V'
    ]
    
    print("Final answer patterns found:")
    final_values = []
    for pattern in final_patterns:
        matches = re.findall(pattern, feedback, re.IGNORECASE)
        if matches:
            print(f"  Pattern '{pattern}': {matches}")
            final_values.extend([float(m) for m in matches])
    
    # Also look for calculation result patterns
    calc_patterns = [
        r'=\s*(\d+\.\d+)\s*V\.',
        r'gives\s*V_T\s*=\s*(\d+\.\d+)',
        r'calculation.*?(\d+\.\d+)\s*V'
    ]
    
    print("\nCalculation result patterns found:")
    calc_values = []
    for pattern in calc_patterns:
        matches = re.findall(pattern, feedback, re.IGNORECASE)
        if matches:
            print(f"  Pattern '{pattern}': {matches}")
            calc_values.extend([float(m) for m in matches])
    
    declared = float(q1['correct_answer'])
    print(f"\nDeclared answer: {declared}")
    print(f"Final answer values found: {final_values}")
    print(f"Calculation values found: {calc_values}")
    
    # Check contradictions
    all_found_values = final_values + calc_values
    contradictions = []
    
    for value in all_found_values:
        if abs(value - declared) / declared > 0.02:  # > 2%
            diff_pct = abs(value - declared) / declared * 100
            contradictions.append((value, diff_pct))
    
    print(f"\nManual contradiction detection:")
    for value, diff_pct in contradictions:
        print(f"  {declared} vs {value}: {diff_pct:.1f}% difference")
    
    # Test with a more targeted intermediate set
    print(f"\n🧪 Test with Enhanced Intermediate Set:")
    
    # Keep only the most basic constants, remove calculation-specific values
    enhanced_intermediates = {0.5, 0.4, 2.0}  # Remove 2.8, 0.8, 0.894, 1.673
    
    detector.common_intermediates = enhanced_intermediates
    detector.contradictions_found = []
    detector.processing_stats = {'questions_analyzed': 0, 'values_extracted': 0, 'contradictions_found': 0}
    
    contradictions_enhanced = detector.detect_contradictions(data)
    print(f"  Contradictions found: {len(contradictions_enhanced)}")
    print(f"  Values extracted: {detector.processing_stats['values_extracted']}")
    
    if contradictions_enhanced:
        for c in contradictions_enhanced:
            print(f"    Question {c.question_index + 1}: {c.values_found}")
            print(f"    Difference: {c.percentage_difference:.1f}%")
            print(f"    Severity: {c.severity}")
            print(f"    Context: {c.contexts[0][:100]}...")

if __name__ == "__main__":
    test_enhanced_filtering()