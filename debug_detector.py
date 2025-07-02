"""
Debug the mathematical consistency detector to understand why it's not catching contradictions
"""

import sys
import os
import json
import re

sys.path.insert(0, 'modules')
from mathematical_consistency_detector_working import MathematicalConsistencyDetectorWorking

def debug_detector():
    """Debug the detector step by step"""
    
    print("🔍 DEBUGGING MATHEMATICAL CONSISTENCY DETECTOR")
    print("=" * 60)
    
    # Load the file
    with open('custom_output.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create detector and analyze first question in detail
    detector = MathematicalConsistencyDetectorWorking()
    
    # Get the first question for detailed analysis
    q1 = data['questions'][0]
    
    print(f"Question 1 Analysis:")
    print(f"  Declared answer: '{q1.get('correct_answer', 'N/A')}'")
    print(f"  Question type: {q1.get('type', 'N/A')}")
    
    # Test the detector's value extraction on this specific question
    print(f"\n🔍 Testing Detector's Value Extraction:")
    
    # Manually test the _extract_numerical_values method
    feedback = q1.get('feedback_correct', '')
    print(f"  Feedback content length: {len(feedback)} chars")
    
    # Try to call the detector's internal methods
    try:
        # This might not work directly, but let's try
        extracted_values = detector._extract_numerical_values(feedback)
        print(f"  Extracted values: {extracted_values}")
    except Exception as e:
        print(f"  Error calling _extract_numerical_values: {e}")
        
        # Fall back to manual regex extraction
        # Common patterns for numbers
        patterns = [
            r'\b\d+\.\d+\b',  # Basic decimal numbers
            r'V_T\s*=\s*(\d+\.\d+)',  # V_T = value
            r'approx\s*(\d+\.\d+)',  # approx value
            r'=\s*(\d+\.\d+)\s*V',  # = value V
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, feedback)
            print(f"  Pattern {i+1} ({pattern}): {matches}")
    
    # Test on all questions
    print(f"\n🔍 Running Full Detection:")
    contradictions = detector.detect_contradictions(data)
    
    print(f"  Questions processed: {detector.processing_stats.get('questions_analyzed', 0)}")
    print(f"  Total values extracted: {detector.processing_stats.get('values_extracted', 0)}")
    print(f"  Contradictions found: {len(contradictions)}")
    
    # Check detector's internal state
    if hasattr(detector, 'extracted_values'):
        print(f"\n🔍 Detector's Internal Values:")
        for q_idx, values in detector.extracted_values.items():
            print(f"  Question {q_idx + 1}: {values}")
    
    # Check if there are any debug/verbose methods
    if hasattr(detector, 'debug_mode'):
        print(f"\n🔍 Enabling Debug Mode:")
        detector.debug_mode = True
        contradictions = detector.detect_contradictions(data)
    
    # Manual contradiction check for Question 1
    print(f"\n🔍 Manual Contradiction Check (Question 1):")
    declared = q1.get('correct_answer', '')
    
    if declared:
        try:
            declared_float = float(declared)
            
            # Look for final answer values in feedback
            final_values = []
            
            # Look for patterns like "V_T = 0.8116" or "≈ 0.812"
            patterns = [
                r'V_T\s*=\s*(\d+\.\d+)',
                r'approx\s*(\d+\.\d+)',
                r'≈\s*(\d+\.\d+)',
                r'=\s*(\d+\.\d+)\s*V',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, feedback)
                for match in matches:
                    try:
                        value = float(match)
                        if abs(value - declared_float) / declared_float > 0.02:  # > 2% difference
                            final_values.append(value)
                    except:
                        pass
            
            print(f"  Declared: {declared_float}")
            print(f"  Potentially contradictory values: {final_values}")
            
            for value in final_values:
                diff_pct = abs(value - declared_float) / declared_float * 100
                print(f"    {value} vs {declared_float}: {diff_pct:.1f}% difference")
                
        except Exception as e:
            print(f"  Error in manual check: {e}")

if __name__ == "__main__":
    debug_detector()