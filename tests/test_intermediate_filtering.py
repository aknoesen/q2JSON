"""
Test if the intermediate value filtering is causing the issue
"""

import sys
import os
import json
sys.path.insert(0, 'modules')
from mathematical_consistency_detector_working import MathematicalConsistencyDetectorWorking

def test_intermediate_filtering():
    """Test if intermediate filtering is the problem"""
    
    print("🔍 TESTING INTERMEDIATE VALUE FILTERING")
    print("=" * 50)
    
    # Load the real data
    with open('custom_output.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    detector = MathematicalConsistencyDetectorWorking()
    
    # Get the first question
    q1 = data['questions'][0]
    
    print(f"Original common_intermediates: {detector.common_intermediates}")
    print(f"Tolerance threshold: {detector.tolerance_threshold}")
    
    # Test 1: Run detection normally
    print(f"\n🧪 Test 1: Normal Detection")
    contradictions1 = detector.detect_contradictions(data)
    print(f"  Contradictions found: {len(contradictions1)}")
    
    # Test 2: Temporarily clear the common_intermediates
    print(f"\n🧪 Test 2: With Empty common_intermediates")
    original_intermediates = detector.common_intermediates.copy()
    detector.common_intermediates = set()  # Clear the filtering
    
    # Reset detector state
    detector.contradictions_found = []
    detector.processing_stats = {'questions_analyzed': 0, 'values_extracted': 0, 'contradictions_found': 0}
    
    contradictions2 = detector.detect_contradictions(data)
    print(f"  Contradictions found: {len(contradictions2)}")
    print(f"  Values extracted: {detector.processing_stats['values_extracted']}")
    
    if contradictions2:
        for c in contradictions2:
            print(f"    Question {c.question_index + 1}: {c.values_found} ({c.percentage_difference:.1f}%)")
    
    # Test 3: Reduce the tolerance threshold
    print(f"\n🧪 Test 3: With Lower Tolerance (2%)")
    detector.common_intermediates = original_intermediates  # Restore
    detector.tolerance_threshold = 0.02  # Lower from 0.05 to 0.02
    
    # Reset detector state
    detector.contradictions_found = []
    detector.processing_stats = {'questions_analyzed': 0, 'values_extracted': 0, 'contradictions_found': 0}
    
    contradictions3 = detector.detect_contradictions(data)
    print(f"  Contradictions found: {len(contradictions3)}")
    
    if contradictions3:
        for c in contradictions3:
            print(f"    Question {c.question_index + 1}: {c.values_found} ({c.percentage_difference:.1f}%)")
    
    # Test 4: Custom intermediate set (remove some values)
    print(f"\n🧪 Test 4: Custom Intermediate Set")
    detector.tolerance_threshold = 0.05  # Restore original
    detector.common_intermediates = {0.5, 0.4, 2.0}  # Keep only some
    
    # Reset detector state
    detector.contradictions_found = []
    detector.processing_stats = {'questions_analyzed': 0, 'values_extracted': 0, 'contradictions_found': 0}
    
    contradictions4 = detector.detect_contradictions(data)
    print(f"  Contradictions found: {len(contradictions4)}")
    print(f"  Values extracted: {detector.processing_stats['values_extracted']}")
    
    if contradictions4:
        for c in contradictions4:
            print(f"    Question {c.question_index + 1}: {c.values_found} ({c.percentage_difference:.1f}%)")
    
    print(f"\n🎯 CONCLUSION:")
    print(f"  Normal detection: {len(contradictions1)} contradictions")
    print(f"  No intermediate filtering: {len(contradictions2)} contradictions")
    print(f"  Lower tolerance: {len(contradictions3)} contradictions")
    print(f"  Custom intermediates: {len(contradictions4)} contradictions")

if __name__ == "__main__":
    test_intermediate_filtering()