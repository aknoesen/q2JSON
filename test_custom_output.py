"""
Test mathematical detection on the custom output file
"""

import sys
import os
import json

sys.path.insert(0, 'modules')
from mathematical_consistency_detector_working import MathematicalConsistencyDetectorWorking

def test_custom_output():
    """Test mathematical detection on custom_output.json"""
    
    print("Testing Mathematical Detection on custom_output.json")
    print("=" * 55)
    
    # Load the file
    try:
        with open('custom_output.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded file: custom_output.json")
        print(f"Questions found: {len(data.get('questions', []))}")
        
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    # Run detection
    detector = MathematicalConsistencyDetectorWorking()
    contradictions = detector.detect_contradictions(data)
    
    print(f"\nDetection Results:")
    print(f"Questions analyzed: {detector.processing_stats['questions_analyzed']}")
    print(f"Values extracted: {detector.processing_stats['values_extracted']}")
    print(f"Contradictions found: {len(contradictions)}")
    
    if contradictions:
        print(f"\nContradictions Details:")
        for i, c in enumerate(contradictions, 1):
            print(f"  #{i} - Question {c.question_index + 1}:")
            print(f"      Values: {c.values_found}")
            print(f"      Difference: {c.percentage_difference:.1f}%")
            print(f"      Severity: {c.severity}")
            print(f"      Context: {c.contexts[0][:100]}...")
    else:
        print(f"\nNo contradictions detected.")
        
        # Let's examine the first question manually
        if data.get('questions'):
            q1 = data['questions'][0]
            print(f"\nFirst Question Analysis:")
            print(f"  Declared answer: {q1.get('correct_answer', 'N/A')}")
            
            feedback = q1.get('feedback_correct', '')
            print(f"  Feedback length: {len(feedback)} characters")
            
            # Look for numerical values in feedback
            import re
            numbers = re.findall(r'\b\d+\.\d+\b', feedback)
            print(f"  Numbers found in feedback: {numbers}")
    
    print(f"\nDetailed Report:")
    print(detector.generate_detailed_report())

if __name__ == "__main__":
    test_custom_output()