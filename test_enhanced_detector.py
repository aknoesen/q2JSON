"""
Test the enhanced mathematical consistency detector
"""

import sys
import os
import json

sys.path.insert(0, 'modules')
from mathematical_consistency_detector_enhanced import MathematicalConsistencyDetectorEnhanced

def test_enhanced_detector():
    """Test the enhanced detector on the MOSFET data"""
    
    print("🚀 TESTING ENHANCED MATHEMATICAL CONSISTENCY DETECTOR")
    print("=" * 65)
    
    # Load the custom output file
    with open('custom_output.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Test with enhanced detector
    enhanced_detector = MathematicalConsistencyDetectorEnhanced()
    
    print(f"Enhanced detector settings:")
    print(f"  Tolerance threshold: {enhanced_detector.tolerance_threshold * 100:.1f}%")
    print(f"  Basic constants: {enhanced_detector.basic_constants}")
    
    # Run detection
    contradictions = enhanced_detector.detect_contradictions(data)
    stats = enhanced_detector.get_summary_stats()
    
    print(f"\n🔍 Enhanced Detection Results:")
    print(f"  Questions analyzed: {stats['questions_analyzed']}")
    print(f"  Values extracted: {stats['values_extracted']}")
    print(f"  Contradictions found: {len(contradictions)}")
    
    if contradictions:
        print(f"\n📋 Contradictions Details:")
        for i, c in enumerate(contradictions, 1):
            print(f"  #{i} - Question {c.question_index + 1}:")
            print(f"      Values: {c.values_found}")
            print(f"      Difference: {c.percentage_difference:.1f}%")
            print(f"      Severity: {c.severity}")
            print(f"      Context: {c.contexts[0][:80]}...")
    
    print(f"\n📊 Detailed Report:")
    print(enhanced_detector.generate_detailed_report())

if __name__ == "__main__":
    test_enhanced_detector()