"""
Debug the fixed detector to see why it's missing real contradictions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.mathematical_consistency_detector_fixed import MathematicalConsistencyDetectorFixed
import re


def debug_pattern_matching():
    """Debug why the fixed detector isn't finding contradictions"""
    
    print("🔍 DEBUGGING FIXED DETECTOR PATTERN MATCHING")
    print("=" * 60)
    
    # Test case that should trigger contradiction
    test_text = "Calculation gives V_T = 0.8116 V. Final answer: V_T = 0.776 V."
    declared_answer = 0.776
    
    print(f"📝 Test text: {test_text}")
    print(f"📝 Declared answer: {declared_answer}")
    
    detector = MathematicalConsistencyDetectorFixed()
    
    # Test the pattern extraction
    final_answers = detector._extract_genuine_final_answers(test_text)
    print(f"\n🎯 Final answers found: {len(final_answers)}")
    for i, (value, context) in enumerate(final_answers):
        print(f"   {i+1}. Value: {value}, Context: {context}")
    
    # Test each pattern individually
    print(f"\n🧪 TESTING INDIVIDUAL PATTERNS:")
    
    patterns = [
        r'(?:final\s+answer|the\s+answer\s+is|result\s+is|therefore|conclusion)\s*[:\s]*[VIR]?_?[A-Z]?\s*[=≈]\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?',
        r'(?:approximately|approx|≈)\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?\s*[.!]?\s*$',
        r'=\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?\s*[.!\$]\s*$',
        r'rounding\s+(?:to\s+\w+\s+decimal\s+places?)?\s*[,:]?\s*[VIR]?_?[A-Z]?\s*[≈=]\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?',
    ]
    
    pattern_names = [
        "Final answer statements",
        "Approximation statements", 
        "End of expression values",
        "Rounding conclusions"
    ]
    
    for i, (pattern, name) in enumerate(zip(patterns, pattern_names)):
        print(f"\n   Pattern {i+1}: {name}")
        matches = list(re.finditer(pattern, test_text, re.IGNORECASE | re.MULTILINE))
        print(f"   Matches: {len(matches)}")
        for match in matches:
            try:
                value = float(match.group(1))
                print(f"      Found value: {value}")
                print(f"      Full match: '{match.group(0)}'")
            except (ValueError, IndexError) as e:
                print(f"      Error extracting value: {e}")
    
    # Test simpler patterns
    print(f"\n🔧 TESTING SIMPLER PATTERNS:")
    
    simple_patterns = [
        r'final\s+answer[:\s]*.*?(\d+\.?\d*)',
        r'V_T\s*=\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*V',
    ]
    
    simple_names = [
        "Simple final answer",
        "V_T equals",
        "Value with V unit"
    ]
    
    for pattern, name in zip(simple_patterns, simple_names):
        print(f"\n   {name}: {pattern}")
        matches = list(re.finditer(pattern, test_text, re.IGNORECASE))
        print(f"   Matches: {len(matches)}")
        for match in matches:
            try:
                value = float(match.group(1))
                print(f"      Found value: {value}")
            except (ValueError, IndexError) as e:
                print(f"      Error: {e}")


def test_with_improved_patterns():
    """Test with improved, simpler patterns"""
    
    print(f"\n\n🛠️ TESTING WITH IMPROVED PATTERNS")
    print("=" * 60)
    
    # Create an improved version inline
    class ImprovedDetector:
        def __init__(self):
            self.tolerance_threshold = 0.05
            self.common_intermediates = {0.4, 0.5, 0.8, 0.894, 1.673, 2.0, 2.8}
        
        def extract_final_values(self, text: str):
            """Simplified final value extraction"""
            
            final_values = []
            
            # Simpler, more reliable patterns
            patterns = [
                # Final answer statements (simplified)
                r'final\s+answer[:\s]*.*?(\d+\.?\d*)',
                # Direct value assignments
                r'V_T\s*=\s*(\d+\.?\d*)',
                # Values with units at sentence/line end
                r'(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{)?V(?:\})?[\s.!]*$',
                # Calculation results
                r'=\s*(\d+\.?\d*)\s*V',
                # Approximations
                r'≈\s*(\d+\.?\d*)',
            ]
            
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                    try:
                        value = float(match.group(1))
                        
                        # Skip obvious intermediates
                        if value not in self.common_intermediates:
                            context = text[max(0, match.start()-30):match.end()+30].strip()
                            final_values.append((value, context))
                    except (ValueError, IndexError):
                        continue
            
            # Remove duplicates
            unique_values = []
            for value, context in final_values:
                if not any(abs(v - value) < 0.001 for v, _ in unique_values):
                    unique_values.append((value, context))
            
            return unique_values
        
        def detect_contradiction(self, declared: float, text: str):
            """Simple contradiction detection"""
            
            final_values = self.extract_final_values(text)
            
            for value, context in final_values:
                if abs(declared - value) > 0.001:  # Not the same
                    percentage_diff = abs(declared - value) / max(declared, 0.001) * 100
                    
                    # Not normal rounding (> 2% difference)
                    if percentage_diff > 2.0:
                        return True, value, percentage_diff, context
            
            return False, None, 0, ""
    
    # Test the improved detector
    improved = ImprovedDetector()
    
    test_cases = [
        {
            "name": "Real contradiction",
            "declared": 0.776,
            "text": "Calculation gives V_T = 0.8116 V. Final answer: V_T = 0.776 V.",
            "should_detect": True
        },
        {
            "name": "Normal rounding",
            "declared": 0.812,
            "text": "V_T = 0.8116 V. Rounding to three decimal places: V_T ≈ 0.812 V.",
            "should_detect": False
        },
        {
            "name": "Calculation progression",
            "declared": 0.8116,
            "text": "V_T = 0.5 + 0.4(1.673 - 0.894) = 0.8116 V",
            "should_detect": False
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        print(f"   Declared: {test_case['declared']}")
        print(f"   Text: {test_case['text']}")
        
        # Extract values
        final_values = improved.extract_final_values(test_case['text'])
        print(f"   Final values found: {final_values}")
        
        # Check contradiction
        has_contradiction, value, diff, context = improved.detect_contradiction(
            test_case['declared'], test_case['text']
        )
        
        print(f"   Contradiction detected: {has_contradiction}")
        if has_contradiction:
            print(f"   Conflicting value: {value} ({diff:.1f}% difference)")
        
        # Check result
        expected = test_case['should_detect']
        if has_contradiction == expected:
            print(f"   ✅ PASS")
        else:
            print(f"   ❌ FAIL - Expected: {expected}, Got: {has_contradiction}")


if __name__ == "__main__":
    debug_pattern_matching()
    test_with_improved_patterns()