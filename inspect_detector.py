"""
Inspect the mathematical consistency detector to understand its methods
"""

import sys
import os
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

if __name__ == "__main__":
    inspect_detector()