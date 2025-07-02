"""
Quick test runner for Mathematical Consistency Detector - REFINED VERSION
Tests the specific 0.8116V vs 0.812V vs 0.776V contradiction
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.mathematical_consistency_detector import MathematicalConsistencyDetector


def quick_test():
    """Quick test with the specific contradiction from MosfetCornerCasePhase2.json"""
    
    print("🔍 Testing Mathematical Consistency Detector (REFINED)")
    print("=" * 55)
    
    # Create test data with the specific contradiction - SIMPLIFIED
    test_data = {
        "questions": [
            {
                "type": "numerical",
                "correct_answer": "0.776",
                "feedback_correct": "Correct! The calculation gives V_T = 0.8116 V. Rounding to three decimal places, V_T ≈ 0.812 V. Final answer: V_T ≈ 0.776 V."
            }
        ]
    }
    
    print("📝 Test Case:")
    print("   Declared Answer: 0.776")
    print("   Feedback contains: 0.8116 V, 0.812 V, 0.776 V")
    print("   Expected: Should detect 0.8116 vs 0.776 (4.8% difference)")
    print("   Expected: Should detect 0.812 vs 0.776 (4.6% difference)")
    print("")
    
    # Initialize detector with 4% threshold to catch these differences
    detector = MathematicalConsistencyDetector(tolerance_threshold=0.04)  # 4% threshold
    
    # Detect contradictions
    contradictions = detector.detect_contradictions(test_data)
    
    print(f"🔍 Results: {len(contradictions)} contradictions found")
    
    if contradictions:
        print("\n📊 Contradiction Details:")
        for i, contradiction in enumerate(contradictions, 1):
            print(f"\nContradiction #{i}:")
            print(f"  Type: {contradiction.field_name}")
            print(f"  Values: {contradiction.values_found}")
            print(f"  Difference: {contradiction.percentage_difference:.1f}%")
            print(f"  Severity: {contradiction.severity}")
            
            # Check if we found the expected contradictions
            if any(abs(v - 0.8116) < 0.01 for v in contradiction.values_found):
                print(f"  ✅ Found expected 0.8116 V contradiction!")
            elif any(abs(v - 0.812) < 0.01 for v in contradiction.values_found):
                print(f"  ✅ Found expected 0.812 V contradiction!")
        
        print(f"\n📋 Summary Report:")
        print(detector.generate_report())
        
        # Check if we found meaningful contradictions
        meaningful_contradictions = [c for c in contradictions if c.percentage_difference < 50]
        
        if meaningful_contradictions:
            print("✅ Test PASSED - Found meaningful mathematical contradictions!")
        else:
            print("⚠️ Test PARTIAL - Found contradictions but they may be false positives")
    else:
        print("❌ Test FAILED - No contradictions detected")
        print("The detector may need further refinement")
    
    return len(contradictions) > 0


def test_with_real_file():
    """Test with the actual MosfetCornerCasePhase2.json file if available"""
    
    print("\n" + "=" * 55)
    print("🔍 Testing with Real MosfetCornerCasePhase2.json")
    print("=" * 55)
    
    # Try to load the actual file
    import json
    
    test_file_paths = [
        "c:/Users/aknoesen/Downloads/MosfetCornerCasePhase2.json",
        "../MosfetCornerCasePhase2.json",
        "MosfetCornerCasePhase2.json"
    ]
    
    test_data = None
    for file_path in test_file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove comments for JSON parsing
                content = '\n'.join(line for line in content.split('\n') 
                                 if not line.strip().startswith('//'))
                test_data = json.loads(content)
                print(f"✅ Loaded: {file_path}")
                break
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            continue
    
    if not test_data:
        print("❌ Could not find MosfetCornerCasePhase2.json file")
        return False
    
    print(f"📊 Found {len(test_data.get('questions', []))} questions")
    
    # Initialize detector
    detector = MathematicalConsistencyDetector(tolerance_threshold=0.04)  # 4% threshold
    
    # Detect contradictions
    contradictions = detector.detect_contradictions(test_data)
    
    print(f"🔍 Results: {len(contradictions)} contradictions found")
    
    if contradictions:
        # Focus on reasonable contradictions (< 100% difference)
        reasonable_contradictions = [c for c in contradictions if c.percentage_difference < 100]
        
        print(f"\n📊 Reasonable Contradictions: {len(reasonable_contradictions)}")
        
        for i, contradiction in enumerate(reasonable_contradictions, 1):
            print(f"\nContradiction #{i}:")
            print(f"  Question: {contradiction.question_index + 1}")
            print(f"  Type: {contradiction.field_name}")
            print(f"  Values: {contradiction.values_found}")
            print(f"  Difference: {contradiction.percentage_difference:.1f}%")
            print(f"  Severity: {contradiction.severity}")
        
        if reasonable_contradictions:
            print("✅ Found meaningful contradictions in real data!")
            return True
    
    print("✅ Analysis complete - see results above")
    return len(contradictions) > 0


if __name__ == "__main__":
    print("Mathematical Consistency Detector - Refined Test")
    print("=" * 55)
    
    # Run both tests
    test1_result = quick_test()
    test2_result = test_with_real_file()
    
    print("\n" + "="*55)
    print("=== FINAL RESULTS ===")
    print(f"Quick test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Real file test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result or test2_result:
        print("\n🎉 Mathematical contradiction detection is working!")
    else:
        print("\n🔧 Detector may need further refinement")