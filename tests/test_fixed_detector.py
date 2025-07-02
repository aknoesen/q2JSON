"""
Quick test of the fixed mathematical consistency detector
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.mathematical_consistency_detector_fixed import MathematicalConsistencyDetectorFixed
import json


def test_fixed_detector():
    """Test the fixed detector against the problematic cases"""
    
    print("🔧 Testing Fixed Mathematical Consistency Detector")
    print("=" * 55)
    
    # Test case 1: Normal calculation progression (should NOT trigger)
    test1 = {
        "questions": [{
            "correct_answer": "0.8116",
            "feedback_correct": "V_T = 0.5 + 0.4(1.673 - 0.894) = 0.5 + 0.3116 = 0.8116 V"
        }]
    }
    
    # Test case 2: Real contradiction (should trigger)
    test2 = {
        "questions": [{
            "correct_answer": "0.776",
            "feedback_correct": "Calculation gives V_T = 0.8116 V. Final answer: V_T = 0.776 V."
        }]
    }
    
    # Test case 3: Normal rounding (should NOT trigger)
    test3 = {
        "questions": [{
            "correct_answer": "0.812",
            "feedback_correct": "V_T = 0.8116 V. Rounding to three decimal places: V_T ≈ 0.812 V."
        }]
    }
    
    detector = MathematicalConsistencyDetectorFixed(tolerance_threshold=0.05)
    
    print("\n🧪 Test 1: Normal calculation progression")
    contradictions1 = detector.detect_contradictions(test1)
    print(f"   Contradictions: {len(contradictions1)} (should be 0)")
    
    print("\n🧪 Test 2: Real contradiction")
    contradictions2 = detector.detect_contradictions(test2)
    print(f"   Contradictions: {len(contradictions2)} (should be > 0)")
    if contradictions2:
        print(f"   Values: {contradictions2[0].values_found}")
        print(f"   Difference: {contradictions2[0].percentage_difference:.1f}%")
    
    print("\n🧪 Test 3: Normal rounding")
    contradictions3 = detector.detect_contradictions(test3)
    print(f"   Contradictions: {len(contradictions3)} (should be 0)")
    
    # Test with real MOSFET file
    print("\n🧪 Test 4: Real MOSFET file")
    try:
        with open("c:/Users/aknoesen/Downloads/MosfetCornerCasePhase2.json", 'r') as f:
            content = f.read()
            content = '\n'.join(line for line in content.split('\n') if not line.strip().startswith('//'))
            mosfet_data = json.loads(content)
        
        contradictions4 = detector.detect_contradictions(mosfet_data)
        print(f"   Contradictions: {len(contradictions4)} (should be < 5)")
        
        print(f"\n📊 Report:")
        print(detector.generate_report())
        
    except FileNotFoundError:
        print("   MOSFET file not found - skipping")
    
    print("\n" + "=" * 55)
    print("🎯 Summary:")
    print(f"   Test 1 (normal calc): {'✅ PASS' if len(contradictions1) == 0 else '❌ FAIL'}")
    print(f"   Test 2 (real contradiction): {'✅ PASS' if len(contradictions2) > 0 else '❌ FAIL'}")  
    print(f"   Test 3 (normal rounding): {'✅ PASS' if len(contradictions3) == 0 else '❌ FAIL'}")


if __name__ == "__main__":
    test_fixed_detector()